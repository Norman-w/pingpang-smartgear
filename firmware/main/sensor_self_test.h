#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include "net_sensor_config.h"

namespace smartgear {

struct BeamChannelCheck {
    bool emitter_ok = false;
    bool receiver_ok = false;
    bool clear_baseline = false;
    bool blocked_response = false;
};

struct BeamSelfTestReport {
    std::uint16_t pass_mask = 0;
    std::uint16_t fail_mask = 0;
    bool all_pass = false;
};

BeamSelfTestReport evaluate_beam_self_test(
    const std::array<BeamChannelCheck, config::kBeamCount>& checks);

bool beam_self_test_report_is_well_formed(const BeamSelfTestReport& report);

struct PiezoQuietBaseline {
    std::array<float, 2> peak = {0.0F, 0.0F};
    std::array<float, 2> rms = {0.0F, 0.0F};
    std::uint32_t sample_count = 0;
};

bool piezo_baseline_is_quiet(const PiezoQuietBaseline& baseline,
                             float max_peak,
                             float max_rms);

struct SensorHealthSnapshot {
    std::uint16_t healthy_beam_mask = 0;
    bool beam_health_valid = false;
    bool piezo_baseline_valid = false;
    bool calibration_valid = false;
};

// Compose the board hook's fail-closed health fields from the separately
// measured optical self-test, PVDF quiet baseline and mechanical calibration.
// Partial optical failure is still a valid health snapshot: only channels in
// healthy_beam_mask may authorize a height result.
SensorHealthSnapshot make_sensor_health_snapshot(
    const BeamSelfTestReport& beam_report,
    const PiezoQuietBaseline& baseline,
    float max_peak,
    float max_rms,
    const char* calibration_id,
    std::size_t calibration_id_capacity,
    bool mechanical_calibration_valid);

// Validate the shape of the board health snapshot before it reaches the
// event state machine. A false calibration flag is allowed, because it is a
// valid fail-closed boot/self-test state; a true flag requires a non-empty
// bounded ID.
bool sensor_health_snapshot_is_well_formed(const char* calibration_id,
                                           std::size_t calibration_id_capacity,
                                           std::uint16_t healthy_beam_mask,
                                           bool beam_health_valid,
                                           bool calibration_valid);

}  // namespace smartgear
