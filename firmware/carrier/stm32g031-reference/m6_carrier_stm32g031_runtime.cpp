#include <cstddef>
#include <cstdint>

// The reference image is intentionally linked without newlib or a board
// syscall layer.  Keep the small pieces of the C/C++ runtime needed by the
// carrier core here instead of silently pulling a hosted runtime into the
// 64 KiB flash budget.

namespace {

std::uint32_t enter_critical() {
    std::uint32_t primask = 0;
    __asm volatile("mrs %0, primask" : "=r"(primask) :: "memory");
    __asm volatile("cpsid i" ::: "memory");
    return primask;
}

void leave_critical(const std::uint32_t primask) {
    __asm volatile("msr primask, %0" :: "r"(primask) : "memory");
}

[[noreturn]] void halt() {
    for (;;) {
        __asm volatile("wfi");
    }
}

}  // namespace

extern "C" void* memset(void* destination,
                         const int value,
                         const std::size_t count) {
    auto* bytes = static_cast<std::uint8_t*>(destination);
    const auto fill = static_cast<std::uint8_t>(value);
    for (std::size_t index = 0; index < count; ++index) {
        bytes[index] = fill;
    }
    return destination;
}

extern "C" void* memcpy(void* destination,
                         const void* source,
                         const std::size_t count) {
    auto* destination_bytes = static_cast<std::uint8_t*>(destination);
    const auto* source_bytes = static_cast<const std::uint8_t*>(source);
    for (std::size_t index = 0; index < count; ++index) {
        destination_bytes[index] = source_bytes[index];
    }
    return destination;
}

extern "C" [[noreturn]] void abort() {
    halt();
}

// Cortex-M0+ has no native atomic byte/word instructions.  The carrier uses
// these GCC atomic fallbacks from both GPIO/SPI interrupt handlers and the
// foreground service loop, so preserve PRIMASK around each operation.  The
// memory-order argument is already enforced by the compiler at the call site;
// the single-core critical section supplies the required read/modify/write
// atomicity here.
extern "C" std::uint8_t __atomic_fetch_or_1(volatile void* address,
                                             const std::uint8_t value,
                                             int) {
    const auto primask = enter_critical();
    auto* target = static_cast<volatile std::uint8_t*>(address);
    const auto previous = *target;
    *target = static_cast<std::uint8_t>(previous | value);
    leave_critical(primask);
    return previous;
}

extern "C" unsigned int __atomic_fetch_add_4(volatile void* address,
                                               const unsigned int value,
                                               int) {
    const auto primask = enter_critical();
    auto* target = static_cast<volatile std::uint32_t*>(address);
    const auto previous = *target;
    *target = previous + value;
    leave_critical(primask);
    return static_cast<unsigned int>(previous);
}

extern "C" unsigned char __atomic_exchange_1(volatile void* address,
                                               const unsigned char value,
                                               int) {
    const auto primask = enter_critical();
    auto* target = static_cast<volatile std::uint8_t*>(address);
    const auto previous = *target;
    *target = value;
    leave_critical(primask);
    return previous;
}
