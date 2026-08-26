#include "m6_carrier_stm32g031_register_port.h"

#include <limits>

// This is the device-specific header published by STMicroelectronics. The
// optional CMake target supplies its Include/ directory and the matching
// CMSIS-Core include directory.
#include "stm32g031xx.h"

namespace smartgear::carrier::stm32g031 {
namespace {

constexpr std::uint32_t kGpioInputMode = 0U;
constexpr std::uint32_t kGpioOutputMode = 1U;
constexpr std::uint32_t kGpioAlternateMode = 2U;
constexpr std::uint32_t kGpioModeMask = 0x3U;
constexpr std::uint32_t kGpioPullMask = 0x3U;
constexpr std::uint32_t kGpioAlternateMask = 0xFU;
constexpr std::uint32_t kExtiPortMask = 0x7U;
constexpr std::uint32_t kExtiPortB = 0x1U;
constexpr std::uint32_t kDmamuxSpi1RxRequest = 0x10U;
constexpr std::uint32_t kDmamuxSpi1TxRequest = 0x11U;
constexpr std::uint32_t kDmaChannel1Flags =
    DMA_ISR_GIF1 | DMA_ISR_TCIF1 | DMA_ISR_HTIF1 | DMA_ISR_TEIF1;
constexpr std::uint32_t kDmaChannel2Flags =
    DMA_ISR_GIF2 | DMA_ISR_TCIF2 | DMA_ISR_HTIF2 | DMA_ISR_TEIF2;
constexpr std::uint32_t kCarrierInputExtiMask =
    (1UL << 1U) | (1UL << 2U) | (1UL << 3U) | (1UL << 4U) |
    (1UL << 5U) | (1UL << 6U) | (1UL << 7U) | (1UL << 9U) |
    (1UL << 10U) | (1UL << 15U);
constexpr std::uint32_t kCarrierCsExtiMask = 1UL << 0U;
constexpr std::uint32_t kCarrierExtiMask =
    kCarrierInputExtiMask | kCarrierCsExtiMask;

template <typename Register>
void set_gpio_mode(Register* gpio, const std::uint8_t pin,
                   const std::uint32_t mode) {
    const std::uint32_t shift = static_cast<std::uint32_t>(pin) * 2U;
    gpio->MODER = (gpio->MODER & ~(kGpioModeMask << shift)) |
                  ((mode & kGpioModeMask) << shift);
}

template <typename Register>
void set_gpio_pull_none(Register* gpio, const std::uint8_t pin) {
    const std::uint32_t shift = static_cast<std::uint32_t>(pin) * 2U;
    gpio->PUPDR &= ~(kGpioPullMask << shift);
}

template <typename Register>
void set_gpio_pull_up(Register* gpio, const std::uint8_t pin) {
    const std::uint32_t shift = static_cast<std::uint32_t>(pin) * 2U;
    gpio->PUPDR = (gpio->PUPDR & ~(kGpioPullMask << shift)) |
                  (1UL << shift);
}

template <typename Register>
void set_gpio_speed_high(Register* gpio, const std::uint8_t pin) {
    const std::uint32_t shift = static_cast<std::uint32_t>(pin) * 2U;
    gpio->OSPEEDR |= kGpioModeMask << shift;
}

template <typename Register>
void set_gpio_af0(Register* gpio, const std::uint8_t pin) {
    const std::uint8_t register_index = pin >= 8U ? 1U : 0U;
    const std::uint32_t shift = static_cast<std::uint32_t>(pin & 7U) * 4U;
    gpio->AFR[register_index] &= ~(kGpioAlternateMask << shift);
}

std::uint32_t pointer_address(const volatile void* pointer) {
    return static_cast<std::uint32_t>(
        reinterpret_cast<std::uintptr_t>(pointer));
}

}  // namespace

M6CarrierStm32G031RegisterPort*
    M6CarrierStm32G031RegisterPort::active_ = nullptr;

M6CarrierStm32G031RegisterPort::M6CarrierStm32G031RegisterPort(
    const std::uint32_t timer_input_clock_hz)
    : timer_input_clock_hz_(timer_input_clock_hz) {}

bool M6CarrierStm32G031RegisterPort::initialize() {
    if (active_ != nullptr && active_ != this) {
        return false;
    }
    active_ = this;
    initialized_ = false;
    cs_active_ = false;
    rx_sink_.fill(0U);

    PlatformHooks hooks;
    hooks.configure_input_exti = &configure_input_exti;
    hooks.configure_timer_1mhz = &configure_timer_1mhz;
    hooks.configure_spi1_slave_dma = &configure_spi1_slave_dma;
    hooks.configure_irq_output = &configure_irq_output;
    hooks.drive_irq_n = &drive_irq_n;

    if (!port_.initialize(hooks)) {
        active_ = nullptr;
        return false;
    }

    initialized_ = true;
    enable_exti_irqs();
    return true;
}

bool M6CarrierStm32G031RegisterPort::service() {
    return initialized_ && port_.service();
}

bool M6CarrierStm32G031RegisterPort::on_cs_asserted() {
    if (!initialized_ || !port_.on_cs_asserted(timestamp_us())) {
        return false;
    }
    if (arm_dma_for_transaction()) {
        cs_active_ = true;
        return true;
    }

    disable_dma();
    (void)on_cs_released(0U);
    return false;
}

bool M6CarrierStm32G031RegisterPort::on_cs_released(
    const std::size_t transferred_bytes) {
    if (!initialized_) {
        return false;
    }
    cs_active_ = false;
    disable_dma();
    clear_spi_receive_state();
    return port_.on_cs_released(transferred_bytes, rx_sink_.data(),
                                 rx_sink_.size(), timestamp_us());
}

bool M6CarrierStm32G031RegisterPort::on_cs_released() {
    return on_cs_released(observed_transaction_bytes());
}

bool M6CarrierStm32G031RegisterPort::service_cs_level() {
    if (!initialized_) {
        return false;
    }

    const bool asserted = (GPIOB->IDR & (1UL << kSpiCsN.number)) == 0U;
    if (asserted) {
        if (cs_active_) {
            return true;
        }
        return on_cs_asserted();
    }
    if (!cs_active_) {
        return true;
    }
    return on_cs_released();
}

std::size_t M6CarrierStm32G031RegisterPort::observed_transaction_bytes()
    const {
    if (active_ != this || !initialized_ || !port_.transaction_active()) {
        return 0U;
    }

    const std::uint32_t rx_remaining = DMA1_Channel1->CNDTR;
    const std::uint32_t tx_remaining = DMA1_Channel2->CNDTR;
    if (rx_remaining > kM6CarrierMaxFrameBytes ||
        tx_remaining > kM6CarrierMaxFrameBytes ||
        rx_remaining != tx_remaining) {
        return 0U;
    }
    return kM6CarrierMaxFrameBytes -
           static_cast<std::size_t>(rx_remaining);
}

void M6CarrierStm32G031RegisterPort::reset_runtime_state() {
    if (initialized_) {
        disable_dma();
        clear_spi_receive_state();
    }
    port_.reset_runtime_state();
    cs_active_ = false;
}

bool M6CarrierStm32G031RegisterPort::configure_input_exti(
    const std::uint8_t logical_channel, const PinDescriptor pin) {
    if (active_ == nullptr || logical_channel >= kCarrierInputPins.size() ||
        pin.port != GpioPort::kA ||
        pin.number != kCarrierInputPins[logical_channel].number ||
        pin.exti_line != kCarrierInputPins[logical_channel].exti_line) {
        return false;
    }

    RCC->IOPENR |= RCC_IOPENR_GPIOAEN;
    const std::uint32_t gpio_mask = 1UL << pin.number;
    set_gpio_mode(GPIOA, pin.number, kGpioInputMode);
    set_gpio_pull_none(GPIOA, pin.number);
    GPIOA->AFR[pin.number >= 8U ? 1U : 0U] &=
        ~(kGpioAlternateMask << (static_cast<std::uint32_t>(pin.number & 7U) *
                                 4U));

    const std::uint32_t exticr_index = pin.exti_line / 4U;
    const std::uint32_t exticr_shift = (pin.exti_line & 3U) * 8U;
    EXTI->EXTICR[exticr_index] &= ~(kExtiPortMask << exticr_shift);

    EXTI->RTSR1 |= gpio_mask;
    EXTI->FTSR1 |= gpio_mask;
    EXTI->IMR1 |= gpio_mask;
    // RPR1/FPR1 are write-one-to-clear registers on STM32G0.
    EXTI->RPR1 = gpio_mask;
    EXTI->FPR1 = gpio_mask;
    return true;
}

bool M6CarrierStm32G031RegisterPort::configure_timer_1mhz() {
    if (active_ == nullptr || active_->timer_input_clock_hz_ < 1'000'000U ||
        active_->timer_input_clock_hz_ % 1'000'000U != 0U) {
        return false;
    }

    RCC->APBENR1 |= RCC_APBENR1_TIM2EN;
    TIM2->CR1 = 0U;
    TIM2->DIER = 0U;
    TIM2->PSC = active_->timer_input_clock_hz_ / 1'000'000U - 1U;
    TIM2->ARR = std::numeric_limits<std::uint32_t>::max();
    TIM2->CNT = 0U;
    TIM2->EGR = TIM_EGR_UG;
    TIM2->SR = 0U;
    TIM2->CR1 = TIM_CR1_CEN;
    active_->last_timer_count_ = 0U;
    active_->timer_wraps_ = 0U;
    return true;
}

bool M6CarrierStm32G031RegisterPort::configure_spi1_slave_dma(
    const Spi1PinMap pin_map, const std::uint8_t* tx_buffer,
    const std::size_t tx_buffer_bytes, const std::uint8_t spi_mode) {
    if (active_ == nullptr || !is_expected_spi_pin_map(pin_map) ||
        tx_buffer == nullptr || tx_buffer_bytes != kM6CarrierMaxFrameBytes ||
        spi_mode != kSpiMode) {
        return false;
    }

    RCC->IOPENR |= RCC_IOPENR_GPIOBEN;
    RCC->APBENR2 |= RCC_APBENR2_SYSCFGEN;
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;
    RCC->APBENR2 |= RCC_APBENR2_SPI1EN;

    constexpr std::array<std::uint8_t, 4> spi_pins = {0U, 3U, 4U, 5U};
    for (const std::uint8_t pin : spi_pins) {
        set_gpio_mode(GPIOB, pin, kGpioAlternateMode);
        set_gpio_pull_none(GPIOB, pin);
        set_gpio_speed_high(GPIOB, pin);
        set_gpio_af0(GPIOB, pin);
        GPIOB->OTYPER &= ~(1UL << pin);
    }

    // The host normally drives CS, but a pull-up keeps NSS/EXTI0 in the
    // released state while the host or the carrier is unpowered.
    set_gpio_pull_up(GPIOB, kSpiCsN.number);

    // PB0 is simultaneously SPI1_NSS/AF0 and the EXTI0 source. PA0 is left
    // unused by the ten input map so the CS edge has a dedicated interrupt.
    const std::uint32_t cs_exti_shift =
        (static_cast<std::uint32_t>(kSpiCsN.exti_line & 3U) * 8U);
    EXTI->EXTICR[kSpiCsN.exti_line / 4U] =
        (EXTI->EXTICR[kSpiCsN.exti_line / 4U] &
         ~(kExtiPortMask << cs_exti_shift)) |
        (kExtiPortB << cs_exti_shift);
    const std::uint32_t cs_mask = 1UL << kSpiCsN.exti_line;
    EXTI->RTSR1 |= cs_mask;
    EXTI->FTSR1 |= cs_mask;
    EXTI->IMR1 |= cs_mask;
    EXTI->RPR1 = cs_mask;
    EXTI->FPR1 = cs_mask;

    disable_dma();
    clear_dma_flags();
    DMAMUX1_Channel0->CCR = kDmamuxSpi1RxRequest;
    DMAMUX1_Channel1->CCR = kDmamuxSpi1TxRequest;

    SPI1->CR1 = 0U;
    SPI1->CR2 = (7UL << SPI_CR2_DS_Pos) | SPI_CR2_FRXTH |
                SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN | SPI_CR2_ERRIE;
    SPI1->CR1 = SPI_CR1_SPE;

    DMA1_Channel1->CPAR = pointer_address(&SPI1->DR);
    DMA1_Channel1->CMAR = pointer_address(active_->rx_sink_.data());
    DMA1_Channel2->CPAR = pointer_address(&SPI1->DR);
    DMA1_Channel2->CMAR = pointer_address(tx_buffer);
    DMA1_Channel1->CNDTR = 0U;
    DMA1_Channel2->CNDTR = 0U;
    clear_spi_receive_state();
    return true;
}

bool M6CarrierStm32G031RegisterPort::configure_irq_output(
    const PinDescriptor pin) {
    if (active_ == nullptr || pin.port != kCarrierIrqN.port ||
        pin.number != kCarrierIrqN.number) {
        return false;
    }

    RCC->IOPENR |= RCC_IOPENR_GPIOBEN;
    set_gpio_mode(GPIOB, pin.number, kGpioOutputMode);
    set_gpio_pull_none(GPIOB, pin.number);
    GPIOB->OTYPER &= ~(1UL << pin.number);
    set_gpio_speed_high(GPIOB, pin.number);
    GPIOB->BSRR = 1UL << pin.number;
    return true;
}

void M6CarrierStm32G031RegisterPort::drive_irq_n(const bool high) {
    if (active_ == nullptr) {
        return;
    }
    const std::uint32_t mask = 1UL << kCarrierIrqN.number;
    GPIOB->BSRR = high ? mask : (mask << 16U);
}

bool M6CarrierStm32G031RegisterPort::arm_dma_for_transaction() {
    if (active_ == nullptr || !active_->initialized_) {
        return false;
    }

    disable_dma();
    clear_dma_flags();
    active_->rx_sink_.fill(0U);

    DMA1_Channel1->CNDTR = kM6CarrierMaxFrameBytes;
    DMA1_Channel2->CNDTR = kM6CarrierMaxFrameBytes;
    DMA1_Channel1->CCR = DMA_CCR_MINC | DMA_CCR_PL_1 | DMA_CCR_TEIE;
    DMA1_Channel2->CCR =
        DMA_CCR_DIR | DMA_CCR_MINC | DMA_CCR_PL_1 | DMA_CCR_TEIE;
    DMA1_Channel1->CCR |= DMA_CCR_EN;
    DMA1_Channel2->CCR |= DMA_CCR_EN;
    return true;
}

void M6CarrierStm32G031RegisterPort::disable_dma() {
    if (active_ == nullptr) {
        return;
    }
    DMA1_Channel1->CCR &= ~DMA_CCR_EN;
    DMA1_Channel2->CCR &= ~DMA_CCR_EN;
}

void M6CarrierStm32G031RegisterPort::clear_dma_flags() {
    if (active_ == nullptr) {
        return;
    }
    DMA1->IFCR = DMA_IFCR_CGIF1 | DMA_IFCR_CGIF2;
}

void M6CarrierStm32G031RegisterPort::clear_spi_receive_state() {
    if (active_ == nullptr) {
        return;
    }
    const std::uint32_t status = SPI1->SR;
    if ((status & SPI_SR_OVR) != 0U || (status & SPI_SR_RXNE) != 0U) {
        (void)SPI1->DR;
    }
    if ((status & (SPI_SR_UDR | SPI_SR_MODF)) != 0U) {
        // The STM32 SPI error-clear sequence is read SR, then rewrite CR1.
        // Re-enabling SPE returns the slave to a known peripheral state before
        // the next CS-gated DMA transaction.
        SPI1->CR1 = 0U;
        SPI1->CR1 = SPI_CR1_SPE;
    }
}

void M6CarrierStm32G031RegisterPort::enable_exti_irqs() {
    NVIC_SetPriority(EXTI0_1_IRQn, 1U);
    NVIC_SetPriority(EXTI2_3_IRQn, 1U);
    NVIC_SetPriority(EXTI4_15_IRQn, 1U);
    NVIC_SetPriority(DMA1_Channel1_IRQn, 0U);
    NVIC_SetPriority(DMA1_Channel2_3_IRQn, 0U);
    NVIC_SetPriority(SPI1_IRQn, 0U);
    NVIC_EnableIRQ(EXTI0_1_IRQn);
    NVIC_EnableIRQ(EXTI2_3_IRQn);
    NVIC_EnableIRQ(EXTI4_15_IRQn);
    NVIC_EnableIRQ(DMA1_Channel1_IRQn);
    NVIC_EnableIRQ(DMA1_Channel2_3_IRQn);
    NVIC_EnableIRQ(SPI1_IRQn);
}

std::uint64_t M6CarrierStm32G031RegisterPort::timestamp_us() {
    const std::uint32_t counter = TIM2->CNT;
    if (counter < last_timer_count_) {
        ++timer_wraps_;
    }
    last_timer_count_ = counter;
    return (static_cast<std::uint64_t>(timer_wraps_) << 32U) | counter;
}

std::uint32_t M6CarrierStm32G031RegisterPort::pin_mask(
    const PinDescriptor pin) {
    return 1UL << pin.number;
}

bool M6CarrierStm32G031RegisterPort::is_expected_spi_pin_map(
    const Spi1PinMap pin_map) {
    return pin_map.cs_n.port == kSpiCsN.port &&
           pin_map.cs_n.number == kSpiCsN.number &&
           pin_map.sck.port == kSpiSck.port &&
           pin_map.sck.number == kSpiSck.number &&
           pin_map.miso.port == kSpiMiso.port &&
           pin_map.miso.number == kSpiMiso.number &&
           pin_map.mosi.port == kSpiMosi.port &&
           pin_map.mosi.number == kSpiMosi.number;
}

void M6CarrierStm32G031RegisterPort::handle_exti(
    const std::uint32_t line_mask) {
    M6CarrierStm32G031RegisterPort* self = active_;
    if (self == nullptr || !self->initialized_) {
        return;
    }

    const std::uint32_t rising = EXTI->RPR1 & line_mask & kCarrierExtiMask;
    const std::uint32_t falling = EXTI->FPR1 & line_mask & kCarrierExtiMask;
    const std::uint32_t pending = rising | falling;
    if (pending == 0U) {
        return;
    }
    EXTI->RPR1 = pending;
    EXTI->FPR1 = pending;

    const std::uint32_t input_pending = pending & kCarrierInputExtiMask;
    const std::uint32_t input_rising = rising & kCarrierInputExtiMask;
    const std::uint32_t input_falling = falling & kCarrierInputExtiMask;
    if (input_pending != 0U) {
        const std::uint64_t timestamp = self->timestamp_us();
        for (std::uint8_t channel = 0;
             channel < static_cast<std::uint8_t>(kCarrierInputPins.size());
             ++channel) {
            const PinDescriptor pin = kCarrierInputPins[channel];
            const std::uint32_t bit = pin_mask(pin);
            if ((input_pending & bit) == 0U) {
                continue;
            }
            if ((input_rising & bit) != 0U &&
                (input_falling & bit) != 0U) {
                // The two latches do not preserve which edge happened first.
                // Preserve the observable level but make the frame invalid.
                self->port_.mark_capture_fault();
            }
            const std::uint8_t level =
                (GPIOA->IDR & bit) == 0U ? 0U : 1U;
            (void)self->port_.on_input_edge(channel, level, timestamp);
        }
    }

    const std::uint32_t cs_pending = pending & kCarrierCsExtiMask;
    if (cs_pending == 0U) {
        return;
    }

    const bool cs_rising = (rising & kCarrierCsExtiMask) != 0U;
    const bool cs_falling = (falling & kCarrierCsExtiMask) != 0U;
    if (cs_rising && cs_falling) {
        self->port_.mark_capture_fault();
        if (self->port_.transaction_active()) {
            self->disable_dma();
            (void)self->on_cs_released(0U);
        }
        return;
    }

    const bool cs_low =
        (GPIOB->IDR & (1UL << kSpiCsN.number)) == 0U;
    if (cs_low) {
        (void)self->on_cs_asserted();
    } else {
        (void)self->on_cs_released();
    }
}

void M6CarrierStm32G031RegisterPort::handle_dma1_channel1() {
    M6CarrierStm32G031RegisterPort* self = active_;
    if (self == nullptr) {
        return;
    }
    const std::uint32_t flags = DMA1->ISR & kDmaChannel1Flags;
    if (flags == 0U) {
        return;
    }
    DMA1->IFCR = kDmaChannel1Flags;
    self->port_.mark_capture_fault();
    if ((flags & DMA_ISR_TEIF1) != 0U && self->port_.transaction_active()) {
        self->disable_dma();
        (void)self->on_cs_released(0U);
    }
}

void M6CarrierStm32G031RegisterPort::handle_dma1_channel2_3() {
    M6CarrierStm32G031RegisterPort* self = active_;
    if (self == nullptr) {
        return;
    }
    const std::uint32_t flags = DMA1->ISR & kDmaChannel2Flags;
    if (flags == 0U) {
        return;
    }
    DMA1->IFCR = kDmaChannel2Flags;
    self->port_.mark_capture_fault();
    if ((flags & DMA_ISR_TEIF2) != 0U && self->port_.transaction_active()) {
        self->disable_dma();
        (void)self->on_cs_released(0U);
    }
}

void M6CarrierStm32G031RegisterPort::handle_spi1() {
    M6CarrierStm32G031RegisterPort* self = active_;
    if (self == nullptr) {
        return;
    }
    const std::uint32_t status = SPI1->SR;
    if ((status & (SPI_SR_OVR | SPI_SR_UDR | SPI_SR_MODF)) == 0U) {
        return;
    }
    self->port_.mark_capture_fault();
    self->clear_spi_receive_state();
    if (self->port_.transaction_active()) {
        self->disable_dma();
        (void)self->on_cs_released(0U);
    }
}

}  // namespace smartgear::carrier::stm32g031

#if defined(__GNUC__)
#define SMARTGEAR_STM32G031_WEAK __attribute__((weak))
#else
#define SMARTGEAR_STM32G031_WEAK
#endif

extern "C" SMARTGEAR_STM32G031_WEAK void EXTI0_1_IRQHandler(void) {
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort::handle_exti(
        (1UL << 0U) | (1UL << 1U));
}

extern "C" SMARTGEAR_STM32G031_WEAK void EXTI2_3_IRQHandler(void) {
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort::handle_exti(
        (1UL << 2U) | (1UL << 3U));
}

extern "C" SMARTGEAR_STM32G031_WEAK void EXTI4_15_IRQHandler(void) {
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort::handle_exti(
        0xFFFFUL & ~((1UL << 4U) | (1UL << 8U) | (1UL << 11U) |
                     (1UL << 12U) | (1UL << 13U) | (1UL << 14U)));
}

extern "C" SMARTGEAR_STM32G031_WEAK void DMA1_Channel1_IRQHandler(void) {
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort::handle_dma1_channel1();
}

extern "C" SMARTGEAR_STM32G031_WEAK void DMA1_Channel2_3_IRQHandler(void) {
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort::handle_dma1_channel2_3();
}

extern "C" SMARTGEAR_STM32G031_WEAK void SPI1_IRQHandler(void) {
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort::handle_spi1();
}

#undef SMARTGEAR_STM32G031_WEAK
