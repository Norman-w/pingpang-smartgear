#include "sensor_self_test.h"

#include <algorithm>
#include <cmath>
#include <cstring>

namespace smartgear {

BeamSelfTestReport evaluate_beam_self_test(
    const std::array<BeamChannelCheck, config::kBeamCount>& checks) {
    BeamSelfTestReport report;
    for (std::uint8_t channel = 0; channel < config::kBeamCount; ++channel) {
        const auto& check = checks[channel];
        const bool pass = check.emitter_ok && check.receiver_ok &&
                          check.clear_baseline && check.blocked_response;
        if (pass) {
            report.pass_mask = static_cast<std::uint16_t>(
                report.pass_mask | static_cast<std::uint16_t>(1U << channel));
        } else {
            report.fail_mask = static_cast<std::uint16_t>(
                report.fail_mask | static_cast<std::uint16_t>(1U << channel));
        }
    }
    report.all_pass = report.fail_mask == 0;
    return report;
}

bool piezo_baseline_is_quiet(const PiezoQuietBaseline& baseline,
                             const float max_peak,
                             const float max_rms) {
    if (baseline.sample_count == 0 || max_peak < 0.0F || max_rms < 0.0F) {
        return false;
    }
    for (std::size_t channel = 0; channel < 2; ++channel) {
        if (!std::isfinite(baseline.peak[channel]) ||
            !std::isfinite(baseline.rms[channel]) || baseline.peak[channel] < 0.0F ||
            baseline.rms[channel] < 0.0F || baseline.peak[channel] > max_peak ||
            baseline.rms[channel] > max_rms) {
            return false;
        }
    }
    return true;
}

bool sensor_health_snapshot_is_well_formed(
    const char* calibration_id,
    const std::size_t calibration_id_capacity,
    const std::uint16_t healthy_beam_mask,
    const bool beam_health_valid,
    const bool calibration_valid) {
    if (calibration_id == nullptr || calibration_id_capacity == 0 ||
        std::memchr(calibration_id, '\0', calibration_id_capacity) == nullptr) {
        return false;
    }
    if (calibration_valid && calibration_id[0] == '\0') {
        return false;
    }
    if (beam_health_valid &&
        (healthy_beam_mask & static_cast<std::uint16_t>(~config::kAllBeamMask)) !=
            0) {
        return false;
    }
    return true;
}

}  // namespace smartgear
