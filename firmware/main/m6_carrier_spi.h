#pragma once

#include <array>
#include <cstdint>

#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_err.h"
#include "m6_carrier_protocol.h"

namespace smartgear {

struct M6CarrierSpiConfig {
    spi_host_device_t host = SPI2_HOST;
    gpio_num_t sck = static_cast<gpio_num_t>(-1);
    gpio_num_t mosi = static_cast<gpio_num_t>(-1);
    gpio_num_t miso = static_cast<gpio_num_t>(-1);
    gpio_num_t cs = static_cast<gpio_num_t>(-1);
    gpio_num_t irq = static_cast<gpio_num_t>(-1);
    gpio_num_t reset = static_cast<gpio_num_t>(-1);
    int clock_hz = 1'000'000;
};

enum class M6CarrierSpiPollResult : std::uint8_t {
    kNoData,
    kFrame,
    kBoundaryError,
    kSpiError,
};

// ESP32-side master for the timestamp-owning M6 capture carrier. The carrier
// asserts IRQ low when a complete event or clock-sync response is ready; one
// fixed-size SPI transaction then reads the largest legal frame and the
// protocol decoder validates the actual length and CRC.
class M6CarrierSpiMaster {
  public:
    explicit M6CarrierSpiMaster(M6CarrierSpiConfig config);
    ~M6CarrierSpiMaster();

    M6CarrierSpiMaster(const M6CarrierSpiMaster&) = delete;
    M6CarrierSpiMaster& operator=(const M6CarrierSpiMaster&) = delete;

    esp_err_t init();
    bool initialized() const { return initialized_; }
    M6CarrierSpiPollResult poll(M6CarrierFrame* frame);

    // Performs the two-transaction NTP-style clock exchange. The first
    // transaction sends a sync request; the carrier returns t2/t3 in a
    // response transaction after asserting IRQ_N. No event frame is consumed
    // by this method.
    esp_err_t exchange_clock_sync(M6CarrierClockSyncSample* sample);

    std::uint32_t spi_error_count() const { return spi_error_count_; }
    std::uint32_t malformed_frame_count() const {
        return malformed_frame_count_;
    }

  private:
    static void IRAM_ATTR irq_handler(void* argument);
    void mark_irq_from_isr();
    bool irq_asserted() const;
    bool wait_for_irq(std::uint64_t timeout_us) const;
    void release_resources();

    M6CarrierSpiConfig config_;
    spi_device_handle_t device_ = nullptr;
    bool bus_initialized_ = false;
    bool irq_handler_installed_ = false;
    bool initialized_ = false;
    volatile bool irq_pending_ = false;
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> tx_buffer_{};
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> rx_buffer_{};
    std::uint32_t spi_error_count_ = 0;
    std::uint32_t malformed_frame_count_ = 0;
};

}  // namespace smartgear
