#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include "m6_carrier_capture_core.h"
#include "m6_carrier_spi_slave_transport.h"

namespace smartgear::carrier::stm32g031 {

// This file is deliberately independent of STM32Cube headers. It is the
// narrow port contract that the real STM32G0 HAL/LL or register layer must
// implement; it is not a flashable STM32 project.
enum class GpioPort : std::uint8_t { kA, kB, kF };

struct PinDescriptor {
    GpioPort port;
    std::uint8_t number;
    std::uint8_t package_pin;
    std::uint8_t exti_line;
};

constexpr std::uint8_t kNoExti = 0xffU;

constexpr std::array<PinDescriptor, 10> kCarrierInputPins = {{
    {GpioPort::kA, 1, 8, 1},
    {GpioPort::kA, 2, 9, 2},
    {GpioPort::kA, 3, 10, 3},
    {GpioPort::kA, 4, 11, 4},
    {GpioPort::kA, 5, 12, 5},
    {GpioPort::kA, 6, 13, 6},
    {GpioPort::kA, 7, 14, 7},
    {GpioPort::kA, 9, 19, 9},
    {GpioPort::kA, 10, 21, 10},
    {GpioPort::kA, 15, 26, 15},
}};

// PB0 remains SPI1_NSS/AF0 and is also mapped to EXTI0 so CS assertion and
// release do not depend on a foreground polling loop. PA0 is deliberately
// left unused for this reference pin map to free EXTI0 for PB0.
constexpr PinDescriptor kSpiCsN = {GpioPort::kB, 0, 15, 0};
constexpr PinDescriptor kSpiSck = {GpioPort::kB, 3, 27, kNoExti};
constexpr PinDescriptor kSpiMiso = {GpioPort::kB, 4, 28, kNoExti};
constexpr PinDescriptor kSpiMosi = {GpioPort::kB, 5, 29, kNoExti};
constexpr PinDescriptor kCarrierIrqN = {GpioPort::kB, 8, 32, kNoExti};
constexpr PinDescriptor kResetN = {GpioPort::kF, 2, 6, kNoExti};
constexpr PinDescriptor kSwdio = {GpioPort::kA, 13, 24, kNoExti};
constexpr PinDescriptor kSwclk = {GpioPort::kA, 14, 25, kNoExti};

struct Spi1PinMap {
    PinDescriptor cs_n;
    PinDescriptor sck;
    PinDescriptor miso;
    PinDescriptor mosi;
};

constexpr Spi1PinMap kSpi1PinMap = {
    kSpiCsN,
    kSpiSck,
    kSpiMiso,
    kSpiMosi,
};

constexpr std::uint8_t kSpiMode = 0;
constexpr std::uint32_t kHostSpiClockHz = 1'000'000U;

constexpr bool input_exti_lines_are_unique() {
    for (std::size_t left = 0; left < kCarrierInputPins.size(); ++left) {
        for (std::size_t right = left + 1; right < kCarrierInputPins.size();
             ++right) {
            if (kCarrierInputPins[left].exti_line ==
                kCarrierInputPins[right].exti_line) {
                return false;
            }
        }
    }
    return true;
}

constexpr bool package_pins_are_unique() {
    constexpr std::array<PinDescriptor, 18> pins = {{
        kCarrierInputPins[0], kCarrierInputPins[1], kCarrierInputPins[2],
        kCarrierInputPins[3], kCarrierInputPins[4], kCarrierInputPins[5],
        kCarrierInputPins[6], kCarrierInputPins[7], kCarrierInputPins[8],
        kCarrierInputPins[9], kSpiCsN, kSpiSck, kSpiMiso, kSpiMosi,
        kCarrierIrqN, kResetN, kSwdio, kSwclk,
    }};
    for (std::size_t left = 0; left < pins.size(); ++left) {
        for (std::size_t right = left + 1; right < pins.size(); ++right) {
            if (pins[left].package_pin == pins[right].package_pin) {
                return false;
            }
        }
    }
    return true;
}

static_assert(kCarrierInputPins.size() == 10,
              "the carrier must expose ten isolated input channels");
static_assert(input_exti_lines_are_unique(),
              "each carrier input must have a unique EXTI line");
static_assert(package_pins_are_unique(),
              "the STM32G031K8U6 package pin map must not overlap");

// Function pointers keep this contract usable from a no-allocation ISR/DMA
// adapter. A real port supplies these with STM32Cube LL, HAL, or registers.
struct PlatformHooks {
    using ConfigureInputExti = bool (*)(std::uint8_t logical_channel,
                                         PinDescriptor pin);
    using ConfigureTimer1MHz = bool (*)();
    using ConfigureSpi1SlaveDma = bool (*)(Spi1PinMap pin_map,
                                            const std::uint8_t* tx_buffer,
                                            std::size_t tx_buffer_bytes,
                                            std::uint8_t spi_mode);
    using ConfigureIrqOutput = bool (*)(PinDescriptor pin);
    using DriveIrqN = void (*)(bool high);

    ConfigureInputExti configure_input_exti = nullptr;
    ConfigureTimer1MHz configure_timer_1mhz = nullptr;
    ConfigureSpi1SlaveDma configure_spi1_slave_dma = nullptr;
    ConfigureIrqOutput configure_irq_output = nullptr;
    DriveIrqN drive_irq_n = nullptr;
};

// STM32G0 integration shell. It owns the platform-neutral capture and SPI
// transaction state, while the hooks own all MCU registers/interrupt vectors.
// It must not be described as a working STM32 firmware until the hooks are
// bound to real STM32G0 peripherals and the board waveforms are measured.
class M6CarrierStm32G031Port {
  public:
    M6CarrierStm32G031Port();

    bool initialize(const PlatformHooks& hooks);

    // Called by each EXTI ISR with a TIM2 (or equivalent) 1-us timestamp.
    bool on_input_edge(std::uint8_t logical_channel,
                       std::uint8_t level,
                       std::uint64_t timestamp_us);

    // Marks an input-side ambiguity (for example, both EXTI edge latches
    // being set before the ISR ran). The next staged frame becomes invalid;
    // this is deliberately fail-closed rather than fabricating edge order.
    void mark_capture_fault();

    // Called from the low-priority service loop. It may stage one frame and
    // updates IRQ_N after every state transition.
    bool service();

    // Called by the SPI/NSS edge glue at CS assertion/release. A CS
    // assertion with neither an event frame nor a pending clock response is
    // treated as the first leg of the clock-sync request exchange.
    bool on_cs_asserted();
    bool on_cs_asserted(std::uint64_t carrier_timestamp_us);
    bool on_cs_released(std::size_t transferred_bytes);
    bool on_cs_released(std::size_t transferred_bytes,
                        const std::uint8_t* rx_buffer,
                        std::size_t rx_buffer_bytes,
                        std::uint64_t carrier_timestamp_us);

    bool clock_sync_request_active() const {
        return transport_.clock_sync_request_active();
    }

    // Clears captured edges and any staged frame after a board reset or a
    // deliberate fault boundary. The peripheral configuration remains owned
    // by the platform hooks.
    void reset_runtime_state();

    bool initialized() const { return initialized_; }
    bool frame_ready() const { return transport_.frame_ready(); }
    bool transaction_active() const {
        return transport_.transaction_active();
    }
    bool irq_asserted() const { return transport_.irq_asserted(); }
    std::size_t wire_frame_bytes() const { return transport_.wire_frame_bytes(); }
    std::size_t tx_transfer_bytes() const {
        return transport_.tx_transfer_bytes();
    }
    const std::uint8_t* tx_buffer() const { return transport_.tx_buffer(); }

  private:
    void update_irq();

    M6CarrierCaptureCore capture_;
    M6CarrierSpiSlaveTransport transport_;
    PlatformHooks hooks_{};
    bool initialized_ = false;
};

}  // namespace smartgear::carrier::stm32g031
