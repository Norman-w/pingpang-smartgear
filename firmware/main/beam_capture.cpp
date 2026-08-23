#include "beam_capture.h"

#include "net_sensor_config.h"

namespace smartgear {

BeamCapture::BeamCapture(const std::uint64_t quiet_us,
                         const std::uint64_t max_event_us)
    : quiet_us_(quiet_us), max_event_us_(max_event_us) {}

std::optional<BeamObservation> BeamCapture::on_edge(
    const std::uint8_t channel,
    const bool blocked,
    const std::uint64_t timestamp_us) {
    if (channel >= config::kBeamCount) {
        return std::nullopt;
    }

    const bool timestamp_in_order = !active_ || timestamp_us >= last_change_us_;
    if (!timestamp_in_order) {
        // GPIO ISR delivery is expected to be FIFO, but a board adapter or
        // replay source can violate that assumption. Keep the boundary
        // recoverable while making the eventual observation invalid.
        timestamp_order_valid_ = false;
    }

    if (active_ && timestamp_us >= start_us_ &&
        timestamp_us - start_us_ > max_event_us_) {
        auto timed_out = finish(timestamp_us, true);
        // 当前边沿属于下一段输入，继续处理而不是丢掉它。
        if (blocked) {
            active_ = true;
            start_us_ = timestamp_us;
            last_change_us_ = timestamp_us;
            active_mask_ = static_cast<std::uint16_t>(1U << channel);
            latched_mask_ = active_mask_;
        }
        return timed_out;
    }

    const std::uint16_t bit = static_cast<std::uint16_t>(1U << channel);
    if (blocked) {
        if (!active_) {
            active_ = true;
            start_us_ = timestamp_us;
            latched_mask_ = 0;
        }
        active_mask_ = static_cast<std::uint16_t>(active_mask_ | bit);
        latched_mask_ = static_cast<std::uint16_t>(latched_mask_ | bit);
    } else if (active_) {
        active_mask_ = static_cast<std::uint16_t>(active_mask_ & ~bit);
    }
    if (timestamp_in_order) {
        last_change_us_ = timestamp_us;
    }
    return std::nullopt;
}

std::optional<BeamObservation> BeamCapture::poll(
    const std::uint64_t timestamp_us) {
    if (!active_) {
        return std::nullopt;
    }
    if (timestamp_us >= start_us_ && timestamp_us - start_us_ > max_event_us_) {
        return finish(timestamp_us, true);
    }
    if (active_mask_ == 0 && timestamp_us >= last_change_us_ &&
        timestamp_us - last_change_us_ >= quiet_us_) {
        return finish(timestamp_us, false);
    }
    return std::nullopt;
}

std::optional<BeamObservation> BeamCapture::finish(
    const std::uint64_t timestamp_us,
    const bool timed_out) {
    if (!active_) {
        return std::nullopt;
    }

    BeamObservation observation;
    observation.valid = latched_mask_ != 0 && timestamp_us >= start_us_ &&
                        timestamp_order_valid_;
    observation.timed_out = timed_out;
    observation.start_us = start_us_;
    observation.end_us = timestamp_us;
    observation.beam_mask = latched_mask_;

    if (observation.valid) {
        bool found = false;
        for (std::uint8_t index = 0; index < config::kBeamCount; ++index) {
            if ((latched_mask_ & (1U << index)) != 0U) {
                if (!found) {
                    observation.min_index = index;
                    found = true;
                }
                observation.max_index = index;
            }
        }
    }

    reset();
    return observation;
}

void BeamCapture::reset() {
    active_ = false;
    active_mask_ = 0;
    latched_mask_ = 0;
    start_us_ = 0;
    last_change_us_ = 0;
    timestamp_order_valid_ = true;
}

}  // namespace smartgear
