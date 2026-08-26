#include "m6_carrier_stm32g031_register_port.h"

#include <cstdint>
#include <new>

namespace {

using RegisterPort =
    smartgear::carrier::stm32g031::M6CarrierStm32G031RegisterPort;

// The reference image deliberately constructs the port after .bss has been
// initialized. This keeps the startup file independent of a C++ runtime and
// makes the linked image usable with the freestanding toolchain target.
alignas(RegisterPort) std::uint8_t carrier_storage[sizeof(RegisterPort)];

[[noreturn]] void halt() {
    for (;;) {
        __asm volatile("wfi");
    }
}

}  // namespace

extern "C" int main() {
    // The reference board leaves the MCU on its reset HSI16 clock. A final
    // board may raise this to 64 MHz after its RCC/power policy is frozen.
    RegisterPort* carrier =
        ::new (static_cast<void*>(carrier_storage)) RegisterPort(16'000'000U);
    if (!carrier->initialize()) {
        halt();
    }

    for (;;) {
        (void)carrier->service();
        // The reference binding handles PB0/NSS through EXTI0. Keep the
        // polling fallback in the loop so a board-specific CS glue can be
        // substituted without changing the transport contract.
        (void)carrier->service_cs_level();
    }
}
