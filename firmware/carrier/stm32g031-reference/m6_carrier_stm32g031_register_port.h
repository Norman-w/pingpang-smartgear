#pragma once

// This adapter is intentionally compiled only by the optional STM32G031
// object target. It binds the platform-neutral port contract to the official
// STM32G031 CMSIS device header; it is not pulled into host tests.

#include <array>
#include <cstddef>
#include <cstdint>

#include "m6_carrier_stm32g031_port.h"

namespace smartgear::carrier::stm32g031 {

class M6CarrierStm32G031RegisterPort {
  public:
    // The timer clock is the TIM2 input clock after the application's RCC
    // setup. The default matches the documented 64 MHz G031 candidate.
    explicit M6CarrierStm32G031RegisterPort(
        std::uint32_t timer_input_clock_hz = 64'000'000U);

    // Binds GPIOA EXTI, TIM2, PB8 IRQ_N and SPI1/DMA1. The caller must provide
    // the CMSIS startup/vector table and must call service() from the main
    // loop. No board power or sensor-level protection is inferred here.
    bool initialize();
    bool service();

    // The PB0 NSS pin remains a hardware SPI input and the register binding
    // maps it to EXTI0. Applications with another CS edge glue can still call
    // these at the real boundaries; service_cs_level() remains a fallback.
    bool on_cs_asserted();
    bool on_cs_released(std::size_t transferred_bytes);
    bool on_cs_released();

    // Poll PB0 as a fallback for a board port that does not use the reference
    // EXTI0 mapping. A missed assertion is deliberately reported as false
    // rather than fabricating a complete transaction.
    bool service_cs_level();

    // Returns the common RX/TX DMA progress, or zero when the two channels
    // disagree or there is no active transaction. A disagreement is treated
    // as an incomplete transaction by on_cs_released().
    std::size_t observed_transaction_bytes() const;

    void reset_runtime_state();

    M6CarrierStm32G031Port& port() { return port_; }
    const M6CarrierStm32G031Port& port() const { return port_; }

    // ISR entry points. They are also exposed as weak C symbols below so an
    // application can either use the default vectors or forward from its own
    // startup file.
    static void handle_exti(std::uint32_t line_mask);
    static void handle_dma1_channel1();
    static void handle_dma1_channel2_3();
    static void handle_spi1();

    static M6CarrierStm32G031RegisterPort* active_instance() {
        return active_;
    }

  private:
    static bool configure_input_exti(std::uint8_t logical_channel,
                                     PinDescriptor pin);
    static bool configure_timer_1mhz();
    static bool configure_spi1_slave_dma(Spi1PinMap pin_map,
                                          const std::uint8_t* tx_buffer,
                                          std::size_t tx_buffer_bytes,
                                          std::uint8_t spi_mode);
    static bool configure_irq_output(PinDescriptor pin);
    static void drive_irq_n(bool high);

    static bool arm_dma_for_transaction();
    static void disable_dma();
    static void clear_dma_flags();
    static void clear_spi_receive_state();
    static void enable_exti_irqs();

    std::uint64_t timestamp_us();
    static std::uint32_t pin_mask(PinDescriptor pin);
    static bool is_expected_spi_pin_map(Spi1PinMap pin_map);

    static M6CarrierStm32G031RegisterPort* active_;

    M6CarrierStm32G031Port port_;
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> rx_sink_{};
    std::uint32_t timer_input_clock_hz_;
    std::uint32_t last_timer_count_ = 0;
    std::uint32_t timer_wraps_ = 0;
    bool initialized_ = false;
    bool cs_active_ = false;
};

}  // namespace smartgear::carrier::stm32g031
