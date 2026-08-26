#include "m6_carrier_capture_core.h"
#include "m6_carrier_spi_slave_transport.h"

#include <array>
#include <cstdint>

#include "driver/gpio.h"
#include "driver/spi_slave.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace {

constexpr char kTag[] = "m6-carrier-s3-ref";

// Reference-only mapping for a second ESP32-S3 carrier board. It is not the
// SmartPaddle host mapping and must not be copied into the host firmware.
constexpr std::array<gpio_num_t, 10> kInputPins = {
    GPIO_NUM_4,  GPIO_NUM_5,  GPIO_NUM_6,  GPIO_NUM_7,  GPIO_NUM_8,
    GPIO_NUM_9,  GPIO_NUM_10, GPIO_NUM_11, GPIO_NUM_12, GPIO_NUM_13,
};
constexpr gpio_num_t kSpiSck = GPIO_NUM_15;
constexpr gpio_num_t kSpiMosi = GPIO_NUM_16;
constexpr gpio_num_t kSpiMiso = GPIO_NUM_17;
constexpr gpio_num_t kSpiCs = GPIO_NUM_18;
constexpr gpio_num_t kIrq = GPIO_NUM_14;
constexpr gpio_num_t kReset = GPIO_NUM_21;

struct InputRoute {
    gpio_num_t pin;
    std::uint8_t channel;
};

smartgear::carrier::M6CarrierCaptureCore g_capture;
smartgear::carrier::M6CarrierSpiSlaveTransport g_transport(g_capture);
std::array<InputRoute, kInputPins.size()> g_routes{};

void IRAM_ATTR carrier_input_isr(void* argument) {
    const auto* route = static_cast<const InputRoute*>(argument);
    if (route == nullptr) {
        return;
    }
    const auto timestamp_us = static_cast<std::uint64_t>(esp_timer_get_time());
    const auto level = static_cast<std::uint8_t>(gpio_get_level(route->pin));
    // The platform-neutral core contains no allocation, logging or filtering;
    // the ISR records the raw edge and lets the SPI task package it later.
    (void)g_capture.on_edge(route->channel, level, timestamp_us);
}

void configure_inputs() {
    gpio_config_t input_config{};
    input_config.pin_bit_mask = 0;
    for (const gpio_num_t pin : kInputPins) {
        input_config.pin_bit_mask |= UINT64_C(1) << static_cast<unsigned>(pin);
    }
    input_config.mode = GPIO_MODE_INPUT;
    input_config.pull_up_en = GPIO_PULLUP_DISABLE;
    input_config.pull_down_en = GPIO_PULLDOWN_DISABLE;
    input_config.intr_type = GPIO_INTR_ANYEDGE;
    ESP_ERROR_CHECK(gpio_config(&input_config));

    for (std::size_t index = 0; index < kInputPins.size(); ++index) {
        g_routes[index] = {
            kInputPins[index], static_cast<std::uint8_t>(index)};
        ESP_ERROR_CHECK(gpio_isr_handler_add(
            kInputPins[index], carrier_input_isr, &g_routes[index]));
    }
}

void configure_control_pins() {
    gpio_config_t irq_config{};
    irq_config.pin_bit_mask = UINT64_C(1) << static_cast<unsigned>(kIrq);
    irq_config.mode = GPIO_MODE_OUTPUT;
    irq_config.pull_up_en = GPIO_PULLUP_DISABLE;
    irq_config.pull_down_en = GPIO_PULLDOWN_DISABLE;
    irq_config.intr_type = GPIO_INTR_DISABLE;
    ESP_ERROR_CHECK(gpio_config(&irq_config));
    ESP_ERROR_CHECK(gpio_set_level(kIrq, 1));

    gpio_config_t reset_config{};
    reset_config.pin_bit_mask = UINT64_C(1) << static_cast<unsigned>(kReset);
    reset_config.mode = GPIO_MODE_INPUT;
    reset_config.pull_up_en = GPIO_PULLUP_ENABLE;
    reset_config.pull_down_en = GPIO_PULLDOWN_DISABLE;
    reset_config.intr_type = GPIO_INTR_DISABLE;
    ESP_ERROR_CHECK(gpio_config(&reset_config));
}

void configure_spi_slave() {
    spi_bus_config_t bus_config{};
    bus_config.mosi_io_num = kSpiMosi;
    bus_config.miso_io_num = kSpiMiso;
    bus_config.sclk_io_num = kSpiSck;
    bus_config.quadwp_io_num = -1;
    bus_config.quadhd_io_num = -1;
    bus_config.max_transfer_sz =
        static_cast<int>(smartgear::kM6CarrierMaxFrameBytes);

    spi_slave_interface_config_t slave_config{};
    slave_config.mode = 0;
    slave_config.spics_io_num = kSpiCs;
    slave_config.queue_size = 1;

    ESP_ERROR_CHECK(spi_slave_initialize(
        SPI2_HOST, &bus_config, &slave_config, SPI_DMA_CH_AUTO));
}

void spi_service_loop() {
    std::array<std::uint8_t, smartgear::kM6CarrierMaxFrameBytes> rx_buffer{};

    while (true) {
        if (gpio_get_level(kReset) == 0) {
            g_transport.reset();
            ESP_ERROR_CHECK(gpio_set_level(kIrq, 1));
            vTaskDelay(pdMS_TO_TICKS(2));
            continue;
        }

        if (!g_transport.frame_ready() &&
            !g_transport.clock_sync_response_pending()) {
            (void)g_transport.service();
        }
        ESP_ERROR_CHECK(gpio_set_level(kIrq,
                                       g_transport.irq_asserted() ? 0 : 1));

        if (g_transport.transaction_active()) {
            vTaskDelay(pdMS_TO_TICKS(1));
            continue;
        }

        // An event response is started only after IRQ is asserted. When no
        // event is pending, the same fixed-size peripheral transaction waits
        // for a host clock-sync request. A valid request makes the transport
        // assert IRQ for the following response transaction.
        bool started = false;
        if (g_transport.frame_ready()) {
            started = g_transport.begin_transaction();
        } else if (g_transport.clock_sync_response_pending()) {
            started = g_transport.begin_clock_sync_response(
                static_cast<std::uint64_t>(esp_timer_get_time()));
        } else {
            started = g_transport.begin_clock_sync_request();
        }
        if (!started) {
            g_capture.mark_transport_fault();
            vTaskDelay(pdMS_TO_TICKS(1));
            continue;
        }
        const bool clock_sync_request =
            g_transport.clock_sync_request_active();
        rx_buffer.fill(0U);
        spi_slave_transaction_t transaction{};
        transaction.length =
            smartgear::kM6CarrierMaxFrameBytes * sizeof(std::uint8_t) * 8U;
        transaction.tx_buffer = g_transport.tx_buffer();
        transaction.rx_buffer = rx_buffer.data();
        const esp_err_t result =
            spi_slave_transmit(SPI2_HOST, &transaction, portMAX_DELAY);
        const std::size_t transferred_bytes =
            result == ESP_OK ? transaction.trans_len / 8U : 0U;
        if (clock_sync_request) {
            (void)g_transport.end_clock_sync_request(
                transferred_bytes, rx_buffer.data(), rx_buffer.size(),
                static_cast<std::uint64_t>(esp_timer_get_time()));
        } else {
            (void)g_transport.end_transaction(transferred_bytes);
        }
        ESP_ERROR_CHECK(gpio_set_level(kIrq,
                                       g_transport.irq_asserted() ? 0 : 1));
        if (result != ESP_OK) {
            ESP_LOGW(kTag, "SPI slave transaction failed: %s",
                     esp_err_to_name(result));
        }
    }
}

}  // namespace

extern "C" void app_main() {
    ESP_ERROR_CHECK(gpio_install_isr_service(ESP_INTR_FLAG_IRAM));
    configure_control_pins();
    configure_inputs();
    configure_spi_slave();
    ESP_LOGI(kTag,
             "reference carrier ready: inputs=10 SPI2 SCK=%d MOSI=%d MISO=%d CS=%d IRQ=%d RESET=%d",
             static_cast<int>(kSpiSck), static_cast<int>(kSpiMosi),
             static_cast<int>(kSpiMiso), static_cast<int>(kSpiCs),
             static_cast<int>(kIrq), static_cast<int>(kReset));
    spi_service_loop();
}
