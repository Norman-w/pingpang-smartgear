#include "net_event_aggregator.h"

#include <algorithm>
#include <cmath>
#include <cinttypes>
#include <cstdio>
#include <limits>
#include <utility>

#include "net_sensor_config.h"

namespace smartgear {
namespace {

void add_quality_flag(NetEvent& event, const std::string& flag) {
    if (flag.empty()) {
        return;
    }
    if (std::find(event.quality_flags.begin(), event.quality_flags.end(), flag) ==
        event.quality_flags.end()) {
        event.quality_flags.push_back(flag);
    }
}

std::uint64_t saturating_add(const std::uint64_t left,
                             const std::uint64_t right) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return left + right;
}

bool beam_shape_is_valid(const BeamObservation& beam) {
    if (!beam.valid || beam.beam_mask == 0 ||
        (beam.beam_mask & static_cast<std::uint16_t>(~config::kAllBeamMask)) !=
            0 ||
        beam.end_us < beam.start_us ||
        beam.min_index >= config::kBeamCount ||
        beam.max_index >= config::kBeamCount || beam.min_index > beam.max_index) {
        return false;
    }
    const auto min_bit = static_cast<std::uint16_t>(1U << beam.min_index);
    const auto max_bit = static_cast<std::uint16_t>(1U << beam.max_index);
    return (beam.beam_mask & min_bit) != 0 && (beam.beam_mask & max_bit) != 0;
}

bool touch_shape_is_valid(const PiezoObservation& touch) {
    if (!touch.valid || !touch.triggered || touch.sensor_mask == 0 ||
        touch.sensor_mask > 0x03U ||
        touch.first_trigger_us > touch.last_trigger_us) {
        return false;
    }
    for (const float value : touch.peak) {
        if (!std::isfinite(value) || value < 0.0F) {
            return false;
        }
    }
    for (const float value : touch.energy) {
        if (!std::isfinite(value) || value < 0.0F) {
            return false;
        }
    }
    return !touch.features_ready || !touch.waveform_ref.empty();
}

std::string make_event_id(const std::uint64_t timestamp_us,
                          const std::uint32_t sequence) {
    char buffer[64] = {};
    // 采用稳定的 UUID-like opaque ID；联网层可在外层替换为正式 UUID。
    std::snprintf(buffer,
                  sizeof(buffer),
                  "%08" PRIx32 "-%04" PRIx16 "-4000-8000-%012" PRIx64,
                  sequence,
                  static_cast<std::uint16_t>(sequence & 0xffffU),
                  static_cast<std::uint64_t>(timestamp_us & UINT64_C(0xffffffffffff)));
    return buffer;
}

}  // namespace

NetEventAggregator::NetEventAggregator(NetEventAggregatorConfig config)
    : config_(config) {}

bool NetEventAggregator::observe_input_timestamp(const std::uint64_t timestamp_us,
                                                 const bool beam_stream) {
    auto& last_timestamp = beam_stream ? last_beam_input_timestamp_us_
                                       : last_touch_input_timestamp_us_;
    auto& has_timestamp = beam_stream ? has_beam_input_timestamp_
                                      : has_touch_input_timestamp_;
    if (has_timestamp && timestamp_us < last_timestamp) {
        return false;
    }
    if (!has_timestamp || timestamp_us > last_timestamp) {
        last_timestamp = timestamp_us;
        has_timestamp = true;
    }
    return true;
}

void NetEventAggregator::set_calibration(std::string calibration_id,
                                         const bool valid) {
    const bool has_id = !calibration_id.empty();
    std::string next_calibration_id =
        has_id ? std::move(calibration_id) : "uncalibrated";
    // A board hook may report an otherwise successful snapshot with an empty
    // ID. Keep the value serializable, but never let that malformed snapshot
    // authorize a clean/touch conclusion.
    const bool next_calibration_valid = valid && has_id;
    if (calibration_id_ != next_calibration_id ||
        calibration_valid_ != next_calibration_valid) {
        if (pending_beam_ || pending_touch_) {
            health_changed_while_pending_ = true;
        }
    }
    calibration_id_ = std::move(next_calibration_id);
    calibration_valid_ = next_calibration_valid;
}

void NetEventAggregator::set_beam_health(const std::uint16_t healthy_mask,
                                         const bool valid) {
    // Do not rely solely on the board hook's validator. This public business
    // boundary is also used by replay/integration adapters and must fail
    // closed when an out-of-range bit is injected directly.
    const bool next_beam_health_valid =
        valid && (healthy_mask & static_cast<std::uint16_t>(~config::kAllBeamMask)) == 0;
    if (beam_healthy_mask_ != healthy_mask ||
        beam_health_valid_ != next_beam_health_valid ||
        !beam_health_configured_) {
        if (pending_beam_ || pending_touch_) {
            health_changed_while_pending_ = true;
        }
    }
    beam_healthy_mask_ = healthy_mask;
    beam_health_valid_ = next_beam_health_valid;
    beam_health_configured_ = true;
}

void NetEventAggregator::set_piezo_baseline(const bool valid) {
    if (!piezo_baseline_configured_ || piezo_baseline_valid_ != valid) {
        if (pending_beam_ || pending_touch_) {
            health_changed_while_pending_ = true;
        }
    }
    piezo_baseline_valid_ = valid;
    piezo_baseline_configured_ = true;
}

void NetEventAggregator::mark_input_overflow() {
    // The capture objects are reset by the ESP32 task at the same boundary.
    // Do not retain a beam/touch candidate from before the dropped GPIO edge;
    // otherwise the first post-overflow input could be paired with stale
    // timestamps and look like a plausible event. The overflow latch is kept
    // for the next fresh event and is cleared only when that event is built.
    clear_pending();
    input_overflow_ = true;
}

bool NetEventAggregator::touch_matches_beam(const PiezoObservation& touch,
                                            const BeamObservation& beam) const {
    if (!touch_shape_is_valid(touch) || !beam_shape_is_valid(beam) ||
        touch.last_trigger_us < beam.start_us) {
        if (!touch_shape_is_valid(touch) || !beam_shape_is_valid(beam)) {
            return false;
        }
        // touch 在 beam 前时，下面的无符号减法不适用，单独处理。
        return beam.start_us - touch.last_trigger_us <=
               config_.touch_association_before_us;
    }
    return touch.first_trigger_us <=
               saturating_add(beam.end_us, config_.touch_association_after_us) &&
           saturating_add(touch.last_trigger_us,
                          config_.touch_association_before_us) >= beam.start_us;
}

NetEvent NetEventAggregator::build_event(
    const std::optional<BeamObservation>& beam,
    const std::optional<PiezoObservation>& touch,
    const NetState state,
    std::string extra_quality_flag) {
    NetEvent event;
    event.event_id = make_event_id(
        beam ? beam->start_us : (touch ? touch->first_trigger_us : 0),
        event_sequence_ + 1);
    event.timestamp_us =
        beam ? beam->start_us : (touch ? touch->first_trigger_us : 0);
    event.calibration_id = calibration_id_;
    bool state_quality_valid = calibration_valid_;

    if (beam && beam->valid && beam_shape_is_valid(*beam)) {
        event.beam_mask = beam->beam_mask;
        const int low = config::kBeamFirstHeightMm +
                        static_cast<int>(beam->min_index) * config::kBeamPitchMm;
        const int high = config::kBeamFirstHeightMm +
                         static_cast<int>(beam->max_index) * config::kBeamPitchMm;
        event.beam_height_mm = {low, high};
        event.ball_bottom_gap_mm = {
            std::max(0, low - config::kBeamPitchMm), low};
    } else if (beam && beam->valid) {
        add_quality_flag(event, "beam_shape_invalid");
        state_quality_valid = false;
    }

    if (touch) {
        const bool touch_shape_valid = touch_shape_is_valid(*touch);
        event.net_touch.triggered = touch_shape_valid && touch->triggered;
        event.net_touch.sensor_mask = touch_shape_valid ? touch->sensor_mask : 0;
        event.net_touch.peak = touch->peak;
        event.net_touch.energy = touch->energy;
        event.net_touch.duration_us = touch->duration_us;
        event.net_touch.waveform_ref = touch->waveform_ref;
        if (!touch_shape_valid && touch->valid) {
            add_quality_flag(event, "touch_shape_invalid");
            state_quality_valid = false;
        }
    }

    if (!beam) {
        add_quality_flag(event, "no_beam");
    }
    if (beam && beam->timed_out) {
        add_quality_flag(event, "beam_event_timeout");
        state_quality_valid = false;
    }
    if (beam && !beam->valid) {
        add_quality_flag(event, "beam_invalid");
        state_quality_valid = false;
    }
    if (touch && !touch->valid) {
        add_quality_flag(event, "touch_invalid");
        state_quality_valid = false;
    }
    if (touch && !touch->features_ready) {
        add_quality_flag(event, "waveform_incomplete");
        state_quality_valid = false;
    }
    if (beam_health_configured_) {
        if (!beam_health_valid_) {
            add_quality_flag(event, "beam_self_test_invalid");
            state_quality_valid = false;
        }
        if (beam && beam_shape_is_valid(*beam) && beam_health_valid_) {
            const auto unhealthy_hits = static_cast<std::uint16_t>(
                beam->beam_mask & static_cast<std::uint16_t>(~beam_healthy_mask_));
            if (unhealthy_hits != 0) {
                add_quality_flag(event, "beam_channel_unhealthy");
                state_quality_valid = false;
            }
        }
    }
    if (touch && touch_shape_is_valid(*touch) && piezo_baseline_configured_ &&
        !piezo_baseline_valid_) {
        add_quality_flag(event, "piezo_baseline_invalid");
        state_quality_valid = false;
    }
    if (!calibration_valid_) {
        add_quality_flag(event, "calibration_invalid");
    }
    if (input_overflow_) {
        add_quality_flag(event, "sensor_queue_overflow");
        state_quality_valid = false;
    }
    if (health_changed_while_pending_) {
        add_quality_flag(event, "sensor_health_changed_during_event");
        state_quality_valid = false;
    }
    event.state = state_quality_valid ? state : NetState::kUnknown;
    add_quality_flag(event, std::move(extra_quality_flag));
    input_overflow_ = false;
    return event;
}

void NetEventAggregator::on_beam(const BeamObservation& observation) {
    if (!observation.valid) {
        if (pending_beam_) {
            emit_pending_beam(NetState::kUnknown,
                              "pending_beam_boundary_unknown");
            clear_beam_pending();
            // emit_pending_beam() includes a pending touch in the same
            // fail-closed event when one exists.
            clear_touch_pending();
        } else if (pending_touch_) {
            emit_pending_touch(NetState::kUnknown,
                               "pending_touch_boundary_unknown");
            clear_touch_pending();
        }
        output_.push_back(build_event(observation, std::nullopt, NetState::kUnknown,
                                      "beam_boundary_unknown"));
        ++event_sequence_;
        return;
    }
    if (!beam_shape_is_valid(observation)) {
        if (pending_beam_) {
            emit_pending_beam(NetState::kUnknown,
                              "pending_beam_shape_unknown");
            clear_beam_pending();
            clear_touch_pending();
        } else if (pending_touch_) {
            emit_pending_touch(NetState::kUnknown,
                               "pending_touch_shape_unknown");
            clear_touch_pending();
        }
        output_.push_back(build_event(observation, std::nullopt,
                                      NetState::kUnknown,
                                      "beam_shape_invalid"));
        ++event_sequence_;
        return;
    }

    // Compare event starts, not ends: two ball paths may overlap in time and
    // still arrive with monotonically increasing start boundaries.
    if (!observe_input_timestamp(observation.start_us, true)) {
        auto out_of_order = observation;
        out_of_order.valid = false;
        on_beam(out_of_order);
        return;
    }

    // 首版明确不处理重叠多球：已有未完成边界时，先标为 unknown，再接收新事件。
    if (pending_beam_) {
        emit_pending_beam(NetState::kUnknown);
        clear_beam_pending();
        if (pending_touch_) {
            // The touch candidate cannot be safely assigned to either
            // overlapping beam boundary. Preserve it as its own no-cross
            // record instead of dropping it with the old beam.
            emit_pending_touch(NetState::kTouchNoCross);
            clear_touch_pending();
        }
    }

    if (pending_touch_) {
        if (touch_matches_beam(*pending_touch_, observation)) {
            output_.push_back(build_event(observation, pending_touch_,
                                          NetState::kTouchOver));
            ++event_sequence_;
            clear_pending();
            return;
        }
        emit_pending_touch(NetState::kTouchNoCross);
        clear_touch_pending();
    }

    pending_beam_ = observation;
    pending_beam_deadline_us_ =
        saturating_add(
            saturating_add(observation.end_us,
                           config_.touch_association_after_us),
            config_.touch_completion_grace_us);
}

void NetEventAggregator::on_touch(const PiezoObservation& observation) {
    if (!observation.valid || !observation.triggered) {
        output_.push_back(build_event(std::nullopt, observation, NetState::kUnknown,
                                      "touch_boundary_unknown"));
        ++event_sequence_;
        return;
    }
    if (!touch_shape_is_valid(observation)) {
        output_.push_back(build_event(std::nullopt, observation,
                                      NetState::kUnknown,
                                      "touch_shape_invalid"));
        ++event_sequence_;
        return;
    }

    if (!observe_input_timestamp(observation.first_trigger_us, false)) {
        auto out_of_order = observation;
        out_of_order.valid = false;
        on_touch(out_of_order);
        return;
    }

    if (pending_beam_) {
        if (touch_matches_beam(observation, *pending_beam_)) {
            output_.push_back(build_event(pending_beam_, observation,
                                          NetState::kTouchOver));
            ++event_sequence_;
            clear_pending();
            return;
        }
        if (observation.first_trigger_us > pending_beam_deadline_us_) {
            emit_pending_beam(NetState::kCleanOver);
            clear_beam_pending();
        }
    }

    if (pending_touch_) {
        emit_pending_touch(NetState::kTouchNoCross);
        clear_touch_pending();
    }

    pending_touch_ = observation;
    pending_touch_deadline_us_ =
        saturating_add(observation.last_trigger_us,
                       config_.touch_only_timeout_us);
}

void NetEventAggregator::poll(const std::uint64_t timestamp_us) {
    if (pending_beam_ && timestamp_us >= pending_beam_deadline_us_) {
        emit_pending_beam(NetState::kCleanOver);
        // 未匹配的 PVDF 候选仍然要有机会在自己的超时点生成
        // touch_no_cross，不能被 clean_over 一起清掉。
        clear_beam_pending();
    }
    if (pending_touch_ && timestamp_us >= pending_touch_deadline_us_) {
        emit_pending_touch(NetState::kTouchNoCross);
        clear_touch_pending();
    }
}

void NetEventAggregator::emit_pending_beam(const NetState state,
                                           std::string extra_quality_flag) {
    if (!pending_beam_) {
        return;
    }
    const std::optional<PiezoObservation> touch_for_beam =
        state == NetState::kCleanOver ? std::nullopt : pending_touch_;
    output_.push_back(build_event(pending_beam_, touch_for_beam, state,
                                  std::move(extra_quality_flag)));
    ++event_sequence_;
}

void NetEventAggregator::emit_pending_touch(const NetState state,
                                            std::string extra_quality_flag) {
    if (!pending_touch_) {
        return;
    }
    output_.push_back(build_event(std::nullopt, pending_touch_, state,
                                  std::move(extra_quality_flag)));
    ++event_sequence_;
}

void NetEventAggregator::clear_pending() {
    clear_beam_pending();
    clear_touch_pending();
    clear_health_change_if_idle();
}

void NetEventAggregator::clear_beam_pending() {
    pending_beam_.reset();
    pending_beam_deadline_us_ = 0;
    clear_health_change_if_idle();
}

void NetEventAggregator::clear_touch_pending() {
    pending_touch_.reset();
    pending_touch_deadline_us_ = 0;
    clear_health_change_if_idle();
}

void NetEventAggregator::clear_health_change_if_idle() {
    if (!pending_beam_ && !pending_touch_) {
        health_changed_while_pending_ = false;
    }
}

bool NetEventAggregator::pop_event(NetEvent& event) {
    if (output_.empty()) {
        return false;
    }
    event = std::move(output_.front());
    output_.pop_front();
    return true;
}

}  // namespace smartgear
