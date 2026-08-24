#include "piezo_capture.h"

#include <cmath>

namespace {

bool finite_nonnegative(const float value) {
    return std::isfinite(value) && value >= 0.0F;
}

}  // namespace

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

    const bool timestamp_in_order =
        !stream_has_timestamp_ || timestamp_us >= stream_last_timestamp_us_;
    if (!timestamp_in_order) {
        if (pending_) {
            // A comparator edge older than the last observed stream boundary
            // cannot be assigned to the current candidate or a new one.
            pending_observation_.valid = false;
            return std::nullopt;
        }
    } else if (!stream_has_timestamp_ ||
               timestamp_us > stream_last_timestamp_us_) {
        stream_last_timestamp_us_ = timestamp_us;
        stream_has_timestamp_ = true;
    }

    const bool trigger_features_valid = finite_nonnegative(peak) &&
                                        finite_nonnegative(energy);

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
        pending_observation_.valid = timestamp_in_order;
        pending_observation_.triggered = true;
        pending_observation_.first_trigger_us = timestamp_us;
        // A comparator edge is only a candidate. Without a non-empty frame
        // reference there is no ADC evidence that can make the observation
        // complete, even if an adapter supplied placeholder peak/energy.
        pending_observation_.features_ready = false;
    }

    pending_observation_.sensor_mask = static_cast<std::uint8_t>(
        pending_observation_.sensor_mask | static_cast<std::uint8_t>(1U << channel));
    if (!trigger_features_valid) {
        pending_observation_.valid = false;
    }
    if (!pending_observation_.features_ready) {
        pending_observation_.peak[channel] =
            pending_observation_.peak[channel] > peak || !trigger_features_valid
                ? pending_observation_.peak[channel]
                : peak;
        if (trigger_features_valid) {
            pending_observation_.energy[channel] += energy;
        }
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
    const bool features_valid = finite_nonnegative(features.peak[0]) &&
                                finite_nonnegative(features.peak[1]) &&
                                finite_nonnegative(features.energy[0]) &&
                                finite_nonnegative(features.energy[1]);
    if (!features_valid) {
        pending_observation_.peak = {0.0F, 0.0F};
        pending_observation_.energy = {0.0F, 0.0F};
        pending_observation_.duration_us = 0;
        pending_observation_.valid = false;
        pending_observation_.features_ready = false;
        return;
    }
    pending_observation_.peak = features.peak;
    pending_observation_.energy = features.energy;
    pending_observation_.duration_us = features.duration_us;
    pending_observation_.features_ready = features.complete;
}

bool PiezoCapture::will_start_new_observation(
    const std::uint64_t timestamp_us) const {
    if (stream_has_timestamp_ && timestamp_us < stream_last_timestamp_us_) {
        return false;
    }
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
    if (stream_has_timestamp_ && timestamp_us < stream_last_timestamp_us_) {
        if (pending_) {
            pending_observation_.valid = false;
        }
        return std::nullopt;
    }
    if (!stream_has_timestamp_ || timestamp_us > stream_last_timestamp_us_) {
        stream_last_timestamp_us_ = timestamp_us;
        stream_has_timestamp_ = true;
    }
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
