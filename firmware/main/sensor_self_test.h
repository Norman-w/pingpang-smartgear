#pragma once

#include <array>
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

struct PiezoQuietBaseline {
    std::array<float, 2> peak = {0.0F, 0.0F};
    std::array<float, 2> rms = {0.0F, 0.0F};
    std::uint32_t sample_count = 0;
};

bool piezo_baseline_is_quiet(const PiezoQuietBaseline& baseline,
                             float max_peak,
                             float max_rms);

}  // namespace smartgear
