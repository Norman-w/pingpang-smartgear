#include <cstdint>

extern "C" {

extern std::uint32_t _estack;
extern std::uint32_t _sidata;
extern std::uint32_t _sdata;
extern std::uint32_t _edata;
extern std::uint32_t _sbss;
extern std::uint32_t _ebss;

[[noreturn]] void Reset_Handler();
[[noreturn]] void Default_Handler();
int main();

void EXTI0_1_IRQHandler();
void EXTI2_3_IRQHandler();
void EXTI4_15_IRQHandler();
void DMA1_Channel1_IRQHandler();
void DMA1_Channel2_3_IRQHandler();
void SPI1_IRQHandler();

}

namespace {

using VectorWord = std::uintptr_t;

constexpr VectorWord address_of(void (*handler)()) {
    return reinterpret_cast<VectorWord>(handler);
}

}  // namespace

extern "C" __attribute__((used, section(".isr_vector"), aligned(256)))
const VectorWord g_vector_table[] = {
    reinterpret_cast<VectorWord>(&_estack),
    address_of(&Reset_Handler),
    address_of(&Default_Handler),  // NMI
    address_of(&Default_Handler),  // HardFault
    0U,                            // reserved
    0U,                            // reserved
    0U,                            // reserved
    0U,                            // reserved
    0U,                            // reserved
    0U,                            // reserved
    0U,                            // reserved
    address_of(&Default_Handler),  // SVCall
    0U,                            // reserved
    0U,                            // reserved
    address_of(&Default_Handler),  // PendSV
    address_of(&Default_Handler),  // SysTick

    // STM32G031 IRQ0..IRQ29. Unused peripherals intentionally point at the
    // same fail-stop handler; EXTI, DMA and SPI are the active carrier
    // handlers in this reference image. EXTI0 also receives PB0/NSS CS edges.
    address_of(&Default_Handler),       // WWDG 0
    address_of(&Default_Handler),       // PVD 1
    address_of(&Default_Handler),       // RTC_TAMP 2
    address_of(&Default_Handler),       // FLASH 3
    address_of(&Default_Handler),       // RCC 4
    address_of(&EXTI0_1_IRQHandler),    // EXTI0_1 5
    address_of(&EXTI2_3_IRQHandler),    // EXTI2_3 6
    address_of(&EXTI4_15_IRQHandler),   // EXTI4_15 7
    address_of(&Default_Handler),       // reserved/UCPD slot 8
    address_of(&DMA1_Channel1_IRQHandler),    // DMA1 channel 1 9
    address_of(&DMA1_Channel2_3_IRQHandler),  // DMA1 channel 2/3 10
    address_of(&Default_Handler),       // DMA1/DMAMUX overflow 11
    address_of(&Default_Handler),       // ADC1 12
    address_of(&Default_Handler),       // TIM1_BRK_UP_TRG_COM 13
    address_of(&Default_Handler),       // TIM1_CC 14
    address_of(&Default_Handler),       // TIM2 15
    address_of(&Default_Handler),       // TIM3 16
    address_of(&Default_Handler),       // LPTIM1 17
    address_of(&Default_Handler),       // LPTIM2 18
    address_of(&Default_Handler),       // TIM14 19
    address_of(&Default_Handler),       // reserved 20
    address_of(&Default_Handler),       // TIM16 21
    address_of(&Default_Handler),       // TIM17 22
    address_of(&Default_Handler),       // I2C1 23
    address_of(&Default_Handler),       // I2C2 24
    address_of(&SPI1_IRQHandler),       // SPI1 25
    address_of(&Default_Handler),       // SPI2 26
    address_of(&Default_Handler),       // USART1 27
    address_of(&Default_Handler),       // USART2 28
    address_of(&Default_Handler),       // LPUART1 29
};

extern "C" [[noreturn]] void Reset_Handler() {
    std::uint32_t* source = &_sidata;
    std::uint32_t* destination = &_sdata;
    while (destination < &_edata) {
        *destination++ = *source++;
    }

    destination = &_sbss;
    while (destination < &_ebss) {
        *destination++ = 0U;
    }

    (void)main();
    for (;;) {
        __asm volatile("wfi");
    }
}

extern "C" [[noreturn]] void Default_Handler() {
    for (;;) {
        __asm volatile("wfi");
    }
}
