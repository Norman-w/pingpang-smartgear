#include "net_event_aggregator.h"

#include <algorithm>
#include <cinttypes>
#include <cstdio>
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

std::string make_event_id(const std::uint64_t timestamp_us,
                          const std::uint32_t sequence) {
    char buffer[64] = {};
    // 采用稳定的 UUID-like opaque ID；联网层可在外层替换为正式 UUID。
    std::snprintf(buffer,
                  sizeof(buffer),
                  "%08" PRIx32 "-%04" PRIx16 "-4000-8000-%012" PRIx64,
                  sequence,
                  static_cast<std::uint16_t>(sequence & 0xffffU),
                  timestamp_us & 0xffffffffffffULL);
    return buffer;
}

}  // namespace

NetEventAggregator::NetEventAggregator(NetEventAggregatorConfig config)
    : config_(config) {}

void NetEventAggregator::set_calibration(std::string calibration_id,
                                         const bool valid) {
    calibration_id_ = calibration_id.empty() ? "uncalibrated" : std::move(calibration_id);
    calibration_valid_ = valid;
}

void NetEventAggregator::set_beam_health(const std::uint16_t healthy_mask,
                                         const bool valid) {
    beam_healthy_mask_ = healthy_mask;
    beam_health_valid_ = valid;
    beam_health_configured_ = true;
}

void NetEventAggregator::set_piezo_baseline(const bool valid) {
    piezo_baseline_valid_ = valid;
    piezo_baseline_configured_ = true;
}

bool NetEventAggregator::touch_matches_beam(const PiezoObservation& touch,
                                            const BeamObservation& beam) const {
    if (!touch.valid || !beam.valid || touch.last_trigger_us < beam.start_us) {
        if (!touch.valid || !beam.valid) {
            return false;
        }
        // touch 在 beam 前时，下面的无符号减法不适用，单独处理。
        return beam.start_us - touch.last_trigger_us <=
               config_.touch_association_before_us;
    }
    return touch.first_trigger_us <=
               beam.end_us + config_.touch_association_after_us &&
           touch.last_trigger_us + config_.touch_association_before_us >=
               beam.start_us;
}

NetEvent NetEventAggregator::build_event(
    const std::optional<BeamObservation>& beam,
    const std::optional<PiezoObservation>& touch,
    const NetState state,
    std::string extra_quality_flag) const {
    NetEvent event;
    event.event_id = make_event_id(
        beam ? beam->start_us : (touch ? touch->first_trigger_us : 0),
        event_sequence_ + 1);
    event.timestamp_us =
        beam ? beam->start_us : (touch ? touch->first_trigger_us : 0);
    event.calibration_id = calibration_id_;
    event.state = calibration_valid_ ? state : NetState::kUnknown;

    if (beam && beam->valid) {
        event.beam_mask = beam->beam_mask;
        const int low = config::kBeamFirstHeightMm +
                        static_cast<int>(beam->min_index) * config::kBeamPitchMm;
        const int high = config::kBeamFirstHeightMm +
                         static_cast<int>(beam->max_index) * config::kBeamPitchMm;
        event.beam_height_mm = {low, high};
        event.ball_bottom_gap_mm = {
            std::max(0, low - config::kBeamPitchMm), low};
    }

    if (touch) {
        event.net_touch.triggered = touch->triggered;
        event.net_touch.sensor_mask = touch->sensor_mask;
        event.net_touch.peak = touch->peak;
        event.net_touch.energy = touch->energy;
        event.net_touch.duration_us = touch->duration_us;
        event.net_touch.waveform_ref = touch->waveform_ref;
    }

    if (!beam) {
        add_quality_flag(event, "no_beam");
    }
    if (beam && beam->timed_out) {
        add_quality_flag(event, "beam_event_timeout");
    }
    if (beam && !beam->valid) {
        add_quality_flag(event, "beam_invalid");
    }
    if (touch && !touch->valid) {
        add_quality_flag(event, "touch_invalid");
    }
    if (touch && !touch->features_ready) {
        add_quality_flag(event, "waveform_incomplete");
    }
    if (beam && beam->valid && beam_health_configured_) {
        if (!beam_health_valid_) {
            add_quality_flag(event, "beam_self_test_invalid");
        }
        if (beam_health_valid_) {
            const auto unhealthy_hits = static_cast<std::uint16_t>(
                beam->beam_mask & static_cast<std::uint16_t>(~beam_healthy_mask_));
            if (unhealthy_hits != 0) {
                add_quality_flag(event, "beam_channel_unhealthy");
            }
        }
    }
    if (touch && touch->triggered && piezo_baseline_configured_ &&
        !piezo_baseline_valid_) {
        add_quality_flag(event, "piezo_baseline_invalid");
    }
    if (!calibration_valid_) {
        add_quality_flag(event, "calibration_invalid");
    }
    add_quality_flag(event, std::move(extra_quality_flag));
    return event;
}

void NetEventAggregator::on_beam(const BeamObservation& observation) {
    if (!observation.valid) {
        output_.push_back(build_event(observation, std::nullopt, NetState::kUnknown,
                                      "beam_boundary_unknown"));
        ++event_sequence_;
        return;
    }

    // 首版明确不处理重叠多球：已有未完成边界时，先标为 unknown，再接收新事件。
    if (pending_beam_) {
        emit_pending_beam(NetState::kUnknown);
        clear_pending();
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
        clear_pending();
    }

    pending_beam_ = observation;
    pending_beam_deadline_us_ =
        observation.end_us + config_.touch_association_after_us;
}

void NetEventAggregator::on_touch(const PiezoObservation& observation) {
    if (!observation.valid || !observation.triggered) {
        output_.push_back(build_event(std::nullopt, observation, NetState::kUnknown,
                                      "touch_boundary_unknown"));
        ++event_sequence_;
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
            clear_pending();
        }
    }

    if (pending_touch_) {
        emit_pending_touch(NetState::kTouchNoCross);
        clear_pending();
    }

    pending_touch_ = observation;
    pending_touch_deadline_us_ =
        observation.last_trigger_us + config_.touch_only_timeout_us;
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

void NetEventAggregator::emit_pending_beam(const NetState state) {
    if (!pending_beam_) {
        return;
    }
    const std::optional<PiezoObservation> touch_for_beam =
        state == NetState::kCleanOver ? std::nullopt : pending_touch_;
    output_.push_back(build_event(pending_beam_, touch_for_beam, state));
    ++event_sequence_;
}

void NetEventAggregator::emit_pending_touch(const NetState state) {
    if (!pending_touch_) {
        return;
    }
    output_.push_back(build_event(std::nullopt, pending_touch_, state));
    ++event_sequence_;
}

void NetEventAggregator::clear_pending() {
    clear_beam_pending();
    clear_touch_pending();
}

void NetEventAggregator::clear_beam_pending() {
    pending_beam_.reset();
    pending_beam_deadline_us_ = 0;
}

void NetEventAggregator::clear_touch_pending() {
    pending_touch_.reset();
    pending_touch_deadline_us_ = 0;
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
