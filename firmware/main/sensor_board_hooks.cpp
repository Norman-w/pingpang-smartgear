#include "sensor_board_hooks.h"

#if defined(__GNUC__)
#define SMARTGEAR_WEAK __attribute__((weak))
#else
#define SMARTGEAR_WEAK
#endif

extern "C" SMARTGEAR_WEAK bool smartgear_board_read_sensor_health(
    char* /*calibration_id*/,
    const std::size_t /*calibration_id_capacity*/,
    std::uint16_t* /*healthy_beam_mask*/,
    bool* /*beam_health_valid*/,
    bool* /*piezo_baseline_valid*/,
    bool* /*calibration_valid*/) {
    return false;
}

#undef SMARTGEAR_WEAK
