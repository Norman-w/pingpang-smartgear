#include "m6_carrier_spi.h"

#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace smartgear {
namespace {

constexpr char kTag[] = "m6-carrier-spi";

bool valid_gpio(const gpio_num_t pin) {
    const int value = static_cast<int>(pin);
    return value >= 0 && value <= 48;
}

std::size_t read_u16_le(const std::uint8_t* bytes) {
    return static_cast<std::size_t>(bytes[0]) |
           (static_cast<std::size_t>(bytes[1]) << 8U);
}

}  // namespace

M6CarrierSpiMaster::M6CarrierSpiMaster(M6CarrierSpiConfig config)
    : config_(config) {}

M6CarrierSpiMaster::~M6CarrierSpiMaster() {
    release_resources();
}

esp_err_t M6CarrierSpiMaster::init() {
    if (initialized_) {
        return ESP_OK;
    }
    if (!valid_gpio(config_.sck) || !valid_gpio(config_.mosi) ||
        !valid_gpio(config_.miso) || !valid_gpio(config_.cs) ||
        !valid_gpio(config_.irq) || !valid_gpio(config_.reset) ||
        config_.clock_hz <= 0) {
        return ESP_ERR_INVALID_ARG;
    }

    const gpio_config_t irq_config{
        .pin_bit_mask = UINT64_C(1) << static_cast<unsigned>(config_.irq),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_NEGEDGE,
    };
    esp_err_t error = gpio_config(&irq_config);
    if (error != ESP_OK) {
        return error;
    }
    error = gpio_set_intr_type(config_.irq, GPIO_INTR_NEGEDGE);
    if (error != ESP_OK) {
        return error;
    }

    const gpio_config_t reset_config{
        .pin_bit_mask = UINT64_C(1) << static_cast<unsigned>(config_.reset),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    error = gpio_config(&reset_config);
    if (error != ESP_OK) {
        return error;
    }
    error = gpio_set_level(config_.reset, 0);
    if (error != ESP_OK) {
        return error;
    }
    vTaskDelay(pdMS_TO_TICKS(10));
    error = gpio_set_level(config_.reset, 1);
    if (error != ESP_OK) {
        return error;
    }

    spi_bus_config_t bus_config{};
    bus_config.sclk_io_num = config_.sck;
    bus_config.mosi_io_num = config_.mosi;
    bus_config.miso_io_num = config_.miso;
    bus_config.quadwp_io_num = -1;
    bus_config.quadhd_io_num = -1;
    bus_config.max_transfer_sz = static_cast<int>(kM6CarrierMaxFrameBytes);
    error = spi_bus_initialize(config_.host, &bus_config, SPI_DMA_DISABLED);
    if (error != ESP_OK) {
        return error;
    }
    bus_initialized_ = true;

    spi_device_interface_config_t device_config{};
    device_config.clock_speed_hz = config_.clock_hz;
    device_config.mode = 0;
    device_config.spics_io_num = config_.cs;
    device_config.queue_size = 1;
    error = spi_bus_add_device(config_.host, &device_config, &device_);
    if (error != ESP_OK) {
        release_resources();
        return error;
    }

    // The normal firmware path installs the ISR service for the GPIO edge
    // queue before this driver is initialized. The carrier driver therefore
    // shares that service and only owns its individual IRQ handler.
    error = gpio_isr_handler_add(config_.irq, irq_handler, this);
    if (error != ESP_OK) {
        release_resources();
        return error;
    }
    irq_handler_installed_ = true;
    irq_pending_ = irq_asserted();
    initialized_ = true;
    ESP_LOGI(kTag, "SPI master ready: host=%d clock=%dHz IRQ=GPIO%d",
             static_cast<int>(config_.host), config_.clock_hz,
             static_cast<int>(config_.irq));
    return ESP_OK;
}

M6CarrierSpiPollResult M6CarrierSpiMaster::poll(M6CarrierFrame* frame) {
    if (!initialized_ || frame == nullptr) {
        return M6CarrierSpiPollResult::kSpiError;
    }
    if (!irq_pending_ && !irq_asserted()) {
        return M6CarrierSpiPollResult::kNoData;
    }
    irq_pending_ = false;

    tx_buffer_.fill(0);
    rx_buffer_.fill(0);
    spi_transaction_t transaction{};
    transaction.length = kM6CarrierMaxFrameBytes * 8U;
    transaction.tx_buffer = tx_buffer_.data();
    transaction.rx_buffer = rx_buffer_.data();
    const esp_err_t error = spi_device_transmit(device_, &transaction);
    if (error != ESP_OK) {
        ++spi_error_count_;
        return M6CarrierSpiPollResult::kSpiError;
    }

    if (rx_buffer_[0] != kM6CarrierMagic0 ||
        rx_buffer_[1] != kM6CarrierMagic1) {
        ++malformed_frame_count_;
        return M6CarrierSpiPollResult::kBoundaryError;
    }
    const std::size_t payload_size = read_u16_le(rx_buffer_.data() + 4);
    const std::size_t frame_size = kM6CarrierHeaderBytes + payload_size +
                                   kM6CarrierFooterBytes;
    if (payload_size > kM6CarrierMaxPayloadBytes ||
        frame_size > kM6CarrierMaxFrameBytes ||
        frame_size < kM6CarrierHeaderBytes + kM6CarrierFooterBytes) {
        ++malformed_frame_count_;
        return M6CarrierSpiPollResult::kBoundaryError;
    }

    const M6CarrierDecodeStatus status =
        m6_carrier_decode_edges(rx_buffer_.data(), frame_size, frame);
    if (status != M6CarrierDecodeStatus::kOk) {
        ++malformed_frame_count_;
        return M6CarrierSpiPollResult::kBoundaryError;
    }
    return M6CarrierSpiPollResult::kFrame;
}

esp_err_t M6CarrierSpiMaster::exchange_clock_sync(
    M6CarrierClockSyncSample* sample) {
    if (!initialized_ || sample == nullptr) {
        return ESP_ERR_INVALID_ARG;
    }
    if (irq_asserted()) {
        // An event or a previous sync response owns the next transaction.
        // Do not clock it as a request and consume the wrong frame type.
        return ESP_ERR_INVALID_STATE;
    }

    irq_pending_ = false;
    tx_buffer_.fill(0U);
    rx_buffer_.fill(0U);
    if (m6_carrier_encode_clock_sync_request(tx_buffer_.data(),
                                             tx_buffer_.size()) == 0U) {
        return ESP_ERR_INVALID_ARG;
    }

    M6CarrierClockSyncSample exchange{};
    exchange.host_sent_us =
        static_cast<std::uint64_t>(esp_timer_get_time());
    spi_transaction_t request_transaction{};
    request_transaction.length = kM6CarrierMaxFrameBytes * 8U;
    request_transaction.tx_buffer = tx_buffer_.data();
    request_transaction.rx_buffer = rx_buffer_.data();
    esp_err_t error =
        spi_device_transmit(device_, &request_transaction);
    if (error != ESP_OK) {
        ++spi_error_count_;
        return error;
    }

    // The carrier has parsed the first transaction and asserts IRQ_N only
    // after its response is ready. This keeps the response frame separate
    // from the event-frame IRQ contract.
    if (!wait_for_irq(50'000U)) {
        ++spi_error_count_;
        return ESP_ERR_TIMEOUT;
    }

    irq_pending_ = false;
    tx_buffer_.fill(0U);
    rx_buffer_.fill(0U);
    spi_transaction_t response_transaction{};
    response_transaction.length = kM6CarrierMaxFrameBytes * 8U;
    response_transaction.tx_buffer = tx_buffer_.data();
    response_transaction.rx_buffer = rx_buffer_.data();
    error = spi_device_transmit(device_, &response_transaction);
    exchange.host_received_us =
        static_cast<std::uint64_t>(esp_timer_get_time());
    if (error != ESP_OK) {
        ++spi_error_count_;
        return error;
    }

    if (rx_buffer_[0] != kM6CarrierMagic0 ||
        rx_buffer_[1] != kM6CarrierMagic1) {
        ++malformed_frame_count_;
        return ESP_FAIL;
    }
    const std::size_t payload_size = read_u16_le(rx_buffer_.data() + 4);
    const std::size_t frame_size = kM6CarrierHeaderBytes + payload_size +
                                   kM6CarrierFooterBytes;
    if (payload_size != kM6CarrierClockSyncResponsePayloadBytes ||
        frame_size != kM6CarrierClockSyncResponseBytes) {
        ++malformed_frame_count_;
        return ESP_FAIL;
    }

    M6CarrierClockSyncResponse response{};
    if (!m6_carrier_decode_clock_sync_response(rx_buffer_.data(), frame_size,
                                               &response) ||
        !response.valid) {
        ++malformed_frame_count_;
        return ESP_FAIL;
    }
    exchange.carrier_received_us = response.carrier_received_us;
    exchange.carrier_sent_us = response.carrier_sent_us;
    *sample = exchange;
    return ESP_OK;
}

void IRAM_ATTR M6CarrierSpiMaster::irq_handler(void* argument) {
    auto* self = static_cast<M6CarrierSpiMaster*>(argument);
    if (self != nullptr) {
        self->mark_irq_from_isr();
    }
}

void M6CarrierSpiMaster::mark_irq_from_isr() {
    irq_pending_ = true;
}

bool M6CarrierSpiMaster::irq_asserted() const {
    return gpio_get_level(config_.irq) == 0;
}

bool M6CarrierSpiMaster::wait_for_irq(const std::uint64_t timeout_us) const {
    const std::uint64_t start_us =
        static_cast<std::uint64_t>(esp_timer_get_time());
    while (!irq_asserted()) {
        const std::uint64_t now_us =
            static_cast<std::uint64_t>(esp_timer_get_time());
        if (now_us - start_us >= timeout_us) {
            return false;
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
    return true;
}

void M6CarrierSpiMaster::release_resources() {
    initialized_ = false;
    if (irq_handler_installed_) {
        gpio_isr_handler_remove(config_.irq);
        irq_handler_installed_ = false;
    }
    if (device_ != nullptr) {
        spi_bus_remove_device(device_);
        device_ = nullptr;
    }
    if (bus_initialized_) {
        spi_bus_free(config_.host);
        bus_initialized_ = false;
    }
    irq_pending_ = false;
}

}  // namespace smartgear
