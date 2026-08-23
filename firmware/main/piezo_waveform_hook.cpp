#include "piezo_waveform_hook.h"

#if defined(__GNUC__)
#define SMARTGEAR_WEAK __attribute__((weak))
#else
#define SMARTGEAR_WEAK
#endif

extern "C" SMARTGEAR_WEAK bool smartgear_board_on_piezo_waveform(
    const char* /*reference*/,
    const std::uint64_t /*trigger_us*/,
    const std::size_t /*pre_trigger_samples*/,
    const std::int16_t* /*left_samples*/,
    const std::size_t /*left_count*/,
    const std::int16_t* /*right_samples*/,
    const std::size_t /*right_count*/,
    const bool /*complete*/) {
    return false;
}

#undef SMARTGEAR_WEAK
