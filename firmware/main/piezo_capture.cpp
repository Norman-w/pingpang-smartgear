#include "piezo_capture.h"

namespace smartgear {

PiezoCapture::PiezoCapture(const std::uint64_t merge_window_us,
                           const std::uint64_t waveform_timeout_us)
    : merge_window_us_(merge_window_us), waveform_timeout_us_(waveform_timeout_us) {}

std::optional<PiezoObservation> PiezoCapture::on_trigger(
    const std::uint8_t channel,
    const std::uint64_t timestamp_us,
    const float peak,
    const float energy,
    const std::string& waveform_ref) {
    if (channel >= 2) {
        return std::nullopt;
    }

    if (pending_ && timestamp_us < pending_observation_.last_trigger_us) {
        // ISR delivery should be FIFO, but an adapter must not allow a late
        // timestamp to make duration arithmetic wrap around. Retain the
        // candidate and fail it closed when it is eventually emitted.
        pending_observation_.valid = false;
        return std::nullopt;
    }

    std::optional<PiezoObservation> completed;
    if (pending_ && timestamp_us >= pending_observation_.last_trigger_us &&
        timestamp_us - pending_observation_.last_trigger_us >= merge_window_us_ &&
        (pending_observation_.features_ready ||
         (timestamp_us >= pending_observation_.first_trigger_us &&
          timestamp_us - pending_observation_.first_trigger_us >=
              waveform_timeout_us_))) {
        completed = finish();
    }

    if (!pending_) {
        pending_ = true;
        pending_observation_ = PiezoObservation{};
        pending_observation_.valid = true;
        pending_observation_.triggered = true;
        pending_observation_.first_trigger_us = timestamp_us;
        pending_observation_.features_ready = waveform_ref.empty();
    }

    pending_observation_.sensor_mask = static_cast<std::uint8_t>(
        pending_observation_.sensor_mask | static_cast<std::uint8_t>(1U << channel));
    if (!pending_observation_.features_ready) {
        pending_observation_.peak[channel] =
            pending_observation_.peak[channel] > peak ? pending_observation_.peak[channel]
                                                       : peak;
        pending_observation_.energy[channel] += energy;
    }
    pending_observation_.last_trigger_us = timestamp_us;
    if (!pending_observation_.features_ready) {
        pending_observation_.duration_us =
            timestamp_us - pending_observation_.first_trigger_us;
    }
    if (!waveform_ref.empty()) {
        if (pending_observation_.waveform_ref.empty()) {
            pending_observation_.waveform_ref = waveform_ref;
            pending_observation_.features_ready = false;
        }
    }
    return completed;
}

void PiezoCapture::on_waveform_ready(const std::string& waveform_ref,
                                     const PiezoFeatureSummary& features) {
    if (!pending_ || waveform_ref.empty() ||
        pending_observation_.waveform_ref != waveform_ref) {
        return;
    }
    pending_observation_.peak = features.peak;
    pending_observation_.energy = features.energy;
    pending_observation_.duration_us = features.duration_us;
    pending_observation_.features_ready = features.complete;
}

bool PiezoCapture::will_start_new_observation(
    const std::uint64_t timestamp_us) const {
    if (!pending_) {
        return true;
    }
    if (timestamp_us < pending_observation_.last_trigger_us ||
        timestamp_us - pending_observation_.last_trigger_us < merge_window_us_) {
        return false;
    }
    return pending_observation_.features_ready ||
           (timestamp_us >= pending_observation_.first_trigger_us &&
            timestamp_us - pending_observation_.first_trigger_us >=
                waveform_timeout_us_);
}

std::optional<PiezoObservation> PiezoCapture::poll(
    const std::uint64_t timestamp_us) {
    if (!pending_ || timestamp_us < pending_observation_.last_trigger_us ||
        timestamp_us - pending_observation_.last_trigger_us < merge_window_us_ ||
        (!pending_observation_.features_ready &&
         (timestamp_us < pending_observation_.first_trigger_us ||
          timestamp_us - pending_observation_.first_trigger_us <
              waveform_timeout_us_))) {
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
