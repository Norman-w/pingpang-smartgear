#include "piezo_capture.h"

namespace smartgear {

PiezoCapture::PiezoCapture(const std::uint64_t merge_window_us)
    : merge_window_us_(merge_window_us) {}

std::optional<PiezoObservation> PiezoCapture::on_trigger(
    const std::uint8_t channel,
    const std::uint64_t timestamp_us,
    const float peak,
    const float energy,
    const std::string& waveform_ref) {
    if (channel >= 2) {
        return std::nullopt;
    }

    std::optional<PiezoObservation> completed;
    if (pending_ && timestamp_us >= pending_observation_.last_trigger_us &&
        timestamp_us - pending_observation_.last_trigger_us > merge_window_us_) {
        completed = finish();
    }

    if (!pending_) {
        pending_ = true;
        pending_observation_ = PiezoObservation{};
        pending_observation_.valid = true;
        pending_observation_.triggered = true;
        pending_observation_.first_trigger_us = timestamp_us;
    }

    pending_observation_.sensor_mask = static_cast<std::uint8_t>(
        pending_observation_.sensor_mask | static_cast<std::uint8_t>(1U << channel));
    pending_observation_.peak[channel] =
        pending_observation_.peak[channel] > peak ? pending_observation_.peak[channel] : peak;
    pending_observation_.energy[channel] += energy;
    pending_observation_.last_trigger_us = timestamp_us;
    pending_observation_.duration_us =
        timestamp_us - pending_observation_.first_trigger_us;
    if (!waveform_ref.empty()) {
        pending_observation_.waveform_ref = waveform_ref;
    }
    return completed;
}

std::optional<PiezoObservation> PiezoCapture::poll(
    const std::uint64_t timestamp_us) {
    if (!pending_ || timestamp_us < pending_observation_.last_trigger_us ||
        timestamp_us - pending_observation_.last_trigger_us < merge_window_us_) {
        return std::nullopt;
    }
    return finish();
}

std::optional<PiezoObservation> PiezoCapture::finish() {
    if (!pending_) {
        return std::nullopt;
    }
    auto result = pending_observation_;
    reset();
    return result;
}

void PiezoCapture::reset() {
    pending_ = false;
    pending_observation_ = PiezoObservation{};
}

}  // namespace smartgear
