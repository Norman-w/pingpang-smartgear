#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

#include "beam_capture.h"
#include "feedback.h"
#include "net_event.h"
#include "net_event_aggregator.h"
#include "net_event_delivery.h"
#include "piezo_capture.h"
#include "piezo_waveform_archive.h"
#include "piezo_waveform_hook.h"
#include "piezo_waveform.h"
#include "ring_buffer.h"
#include "net_sensor_config.h"
#include "sensor_health_gate.h"
#include "sensor_self_test.h"

namespace {

bool g_waveform_hook_called = false;
bool g_waveform_hook_complete = false;
std::size_t g_waveform_hook_left_count = 0;
std::size_t g_waveform_hook_right_count = 0;

}  // namespace

extern "C" bool smartgear_board_on_piezo_waveform(
    const char* reference,
    const std::uint64_t trigger_us,
    const std::size_t pre_trigger_samples,
    const std::int16_t* left_samples,
    const std::size_t left_count,
    const std::int16_t* right_samples,
    const std::size_t right_count,
    const bool complete) {
    g_waveform_hook_called = reference != nullptr && trigger_us == 1234 &&
                             pre_trigger_samples == 2 && left_samples != nullptr &&
                             right_samples != nullptr;
    g_waveform_hook_left_count = left_count;
    g_waveform_hook_right_count = right_count;
    g_waveform_hook_complete = complete;
    return g_waveform_hook_called;
}

namespace {

void require(const bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

smartgear::BeamObservation beam(std::uint64_t start,
                                std::uint64_t end,
                                std::uint16_t mask,
                                std::uint8_t min_index,
                                std::uint8_t max_index) {
    smartgear::BeamObservation result;
    result.valid = true;
    result.start_us = start;
    result.end_us = end;
    result.beam_mask = mask;
    result.min_index = min_index;
    result.max_index = max_index;
    return result;
}

smartgear::PiezoObservation touch(std::uint64_t first,
                                   std::uint64_t last,
                                   std::uint8_t sensor_mask) {
    smartgear::PiezoObservation result;
    result.valid = true;
    result.triggered = true;
    result.sensor_mask = sensor_mask;
    result.first_trigger_us = first;
    result.last_trigger_us = last;
    result.duration_us = last - first;
    result.peak = {1.5F, 2.5F};
    result.energy = {3.0F, 4.0F};
    result.waveform_ref = "wave-test-1";
    result.features_ready = true;
    return result;
}

bool has_quality_flag(const smartgear::NetEvent& event, const std::string& flag) {
    for (const auto& value : event.quality_flags) {
        if (value == flag) {
            return true;
        }
    }
    return false;
}

smartgear::NetEvent pop_one(smartgear::NetEventAggregator& aggregator) {
    smartgear::NetEvent event;
    require(aggregator.pop_event(event), "expected one NetEvent");
    require(aggregator.pending_output_count() == 0,
            "expected the output queue to be drained; remaining=" +
                std::to_string(aggregator.pending_output_count()) +
                " first_state=" + smartgear::net_state_name(event.state) +
                " first_timestamp=" + std::to_string(event.timestamp_us));
    return event;
}

void test_beam_capture() {
    smartgear::BeamCapture capture(5, 1'000);
    require(!capture.on_edge(0, true, 100), "first beam edge must not finish");
    capture.on_edge(3, true, 110);
    capture.on_edge(0, false, 120);
    capture.on_edge(3, false, 130);
    require(!capture.poll(134), "quiet interval is not complete");
    auto observation = capture.poll(135);
    require(observation.has_value(), "beam event should finish after quiet interval");
    require(observation->beam_mask == 0b0000001001,
            "beam mask must preserve both hit channels");
    require(observation->min_index == 0 && observation->max_index == 3,
            "beam min/max indices are wrong");
    require(!observation->timed_out, "short beam event must not time out");

    smartgear::BeamCapture timeout(5, 100);
    timeout.on_edge(1, true, 1'000);
    const auto timed_out = timeout.poll(1'101);
    require(timed_out.has_value() && timed_out->timed_out,
            "an overlong beam boundary must be explicitly timed out");

    smartgear::BeamCapture out_of_order(5, 1'000);
    out_of_order.on_edge(0, true, 2'000);
    out_of_order.on_edge(0, false, 1'900);
    const auto invalid_order = out_of_order.poll(3'001);
    require(invalid_order.has_value() && !invalid_order->valid,
            "out-of-order beam timestamps must fail closed");

    smartgear::BeamCapture late_after_boundary(5, 1'000);
    late_after_boundary.on_edge(0, true, 4'000);
    late_after_boundary.on_edge(0, false, 4'010);
    const auto first_boundary = late_after_boundary.poll(4'015);
    require(first_boundary.has_value() && first_boundary->valid,
            "ordered beam boundary should remain valid before late input");
    late_after_boundary.on_edge(0, true, 3'000);
    late_after_boundary.on_edge(0, false, 3'010);
    const auto late_boundary = late_after_boundary.poll(3'015);
    require(late_boundary.has_value() && !late_boundary->valid,
            "a late beam edge after a closed boundary must be invalid");
}

void test_each_beam_channel_independently() {
    for (std::uint8_t channel = 0; channel < smartgear::config::kBeamCount;
         ++channel) {
        smartgear::BeamCapture capture(5, 1'000);
        capture.on_edge(channel, true, 100);
        capture.on_edge(channel, false, 110);
        auto observation = capture.poll(115);
        require(observation.has_value(), "individual beam self-test event missing");
        require(observation->beam_mask == (1U << channel),
                "individual beam mask has a neighboring bit");
        require(observation->min_index == channel &&
                    observation->max_index == channel,
                "individual beam min/max index is wrong");
    }
    smartgear::BeamCapture out_of_range(5, 1'000);
    require(!out_of_range.on_edge(10, true, 100),
            "channel outside the +10..+100 window must be ignored");
    require(!out_of_range.poll(10'000),
            "outside-window input must not create an event");
}

void test_piezo_merge() {
    smartgear::PiezoCapture capture(5'000, 120'000);
    capture.on_trigger(0, 1'000, 1.0F, 2.0F, "wave-a");
    require(!capture.will_start_new_observation(3'000),
            "a trigger inside the merge window must reuse the current frame");
    capture.on_trigger(1, 3'000, 2.0F, 4.0F, "wave-a");
    smartgear::PiezoFeatureSummary features;
    features.peak = {1.5F, 2.5F};
    features.energy = {3.5F, 4.5F};
    features.duration_us = 4'000;
    features.complete = true;
    capture.on_waveform_ready("wave-a", features);
    capture.on_trigger(0, 4'000, 0.0F, 0.0F, "wave-a");
    auto result = capture.poll(9'001);
    require(result.has_value(), "PVDF event should close after merge window");
    require(result->sensor_mask == 3, "both PVDF channels must be retained");
    require(result->peak[0] == 1.5F && result->peak[1] == 2.5F,
            "PVDF waveform peak values were not retained");
    require(result->energy[0] == 3.5F && result->energy[1] == 4.5F,
            "PVDF waveform energy values were not retained");
    require(result->duration_us == 4'000 && result->features_ready,
            "PVDF waveform duration/readiness is wrong");

    smartgear::PiezoCapture timeout(5'000, 100'000);
    timeout.on_trigger(0, 10'000, 0.0F, 0.0F, "wave-timeout");
    require(!timeout.poll(109'999),
            "PVDF event must wait for merge window and waveform timeout");
    auto timed_out = timeout.poll(115'001);
    require(timed_out.has_value() && !timed_out->features_ready,
            "PVDF waveform timeout must preserve an incomplete quality state");
    require(timeout.will_start_new_observation(225'001),
            "a trigger after waveform timeout must start a new frame");

    smartgear::PiezoCapture no_waveform(5'000, 100'000);
    no_waveform.on_trigger(0, 10'000, 99.0F, 100.0F, "");
    const auto no_waveform_result = no_waveform.poll(115'001);
    require(no_waveform_result.has_value() &&
                !no_waveform_result->features_ready,
            "an empty waveform reference must remain incomplete evidence");

    smartgear::PiezoCapture invalid_features(5'000, 100'000);
    invalid_features.on_trigger(0, 20'000, 0.0F, 0.0F, "wave-invalid");
    smartgear::PiezoFeatureSummary invalid_summary;
    invalid_summary.peak[0] = std::numeric_limits<float>::quiet_NaN();
    invalid_summary.complete = true;
    invalid_features.on_waveform_ready("wave-invalid", invalid_summary);
    const auto invalid_feature_result = invalid_features.poll(125'001);
    require(invalid_feature_result.has_value() &&
                !invalid_feature_result->valid &&
                !invalid_feature_result->features_ready,
            "non-finite waveform features must fail closed");

    smartgear::PiezoCapture out_of_order(5'000, 20'000);
    out_of_order.on_trigger(0, 10'000, 0.0F, 0.0F, "wave-order");
    out_of_order.on_trigger(1, 9'000, 0.0F, 0.0F, "wave-order");
    const auto invalid_order = out_of_order.poll(35'001);
    require(invalid_order.has_value() && !invalid_order->valid,
            "out-of-order PVDF timestamps must fail closed");

    smartgear::PiezoCapture late_after_boundary(5'000, 5'000);
    late_after_boundary.on_trigger(0, 4'000, 0.0F, 0.0F, "wave-first-touch");
    smartgear::PiezoFeatureSummary first_features;
    first_features.peak = {1.0F, 0.0F};
    first_features.energy = {2.0F, 0.0F};
    first_features.complete = true;
    late_after_boundary.on_waveform_ready("wave-first-touch", first_features);
    require(late_after_boundary.poll(9'001).has_value(),
            "first PVDF boundary should close before testing late input");
    require(!late_after_boundary.will_start_new_observation(3'000),
            "late PVDF edge must not start a new valid observation");
    late_after_boundary.on_trigger(0, 3'000, 0.0F, 0.0F, "wave-late-touch");
    const auto late_touch = late_after_boundary.poll(14'001);
    require(late_touch.has_value() && !late_touch->valid,
            "a late PVDF edge after a closed boundary must be invalid");
}

void test_clean_over_and_height_interval() {
    smartgear::NetEventAggregator aggregator;
    aggregator.set_calibration("cal-test", true);
    aggregator.on_beam(beam(10'000, 11'000, 0b0000001001, 0, 3));
    aggregator.poll(256'001);
    const auto event = pop_one(aggregator);
    require(event.state == smartgear::NetState::kCleanOver,
            "beam-only event must be clean_over");
    require(event.beam_height_mm == std::array<int, 2>{10, 40},
            "height interval must use lowest/highest hit beam");
    require(event.ball_bottom_gap_mm == std::array<int, 2>{0, 10},
            "ball bottom gap must be derived from lowest beam");
    require(event.net_touch.sensor_mask == 0,
            "clean event must not report a PVDF sensor");
}

void test_every_beam_mask_interval() {
    for (std::uint16_t mask = 1; mask <= smartgear::config::kAllBeamMask;
         ++mask) {
        std::uint8_t min_index = 0;
        std::uint8_t max_index = 0;
        bool found = false;
        for (std::uint8_t index = 0; index < smartgear::config::kBeamCount;
             ++index) {
            if ((mask & (1U << index)) == 0) {
                continue;
            }
            if (!found) {
                min_index = index;
                found = true;
            }
            max_index = index;
        }

        smartgear::NetEventAggregator aggregator;
        aggregator.set_calibration("cal-mask", true);
        aggregator.on_beam(beam(1'000, 2'000, mask, min_index, max_index));
        aggregator.poll(300'000);
        const auto event = pop_one(aggregator);
        const int low = smartgear::config::kBeamFirstHeightMm +
                        static_cast<int>(min_index) *
                            smartgear::config::kBeamPitchMm;
        const int high = smartgear::config::kBeamFirstHeightMm +
                         static_cast<int>(max_index) *
                             smartgear::config::kBeamPitchMm;
        require(event.state == smartgear::NetState::kCleanOver &&
                    event.beam_mask == mask &&
                    event.beam_height_mm == std::array<int, 2>{low, high} &&
                    event.ball_bottom_gap_mm ==
                        std::array<int, 2>{std::max(0, low -
                                                           smartgear::config::kBeamPitchMm),
                                           low},
                "every nonzero beam mask must map to a stable height interval");
    }
}

void test_touch_over_before_and_after_beam() {
    smartgear::NetEventAggregator before;
    before.set_calibration("cal-test", true);
    before.on_touch(touch(9'000, 9'500, 1));
    before.on_beam(beam(10'000, 11'000, 1, 0, 0));
    const auto before_event = pop_one(before);
    require(before_event.state == smartgear::NetState::kTouchOver,
            "PVDF before beam should associate as touch_over");
    require(before_event.net_touch.sensor_mask == 1,
            "left PVDF mask must be preserved");

    smartgear::NetEventAggregator after;
    after.set_calibration("cal-test", true);
    after.on_beam(beam(20'000, 21'000, 1U << 4, 4, 4));
    after.on_touch(touch(21'500, 22'000, 2));
    const auto after_event = pop_one(after);
    require(after_event.state == smartgear::NetState::kTouchOver,
            "PVDF after beam should associate as touch_over");
    require(after_event.net_touch.sensor_mask == 2,
            "right PVDF mask must be preserved");

    smartgear::NetEventAggregator delayed({20'000, 120'000, 140'000,
                                           125'000});
    delayed.set_calibration("cal-test", true);
    delayed.on_beam(beam(100'000, 101'000, 1U << 1, 1, 1));
    // 先越过业务关联窗口，但仍处于 ADC/归并完成裕量内；晚到的 PVDF
    // 候选按自身 first_trigger_us 仍应关联到这次光栅事件。
    delayed.poll(221'001);
    require(delayed.pending_output_count() == 0,
            "beam must remain pending during waveform completion grace");
    delayed.on_touch(touch(220'000, 220'500, 1));
    const auto delayed_event = pop_one(delayed);
    require(delayed_event.state == smartgear::NetState::kTouchOver,
            "late waveform completion must still associate within touch window");
}

void test_touch_no_cross_and_unknown() {
    smartgear::NetEventAggregator no_cross;
    no_cross.set_calibration("cal-test", true);
    no_cross.on_touch(touch(30'000, 31'000, 1));
    no_cross.poll(171'001);
    const auto no_cross_event = pop_one(no_cross);
    require(no_cross_event.state == smartgear::NetState::kTouchNoCross,
            "PVDF without beam must become touch_no_cross");
    require(no_cross_event.beam_mask == 0,
            "touch_no_cross must have no beam mask");

    smartgear::NetEventAggregator invalid;
    invalid.set_calibration("pending", false);
    invalid.on_beam(beam(40'000, 41'000, 1, 0, 0));
    invalid.poll(286'001);
    const auto unknown_event = pop_one(invalid);
    require(unknown_event.state == smartgear::NetState::kUnknown,
            "invalid calibration must force unknown state");
    require(!unknown_event.quality_flags.empty(),
            "unknown event must explain its quality failure");

    smartgear::NetEventAggregator incomplete;
    incomplete.set_calibration("cal-test", true);
    auto incomplete_touch = touch(50'000, 50'500, 1);
    incomplete_touch.features_ready = false;
    incomplete.on_touch(incomplete_touch);
    incomplete.poll(190'501);
    const auto incomplete_event = pop_one(incomplete);
    require(has_quality_flag(incomplete_event, "waveform_incomplete"),
            "incomplete PVDF waveform must be visible in quality flags");
    require(incomplete_event.state == smartgear::NetState::kUnknown,
            "incomplete PVDF evidence must not produce a valid state");
}

void test_sequential_and_overlapping_events() {
    smartgear::NetEventAggregator sequential;
    sequential.set_calibration("cal-test", true);
    sequential.on_beam(beam(200'000, 201'000, 1, 0, 0));
    sequential.poll(446'001);
    sequential.on_beam(beam(300'000, 301'000, 1U << 2, 2, 2));
    sequential.poll(546'001);
    smartgear::NetEvent first;
    smartgear::NetEvent second;
    require(sequential.pop_event(first) && sequential.pop_event(second),
            "two separated beam events must be emitted");
    require(sequential.pending_output_count() == 0,
            "sequential event output must be drained");
    require(first.state == smartgear::NetState::kCleanOver &&
                second.state == smartgear::NetState::kCleanOver,
            "separated single-ball events must remain separate");
    require(!first.event_id.empty() && first.event_id != second.event_id,
            "separated events must have distinct stable IDs");

    smartgear::NetEventAggregator overlapping;
    overlapping.set_calibration("cal-test", true);
    overlapping.on_beam(beam(400'000, 401'000, 1, 0, 0));
    overlapping.on_beam(beam(400'500, 401'500, 2, 1, 1));
    const auto unknown = pop_one(overlapping);
    require(unknown.state == smartgear::NetState::kUnknown,
            "overlapping beam events must not be silently merged");

    smartgear::NetEventAggregator unmatched({20'000, 80'000, 200'000, 0});
    unmatched.set_calibration("cal-test", true);
    unmatched.on_beam(beam(500'000, 501'000, 1, 0, 0));
    // 该 PVDF 时间点距离光栅开始超过 before 窗口，但仍在 beam 的
    // after deadline 之前；它必须拆成 clean_over + touch_no_cross。
    unmatched.on_touch(touch(450'000, 450'000, 1));
    unmatched.poll(581'001);
    smartgear::NetEvent clean;
    require(unmatched.pop_event(clean), "unmatched beam event missing");
    require(clean.state == smartgear::NetState::kCleanOver &&
                !clean.net_touch.triggered,
            "unmatched PVDF must not be attached to clean_over");
    unmatched.poll(650'001);
    const auto no_cross = pop_one(unmatched);
    require(no_cross.state == smartgear::NetState::kTouchNoCross,
            "unmatched PVDF must remain as touch_no_cross");

    smartgear::NetEventAggregator preserve_beam({20'000, 80'000, 200'000, 0});
    preserve_beam.set_calibration("cal-test", true);
    preserve_beam.on_beam(beam(700'000, 701'000, 1, 0, 0));
    preserve_beam.on_touch(touch(600'000, 600'000, 1));
    preserve_beam.on_touch(touch(600'100, 600'100, 2));
    preserve_beam.poll(781'001);
    smartgear::NetEvent preserved_touch;
    smartgear::NetEvent preserved_beam;
    require(preserve_beam.pop_event(preserved_touch) &&
                preserve_beam.pop_event(preserved_beam),
            "mismatched pending candidates must both be retained");
    require(preserved_touch.state == smartgear::NetState::kTouchNoCross &&
                preserved_beam.state == smartgear::NetState::kCleanOver,
            "mismatched candidates must not silently drop the beam event");
}

void test_waveform_window() {
    smartgear::PiezoWaveformCapture capture({1'000, 20, 30});
    require(!capture.start_capture(0, ""),
            "waveform capture must reject an empty replay reference");
    require(capture.config().pre_trigger_samples() == 20,
            "pre-trigger sample count is wrong");
    require(capture.config().post_trigger_samples() == 30,
            "post-trigger sample count is wrong");
    for (int sample = 0; sample < 25; ++sample) {
        capture.feed_sample(0, static_cast<std::int16_t>(sample), sample);
        capture.feed_sample(1, static_cast<std::int16_t>(sample + 100), sample);
    }
    require(capture.start_capture(1'000, "wave-test"),
            "waveform capture should start");
    for (int sample = 0; sample < 30; ++sample) {
        capture.feed_sample(0, static_cast<std::int16_t>(200 + sample),
                            1'000 + sample);
        capture.feed_sample(1, static_cast<std::int16_t>(300 + sample),
                            1'000 + sample);
    }
    require(capture.ready(), "waveform capture should become ready");
    auto frame = capture.take_ready();
    require(frame.has_value(), "ready waveform frame should be available");
    require(frame->samples[0].size() == 50 && frame->samples[1].size() == 50,
            "each channel must contain pre+post samples");
    require(frame->pre_trigger_samples == 20,
            "waveform frame must retain its trigger sample boundary");
    require(frame->complete && frame->post_samples == std::array<std::size_t, 2>{30, 30},
            "complete waveform must record both post-trigger sample counts");
    require(frame->samples[0][19] == 24 && frame->samples[0][20] == 200,
            "pre/post waveform boundary is wrong");
    require(frame->samples[1][19] == 124 && frame->samples[1][20] == 300,
            "second channel waveform boundary is wrong");

    smartgear::PiezoWaveformCapture partial({1'000, 5, 5});
    partial.feed_sample(0, 11, 0);
    partial.feed_sample(0, 12, 1);
    require(partial.start_capture(2'000, "wave-partial"),
            "partial history waveform should start");
    for (int sample = 0; sample < 5; ++sample) {
        partial.feed_sample(0, static_cast<std::int16_t>(30 + sample),
                            2'000 + sample);
        partial.feed_sample(1, static_cast<std::int16_t>(40 + sample),
                            2'000 + sample);
    }
    auto partial_frame = partial.take_ready();
    require(partial_frame.has_value(), "partial history waveform should complete");
    require(partial_frame->samples[0][0] == 0 &&
                partial_frame->samples[0][1] == 0 &&
                partial_frame->samples[0][2] == 0 &&
                partial_frame->samples[0][3] == 11 &&
                partial_frame->samples[0][4] == 12,
            "partial pre-trigger history must be zero-filled chronologically");

    smartgear::PiezoWaveformCapture delayed_history({1'000, 5, 5});
    for (int sample = 0; sample < 5; ++sample) {
        delayed_history.feed_sample(
            0, static_cast<std::int16_t>(100 + sample),
            100 + static_cast<std::uint64_t>(sample));
        delayed_history.feed_sample(
            1, static_cast<std::int16_t>(200 + sample),
            100 + static_cast<std::uint64_t>(sample));
    }
    require(delayed_history.start_capture(102, "wave-delayed-history"),
            "delayed-history waveform should start");
    for (int sample = 0; sample < 5; ++sample) {
        delayed_history.feed_sample(
            0, static_cast<std::int16_t>(300 + sample),
            102 + static_cast<std::uint64_t>(sample));
        delayed_history.feed_sample(
            1, static_cast<std::int16_t>(400 + sample),
            102 + static_cast<std::uint64_t>(sample));
    }
    const auto delayed_frame = delayed_history.take_ready();
    require(delayed_frame.has_value() &&
                delayed_frame->pre_samples_available ==
                    std::array<std::size_t, 2>{2, 2} &&
                delayed_frame->samples[0][3] == 100 &&
                delayed_frame->samples[0][4] == 101 &&
                delayed_frame->samples[1][3] == 200 &&
                delayed_frame->samples[1][4] == 201,
            "pre-trigger history must exclude samples at or after the trigger");

    smartgear::PiezoWaveformCapture delayed_out_of_order({1'000, 5, 5});
    for (int sample = 0; sample < 5; ++sample) {
        delayed_out_of_order.feed_sample(
            0, static_cast<std::int16_t>(500 + sample),
            100 + static_cast<std::uint64_t>(sample));
        delayed_out_of_order.feed_sample(
            1, static_cast<std::int16_t>(600 + sample),
            100 + static_cast<std::uint64_t>(sample));
    }
    require(delayed_out_of_order.start_capture(102,
                                               "wave-delayed-out-of-order"),
            "delayed out-of-order waveform should start");
    // This sample is still inside the pre-trigger window, but older than the
    // newest sample already captured by the start snapshot. It is a genuine
    // reordered DMA delivery and must invalidate the frame.
    delayed_out_of_order.feed_sample(0, 499, 99);
    for (int sample = 0; sample < 5; ++sample) {
        delayed_out_of_order.feed_sample(
            0, static_cast<std::int16_t>(700 + sample),
            102 + static_cast<std::uint64_t>(sample));
        delayed_out_of_order.feed_sample(
            1, static_cast<std::int16_t>(800 + sample),
            102 + static_cast<std::uint64_t>(sample));
    }
    const auto delayed_out_of_order_frame = delayed_out_of_order.take_ready();
    require(delayed_out_of_order_frame.has_value() &&
                !delayed_out_of_order_frame->sample_timestamps_valid,
            "in-window DMA samples older than the snapshot must invalidate evidence");

    smartgear::PiezoWaveformCapture cold_start({1'000, 5, 5});
    require(cold_start.start_capture(3'000, "wave-cold-start"),
            "cold-start waveform should begin without history");
    for (int sample = 0; sample < 5; ++sample) {
        cold_start.feed_sample(0, static_cast<std::int16_t>(50 + sample),
                               3'000 + sample);
        cold_start.feed_sample(1, static_cast<std::int16_t>(60 + sample),
                               3'000 + sample);
    }
    auto cold_frame = cold_start.take_ready();
    require(cold_frame.has_value() && cold_frame->complete &&
                cold_frame->pre_samples_available == std::array<std::size_t, 2>{0, 0},
            "cold-start waveform must retain its missing pre-trigger evidence");
    const auto cold_features =
        smartgear::extract_piezo_features(*cold_frame, 1'000);
    require(!cold_features.complete,
            "missing pre-trigger history must keep features incomplete");

    smartgear::PiezoWaveformCapture dma_backlog({1'000, 5, 5});
    require(dma_backlog.start_capture(100, "wave-dma-backlog"),
            "DMA backlog waveform should begin without prehistory");
    for (int sample = 0; sample < 5; ++sample) {
        dma_backlog.feed_sample(0, static_cast<std::int16_t>(70 + sample),
                                95 + sample);
        dma_backlog.feed_sample(1, static_cast<std::int16_t>(80 + sample),
                                95 + sample);
    }
    for (int sample = 0; sample < 5; ++sample) {
        dma_backlog.feed_sample(0, static_cast<std::int16_t>(90 + sample),
                                100 + sample);
        dma_backlog.feed_sample(1, static_cast<std::int16_t>(100 + sample),
                                100 + sample);
    }
    auto dma_frame = dma_backlog.take_ready();
    require(dma_frame.has_value() &&
                dma_frame->pre_samples_available == std::array<std::size_t, 2>{5, 5} &&
                dma_frame->samples[0][4] == 74 &&
                dma_frame->samples[0][5] == 90,
            "late pre-trigger DMA samples must backfill the current frame");
    const auto dma_features =
        smartgear::extract_piezo_features(*dma_frame, 1'000);
    require(dma_features.complete,
            "a fully recovered DMA pre-trigger window must become complete evidence");

    smartgear::PiezoWaveformCapture stale_dma({1'000, 5, 5});
    require(stale_dma.start_capture(10'000, "wave-stale-dma"),
            "stale DMA waveform should begin");
    // This sample is 10 ms before the trigger, outside the configured 5 ms
    // pre-trigger window. It must not fill the frame's missing history.
    stale_dma.feed_sample(0, 999, 0);
    stale_dma.feed_sample(1, 999, 0);
    for (int sample = 0; sample < 5; ++sample) {
        stale_dma.feed_sample(0, static_cast<std::int16_t>(120 + sample),
                              10'000 + sample);
        stale_dma.feed_sample(1, static_cast<std::int16_t>(220 + sample),
                              10'000 + sample);
    }
    auto stale_frame = stale_dma.take_ready();
    require(stale_frame.has_value() &&
                stale_frame->pre_samples_available == std::array<std::size_t, 2>{0, 0} &&
                stale_frame->sample_timestamps_valid &&
                stale_frame->samples[0][4] == 0,
            "stale DMA samples must not be treated as pre-trigger evidence");
    require(!smartgear::extract_piezo_features(*stale_frame, 1'000).complete,
            "a stale-only pre-trigger window must remain incomplete");

    smartgear::PiezoWaveformCapture out_of_order({1'000, 5, 5});
    require(out_of_order.start_capture(20'000, "wave-out-of-order"),
            "out-of-order waveform should begin");
    const std::array<std::uint64_t, 5> left_times = {20'000, 20'002, 20'001,
                                                       20'003, 20'004};
    const std::array<std::uint64_t, 5> right_times = {20'000, 20'001, 20'002,
                                                        20'003, 20'004};
    for (std::size_t sample = 0; sample < left_times.size(); ++sample) {
        out_of_order.feed_sample(0, static_cast<std::int16_t>(150 + sample),
                                 left_times[sample]);
        out_of_order.feed_sample(1, static_cast<std::int16_t>(250 + sample),
                                 right_times[sample]);
    }
    const auto out_of_order_frame = out_of_order.take_ready();
    require(out_of_order_frame.has_value() && !out_of_order_frame->complete &&
                !out_of_order_frame->sample_timestamps_valid,
            "out-of-order ADC samples must not become complete evidence");
    require(!smartgear::extract_piezo_features(*out_of_order_frame, 1'000)
                 .complete,
            "out-of-order ADC features must remain incomplete");
    require(out_of_order.start_capture(21'000, "wave-after-out-of-order"),
            "out-of-order frame must release the capture state");
    for (int sample = 0; sample < 5; ++sample) {
        out_of_order.feed_sample(0, static_cast<std::int16_t>(350 + sample),
                                 21'000 + static_cast<std::uint64_t>(sample));
        out_of_order.feed_sample(1, static_cast<std::int16_t>(450 + sample),
                                 21'000 + static_cast<std::uint64_t>(sample));
    }
    const auto after_out_of_order = out_of_order.take_ready();
    require(after_out_of_order.has_value() &&
                after_out_of_order->pre_samples_available ==
                    std::array<std::size_t, 2>{0, 0},
            "out-of-order samples must not pollute the next pre-trigger history");

    smartgear::PiezoWaveformCapture outside_window({1'000, 5, 5});
    for (int sample = 0; sample < 5; ++sample) {
        outside_window.feed_sample(0, static_cast<std::int16_t>(130 + sample),
                                   25'000 + static_cast<std::uint64_t>(sample));
        outside_window.feed_sample(1, static_cast<std::int16_t>(230 + sample),
                                   25'000 + static_cast<std::uint64_t>(sample));
    }
    require(outside_window.start_capture(30'000, "wave-outside-window"),
            "outside-window waveform should begin");
    // This old DMA backlog is ignored for the current frame; it must not
    // damage a complete frame whose valid post-trigger samples follow it.
    outside_window.feed_sample(0, 120, 0);
    outside_window.feed_sample(1, 220, 0);
    for (int sample = 0; sample < 5; ++sample) {
        outside_window.feed_sample(0, static_cast<std::int16_t>(180 + sample),
                                   30'000 + static_cast<std::uint64_t>(sample));
        outside_window.feed_sample(1, static_cast<std::int16_t>(280 + sample),
                                   30'000 + static_cast<std::uint64_t>(sample));
    }
    const auto complete_after_backlog = outside_window.take_ready();
    require(complete_after_backlog.has_value() &&
                complete_after_backlog->complete &&
                complete_after_backlog->sample_timestamps_valid &&
                complete_after_backlog->pre_samples_available ==
                    std::array<std::size_t, 2>{5, 5},
            "stale DMA backlog must not poison an otherwise complete frame");

    // A stale DMA sample can also arrive after the frame has already closed.
    // It must be rejected from the rolling history, otherwise it becomes the
    // next event's pre-trigger baseline even though it was outside the old
    // frame's timestamp window.
    outside_window.feed_sample(0, 1, 0);
    outside_window.feed_sample(1, 2, 0);
    require(outside_window.start_capture(31'000, "wave-after-stale-history"),
            "capture after a stale inactive sample should start");
    for (int sample = 0; sample < 5; ++sample) {
        outside_window.feed_sample(
            0, static_cast<std::int16_t>(380 + sample),
            31'000 + static_cast<std::uint64_t>(sample));
        outside_window.feed_sample(
            1, static_cast<std::int16_t>(480 + sample),
            31'000 + static_cast<std::uint64_t>(sample));
    }
    const auto after_stale_history = outside_window.take_ready();
    require(after_stale_history.has_value() &&
                after_stale_history->pre_samples_available ==
                    std::array<std::size_t, 2>{5, 5} &&
                after_stale_history->samples[0][0] == 180 &&
                after_stale_history->samples[0][4] == 184,
            "late inactive DMA samples must not enter the next pre-trigger history");

    smartgear::PiezoWaveformCapture post_outside_window({1'000, 5, 5});
    require(post_outside_window.start_capture(40'000,
                                              "wave-post-outside-window"),
            "post-outside-window waveform should begin");
    for (int sample = 0; sample < 4; ++sample) {
        post_outside_window.feed_sample(
            0, static_cast<std::int16_t>(180 + sample),
            40'000 + static_cast<std::uint64_t>(sample));
        post_outside_window.feed_sample(
            1, static_cast<std::int16_t>(280 + sample),
            40'000 + static_cast<std::uint64_t>(sample));
    }
    post_outside_window.feed_sample(0, 190, 45'001);
    post_outside_window.feed_sample(1, 290, 45'001);
    require(post_outside_window.expire(45'000),
            "outside-window waveform must flush at its post deadline");
    const auto outside_frame = post_outside_window.take_ready();
    require(outside_frame.has_value() && !outside_frame->complete &&
                outside_frame->sample_timestamps_valid &&
                outside_frame->post_samples == std::array<std::size_t, 2>{4, 4},
            "samples after the post window must not fill the waveform frame");
}

void test_waveform_timeout_flush() {
    smartgear::PiezoWaveformCapture capture({1'000, 5, 5});
    require(capture.start_capture(1'000, "wave-timeout-partial"),
            "partial timeout waveform should start");
    for (int sample = 0; sample < 3; ++sample) {
        capture.feed_sample(0, static_cast<std::int16_t>(20 + sample),
                            1'000 + sample);
    }
    require(capture.expire(6'000),
            "waveform must flush when the post-trigger deadline expires");
    auto frame = capture.take_ready();
    require(frame.has_value() && !frame->complete,
            "expired waveform must remain explicitly incomplete");
    require(frame->post_samples == std::array<std::size_t, 2>{3, 0},
            "partial waveform must retain per-channel sample counts");
    const auto features =
        smartgear::extract_piezo_features(*frame, 1'000);
    require(!features.complete,
            "partial waveform features must not become ready evidence");
    require(capture.start_capture(7'000, "wave-after-timeout"),
            "timeout flush must release the capture state");
}

void test_piezo_feature_extraction() {
    smartgear::PiezoWaveformFrame frame;
    frame.pre_trigger_samples = 4;
    frame.samples[0] = {100, 100, 100, 100, 101, 102, 106, 110, 104, 100};
    frame.samples[1] = {200, 200, 200, 200, 200, 200, 205, 200, 200, 200};
    frame.pre_samples_available = {4, 4};
    frame.post_samples = {6, 6};
    frame.complete = true;
    const auto features = smartgear::extract_piezo_features(frame, 1'000);
    require(features.peak[0] == 10.0F && features.peak[1] == 5.0F,
            "waveform peak extraction is wrong");
    require(features.energy[0] == 157.0F && features.energy[1] == 25.0F,
            "waveform energy extraction is wrong");
    require(features.duration_us == 5'000,
            "waveform duration must use the longest thresholded run");
}

void test_waveform_archive() {
    smartgear::PiezoWaveformArchive archive(2);
    smartgear::PiezoWaveformFrame first;
    first.reference = "wave-1";
    first.samples[0] = {1, 2, 3};
    archive.store(first);
    require(archive.contains("wave-1"),
            "waveform archive must retain the first reference");

    smartgear::PiezoWaveformFrame second;
    second.reference = "wave-2";
    second.samples[0] = {4, 5};
    archive.store(second);

    smartgear::PiezoWaveformFrame replacement;
    replacement.reference = "wave-1";
    replacement.samples[0] = {9, 9, 9};
    archive.store(replacement);
    require(archive.size() == 2 && archive.dropped_count() == 0,
            "replacing a waveform must not evict another frame");
    const auto* stored = archive.find("wave-1");
    require(stored != nullptr && stored->samples[0][0] == 9,
            "waveform archive replacement is wrong");

    smartgear::PiezoWaveformFrame third;
    third.reference = "wave-3";
    archive.store(third);
    require(!archive.contains("wave-1") && archive.contains("wave-2") &&
                archive.contains("wave-3") &&
                archive.dropped_count() == 1,
            "waveform archive must evict the oldest frame at capacity");
}

void test_waveform_hook_contract() {
    const std::int16_t left[] = {1, 2, 3};
    const std::int16_t right[] = {4, 5};
    g_waveform_hook_called = false;
    require(smartgear_board_on_piezo_waveform(
                "wave-hook", 1'234, 2, left, 3, right, 2, false),
            "waveform adapter hook must accept a synchronous frame");
    require(g_waveform_hook_called && !g_waveform_hook_complete &&
                g_waveform_hook_left_count == 3 &&
                g_waveform_hook_right_count == 2,
            "waveform adapter hook contract must preserve frame metadata");
}

void test_sensor_health_quality_flags() {
    smartgear::NetEventAggregator healthy;
    healthy.set_calibration("cal-test", true);
    healthy.set_beam_health(1U << 2, true);
    healthy.set_piezo_baseline(true);
    healthy.on_beam(beam(10'000, 11'000, 1U << 2, 2, 2));
    healthy.poll(256'001);
    const auto healthy_event = pop_one(healthy);
    require(!has_quality_flag(healthy_event, "beam_self_test_invalid") &&
                !has_quality_flag(healthy_event, "beam_channel_unhealthy"),
            "healthy beam self-test must not add failure flags");

    smartgear::NetEventAggregator unverified;
    unverified.set_calibration("pending", false);
    unverified.set_beam_health(0, false);
    unverified.on_beam(beam(15'000, 16'000, 1, 0, 0));
    unverified.poll(261'001);
    const auto unverified_event = pop_one(unverified);
    require(has_quality_flag(unverified_event, "beam_self_test_invalid") &&
                !has_quality_flag(unverified_event, "beam_channel_unhealthy"),
            "incomplete beam self-test must not claim a channel failure");

    smartgear::NetEventAggregator unhealthy;
    unhealthy.set_calibration("cal-test", true);
    unhealthy.set_beam_health(0, true);
    unhealthy.set_piezo_baseline(false);
    unhealthy.on_beam(beam(20'000, 21'000, 1, 0, 0));
    unhealthy.poll(266'001);
    const auto unhealthy_beam = pop_one(unhealthy);
    require(!has_quality_flag(unhealthy_beam, "beam_self_test_invalid") &&
                has_quality_flag(unhealthy_beam, "beam_channel_unhealthy"),
            "failed beam self-test must be visible in event quality");
    require(unhealthy_beam.state == smartgear::NetState::kUnknown,
            "a hit on an unhealthy beam must not be reported as valid height");

    unhealthy.on_touch(touch(30'000, 30'500, 1));
    unhealthy.poll(170'501);
    const auto unhealthy_touch = pop_one(unhealthy);
    require(has_quality_flag(unhealthy_touch, "piezo_baseline_invalid"),
            "failed PVDF baseline must be visible in event quality");
    require(unhealthy_touch.state == smartgear::NetState::kUnknown,
            "PVDF baseline failure must make the touch state unknown");

    smartgear::NetEventAggregator overflow;
    overflow.set_calibration("cal-test", true);
    overflow.mark_input_overflow();
    overflow.on_beam(beam(25'000, 26'000, 1, 0, 0));
    overflow.poll(271'001);
    const auto overflow_event = pop_one(overflow);
    require(overflow_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(overflow_event, "sensor_queue_overflow"),
            "dropped GPIO edges must produce an explicit unknown event");

    smartgear::NetEventAggregator overflow_pending;
    overflow_pending.set_calibration("cal-test", true);
    overflow_pending.on_touch(touch(26'000, 26'500, 1));
    overflow_pending.mark_input_overflow();
    overflow_pending.on_beam(beam(35'000, 36'000, 1U << 1, 1, 1));
    overflow_pending.poll(281'001);
    const auto post_overflow_event = pop_one(overflow_pending);
    require(post_overflow_event.timestamp_us == 35'000 &&
                post_overflow_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(post_overflow_event, "sensor_queue_overflow") &&
                post_overflow_event.net_touch.sensor_mask == 0,
            "overflow must discard stale touch candidates before the next event");

    smartgear::NetEventAggregator invalid_health;
    invalid_health.set_calibration("cal-test", true);
    invalid_health.set_beam_health(0x0400U, true);
    invalid_health.on_beam(beam(26'000, 27'000, 1, 0, 0));
    invalid_health.poll(272'001);
    const auto invalid_health_event = pop_one(invalid_health);
    require(invalid_health_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(invalid_health_event, "beam_self_test_invalid") &&
                !has_quality_flag(invalid_health_event, "beam_channel_unhealthy"),
            "an out-of-range health bit must fail closed before height validation");

    smartgear::NetEventAggregator empty_calibration;
    empty_calibration.set_calibration("", true);
    empty_calibration.on_beam(beam(28'000, 29'000, 1, 0, 0));
    empty_calibration.poll(274'001);
    const auto empty_calibration_event = pop_one(empty_calibration);
    require(empty_calibration_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(empty_calibration_event, "calibration_invalid"),
            "an empty calibration ID must not authorize a valid event");

    smartgear::NetEventAggregator changed_during_beam;
    changed_during_beam.set_calibration("cal-before", true);
    changed_during_beam.set_beam_health(0x03ffU, true);
    changed_during_beam.set_piezo_baseline(true);
    changed_during_beam.on_beam(beam(29'000, 30'000, 1U << 2, 2, 2));
    changed_during_beam.set_beam_health(0x03fbU, true);
    changed_during_beam.poll(300'001);
    const auto changed_beam_event = pop_one(changed_during_beam);
    require(changed_beam_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(changed_beam_event,
                                 "sensor_health_changed_during_event"),
            "a health change during a pending beam event must fail closed");

    smartgear::NetEventAggregator changed_during_touch;
    changed_during_touch.set_calibration("cal-before", true);
    changed_during_touch.set_beam_health(0x03ffU, true);
    changed_during_touch.set_piezo_baseline(true);
    changed_during_touch.on_touch(touch(31'000, 31'500, 1));
    changed_during_touch.set_calibration("cal-after", true);
    changed_during_touch.poll(172'001);
    const auto changed_touch_event = pop_one(changed_during_touch);
    require(changed_touch_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(changed_touch_event,
                                 "sensor_health_changed_during_event"),
            "a calibration change during a pending touch must fail closed");

    smartgear::NetEventAggregator unchanged_snapshot;
    unchanged_snapshot.set_calibration("cal-same", true);
    unchanged_snapshot.set_beam_health(0x03ffU, true);
    unchanged_snapshot.set_piezo_baseline(true);
    unchanged_snapshot.on_beam(beam(32'000, 33'000, 1U << 1, 1, 1));
    // Repeating the same board snapshot is not a health transition and must
    // not make an otherwise valid pending event unknown.
    unchanged_snapshot.set_calibration("cal-same", true);
    unchanged_snapshot.set_beam_health(0x03ffU, true);
    unchanged_snapshot.set_piezo_baseline(true);
    unchanged_snapshot.poll(303'001);
    const auto unchanged_event = pop_one(unchanged_snapshot);
    require(unchanged_event.state == smartgear::NetState::kCleanOver &&
                !has_quality_flag(unchanged_event,
                                  "sensor_health_changed_during_event"),
            "an identical health snapshot must not invalidate a pending event");
}

void test_channel_self_test_and_baseline() {
    std::array<smartgear::BeamChannelCheck, smartgear::config::kBeamCount> checks{};
    for (auto& check : checks) {
        check = {true, true, true, true};
    }
    checks[7].receiver_ok = false;
    const auto report = smartgear::evaluate_beam_self_test(checks);
    require((report.pass_mask & (1U << 0)) != 0,
            "healthy beam channel must pass self-test");
    require((report.fail_mask & (1U << 7)) != 0,
            "failed receiver must be reported by channel mask");
    require(!report.all_pass, "one failed beam channel must fail self-test");

    for (std::size_t failed_field = 0; failed_field < 4; ++failed_field) {
        auto one_channel = std::array<smartgear::BeamChannelCheck,
                                      smartgear::config::kBeamCount>{};
        for (auto& check : one_channel) {
            check = {true, true, true, true};
        }
        switch (failed_field) {
            case 0:
                one_channel[0].emitter_ok = false;
                break;
            case 1:
                one_channel[0].receiver_ok = false;
                break;
            case 2:
                one_channel[0].clear_baseline = false;
                break;
            default:
                one_channel[0].blocked_response = false;
                break;
        }
        const auto field_report = smartgear::evaluate_beam_self_test(one_channel);
        require((field_report.fail_mask & 1U) != 0 &&
                    (field_report.pass_mask & 1U) == 0,
                "each optical self-test component must gate its channel");
    }

    const smartgear::PiezoQuietBaseline quiet{{0.2F, 0.3F}, {0.1F, 0.1F}, 1600};
    require(smartgear::piezo_baseline_is_quiet(quiet, 0.5F, 0.2F),
            "quiet PVDF baseline should pass");
    const smartgear::PiezoQuietBaseline noisy{{0.8F, 0.3F}, {0.1F, 0.1F}, 1600};
    require(!smartgear::piezo_baseline_is_quiet(noisy, 0.5F, 0.2F),
            "noisy PVDF baseline should fail");
    const smartgear::PiezoQuietBaseline invalid{{-0.1F, 0.3F}, {0.1F, 0.1F}, 1600};
    require(!smartgear::piezo_baseline_is_quiet(invalid, 0.5F, 0.2F),
            "negative PVDF baseline values must fail validation");
    require(!smartgear::piezo_baseline_is_quiet(quiet,
                                                std::numeric_limits<float>::quiet_NaN(),
                                                0.2F) &&
                !smartgear::piezo_baseline_is_quiet(quiet, 0.5F,
                                                    std::numeric_limits<float>::infinity()),
            "non-finite PVDF baseline thresholds must fail validation");

    auto all_pass_checks = checks;
    all_pass_checks[7].receiver_ok = true;
    const auto complete_report =
        smartgear::evaluate_beam_self_test(all_pass_checks);
    require(smartgear::beam_self_test_report_is_well_formed(complete_report),
            "complete optical self-test report should be well formed");
    const char health_id[] = "cal-health-v1";
    const auto complete_snapshot = smartgear::make_sensor_health_snapshot(
        complete_report, quiet, 0.5F, 0.2F, health_id, sizeof(health_id), true);
    require(complete_snapshot.healthy_beam_mask == 0x03ffU &&
                complete_snapshot.beam_health_valid &&
                complete_snapshot.piezo_baseline_valid &&
                complete_snapshot.calibration_valid,
            "complete self-test inputs must compose into a valid health snapshot");

    const auto partial_snapshot = smartgear::make_sensor_health_snapshot(
        report, quiet, 0.5F, 0.2F, health_id, sizeof(health_id), true);
    require(partial_snapshot.beam_health_valid &&
                (partial_snapshot.healthy_beam_mask & (1U << 7)) == 0 &&
                partial_snapshot.calibration_valid,
            "partial optical failure must preserve a valid partial health mask");

    auto malformed_report = complete_report;
    malformed_report.pass_mask = 0x0400U;
    const auto malformed_snapshot = smartgear::make_sensor_health_snapshot(
        malformed_report, quiet, 0.5F, 0.2F, health_id, sizeof(health_id), true);
    require(!malformed_snapshot.beam_health_valid &&
                malformed_snapshot.healthy_beam_mask == 0 &&
                !malformed_snapshot.calibration_valid,
            "malformed optical report must fail closed at health composition");

    const char valid_id[] = "cal-v1";
    require(smartgear::sensor_health_snapshot_is_well_formed(
                valid_id, sizeof(valid_id), 0x03ffU, true, true),
            "well-formed sensor health snapshot should pass");
    require(!smartgear::sensor_health_snapshot_is_well_formed(
                "", 1, 0x03ffU, true, true),
            "valid calibration cannot have an empty ID");
    require(!smartgear::sensor_health_snapshot_is_well_formed(
                valid_id, sizeof(valid_id), 0x0400U, true, true),
            "beam health snapshot must not contain bits above channel 9");
    require(!smartgear::sensor_health_snapshot_is_well_formed(
                valid_id, sizeof(valid_id), 0x0400U, false, false),
            "invalid beam health must still reject out-of-range bits");
    require(!smartgear::sensor_health_snapshot_is_well_formed(
                valid_id, sizeof(valid_id), 1U, false, false),
            "invalid beam health must not carry a nonzero healthy mask");
    const char unterminated_id[] = {'c', 'a', 'l', 'x'};
    require(!smartgear::sensor_health_snapshot_is_well_formed(
                unterminated_id, sizeof(unterminated_id), 0x03ffU, true,
                true),
            "health snapshot must reject an unterminated calibration ID");
}

void test_sensor_health_gate_pipeline() {
    const char calibration_id[] = "cal-gate-v1";
    smartgear::SensorHealthSnapshot partial{
        static_cast<std::uint16_t>(smartgear::config::kAllBeamMask & ~(1U << 7)),
        true,
        true,
        true,
    };
    smartgear::NetEventAggregator aggregator;
    require(smartgear::apply_sensor_health_snapshot(
                aggregator, calibration_id, sizeof(calibration_id), partial),
            "valid partial health snapshot must be accepted by the gate");

    aggregator.on_beam(beam(40'000, 41'000, 1U << 2, 2, 2));
    aggregator.poll(291'001);
    const auto healthy_channel_event = pop_one(aggregator);
    require(healthy_channel_event.state == smartgear::NetState::kCleanOver &&
                !has_quality_flag(healthy_channel_event,
                                  "beam_channel_unhealthy"),
            "a healthy channel from a partial snapshot must authorize height");

    aggregator.on_beam(beam(42'000, 43'000, 1U << 7, 7, 7));
    aggregator.poll(293'001);
    const auto failed_channel_event = pop_one(aggregator);
    require(failed_channel_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(failed_channel_event, "beam_channel_unhealthy"),
            "a failed channel from a partial snapshot must fail closed");

    smartgear::NetEventAggregator unavailable;
    smartgear::apply_sensor_health_unavailable(unavailable);
    unavailable.on_beam(beam(44'000, 45'000, 1, 0, 0));
    unavailable.poll(295'001);
    const auto unavailable_event = pop_one(unavailable);
    require(unavailable_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(unavailable_event, "calibration_invalid") &&
                has_quality_flag(unavailable_event, "beam_self_test_invalid"),
            "an unavailable health hook must fail closed through the gate");

    const char malformed_id[] = {'c', 'a', 'l'};
    smartgear::NetEventAggregator malformed;
    require(!smartgear::apply_sensor_health_snapshot(
                malformed, malformed_id, sizeof(malformed_id), partial),
            "unterminated calibration ID must be rejected by the gate");
    malformed.on_beam(beam(46'000, 47'000, 1, 0, 0));
    malformed.poll(297'001);
    const auto malformed_event = pop_one(malformed);
    require(malformed_event.state == smartgear::NetState::kUnknown &&
                malformed_event.calibration_id == "health-snapshot-invalid" &&
                has_quality_flag(malformed_event, "beam_self_test_invalid"),
            "malformed health input must leave a deterministic fail-closed marker");
}

void test_sensor_pipeline_end_to_end() {
    smartgear::BeamCapture beam_capture(5, 250'000);
    smartgear::PiezoCapture piezo_capture(5'000, 120'000);
    smartgear::NetEventAggregator aggregator;
    aggregator.set_calibration("cal-pipeline", true);
    aggregator.set_beam_health(1U, true);
    aggregator.set_piezo_baseline(true);

    piezo_capture.on_trigger(0, 1'000, 0.0F, 0.0F, "wave-pipeline");
    smartgear::PiezoFeatureSummary features;
    features.peak = {8.0F, 0.0F};
    features.energy = {64.0F, 0.0F};
    features.duration_us = 750;
    features.complete = true;
    piezo_capture.on_waveform_ready("wave-pipeline", features);
    const auto touch_observation = piezo_capture.poll(6'001);
    require(touch_observation.has_value(),
            "pipeline PVDF observation must close before beam association");
    aggregator.on_touch(*touch_observation);

    beam_capture.on_edge(0, true, 5'000);
    beam_capture.on_edge(0, false, 6'000);
    const auto beam_observation = beam_capture.poll(6'005);
    require(beam_observation.has_value(),
            "pipeline beam observation must close after quiet time");
    aggregator.on_beam(*beam_observation);

    const auto event = pop_one(aggregator);
    require(event.state == smartgear::NetState::kTouchOver,
            "sensor pipeline must produce touch_over");
    require(event.beam_mask == 1 && event.net_touch.sensor_mask == 1,
            "pipeline must retain both beam and PVDF channel masks");
    require(event.net_touch.waveform_ref == "wave-pipeline" &&
                event.net_touch.peak[0] == 8.0F,
            "pipeline must retain completed waveform evidence");
}

void test_trigger_before_dma_dispatch_pipeline() {
    constexpr std::uint64_t trigger_us = 10'000;
    constexpr char waveform_reference[] = "wave-trigger-first";

    smartgear::PiezoCapture piezo_capture(5'000, 20'000);
    smartgear::PiezoWaveformCapture waveform_capture({1'000, 5, 5});
    smartgear::NetEventAggregator aggregator;
    aggregator.set_calibration("cal-trigger-first", true);
    aggregator.set_beam_health(1U, true);
    aggregator.set_piezo_baseline(true);

    // This is the ordering used by the ESP32 task: consume the comparator
    // edge first, then dispatch the ADC DMA batch containing late pre-trigger
    // samples and the post-trigger window.
    require(waveform_capture.start_capture(trigger_us, waveform_reference),
            "trigger-first pipeline must start its waveform frame");
    require(!piezo_capture.on_trigger(0, trigger_us, 0.0F, 0.0F,
                                      waveform_reference),
            "the first comparator edge must only create a pending candidate");
    for (int sample = 0; sample < 5; ++sample) {
        waveform_capture.feed_sample(
            0, static_cast<std::int16_t>(70 + sample),
            trigger_us - 5'000 + static_cast<std::uint64_t>(sample) * 1'000U);
        waveform_capture.feed_sample(
            1, static_cast<std::int16_t>(80 + sample),
            trigger_us - 5'000 + static_cast<std::uint64_t>(sample) * 1'000U);
    }
    for (int sample = 0; sample < 5; ++sample) {
        waveform_capture.feed_sample(
            0, static_cast<std::int16_t>(90 + sample),
            trigger_us + static_cast<std::uint64_t>(sample) * 1'000U);
        waveform_capture.feed_sample(
            1, static_cast<std::int16_t>(100 + sample),
            trigger_us + static_cast<std::uint64_t>(sample) * 1'000U);
    }

    auto frame = waveform_capture.take_ready();
    require(frame.has_value() && frame->complete &&
                frame->pre_samples_available == std::array<std::size_t, 2>{5, 5},
            "trigger-first DMA dispatch must produce a complete frame");
    const auto features = smartgear::extract_piezo_features(*frame, 1'000);
    require(features.complete,
            "trigger-first DMA dispatch must retain complete waveform evidence");
    piezo_capture.on_waveform_ready(frame->reference, features);
    const auto touch_observation = piezo_capture.poll(trigger_us + 5'001);
    require(touch_observation.has_value() && touch_observation->features_ready &&
                touch_observation->waveform_ref == waveform_reference,
            "completed DMA frame must close the comparator candidate");
    aggregator.on_touch(*touch_observation);

    aggregator.on_beam(beam(trigger_us + 2'000, trigger_us + 3'000, 1, 0, 0));
    const auto event = pop_one(aggregator);
    require(event.state == smartgear::NetState::kTouchOver &&
                event.net_touch.waveform_ref == waveform_reference &&
                event.net_touch.sensor_mask == 1,
            "trigger-first pipeline must produce touch_over with waveform evidence");
}

void test_input_shape_and_deadline_safety() {
    smartgear::NetEventAggregator malformed_beam;
    malformed_beam.set_calibration("cal-shape", true);
    auto beam_with_wrong_bounds = beam(80'000, 81'000, 1, 0, 0);
    beam_with_wrong_bounds.min_index = 4;
    malformed_beam.on_beam(beam_with_wrong_bounds);
    const auto malformed_beam_event = pop_one(malformed_beam);
    require(malformed_beam_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(malformed_beam_event, "beam_shape_invalid") &&
                malformed_beam_event.beam_mask == 0,
            "malformed beam observations must fail closed without height data");

    smartgear::NetEventAggregator reversed_beam;
    reversed_beam.set_calibration("cal-shape", true);
    auto beam_with_reversed_time = beam(83'000, 82'000, 1, 0, 0);
    reversed_beam.on_beam(beam_with_reversed_time);
    const auto reversed_beam_event = pop_one(reversed_beam);
    require(reversed_beam_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(reversed_beam_event, "beam_shape_invalid") &&
                reversed_beam_event.beam_mask == 0,
            "beam observations with reversed time bounds must fail closed");

    smartgear::NetEventAggregator malformed_touch;
    malformed_touch.set_calibration("cal-shape", true);
    auto touch_with_wrong_mask = touch(82'000, 82'100, 1);
    touch_with_wrong_mask.sensor_mask = 4;
    malformed_touch.on_touch(touch_with_wrong_mask);
    const auto malformed_touch_event = pop_one(malformed_touch);
    require(malformed_touch_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(malformed_touch_event, "touch_shape_invalid") &&
                !malformed_touch_event.net_touch.triggered &&
                malformed_touch_event.net_touch.sensor_mask == 0,
            "malformed PVDF observations must not violate the event contract");

    smartgear::NetEvent direct_event;
    direct_event.net_touch.peak[0] =
        std::numeric_limits<float>::quiet_NaN();
    direct_event.net_touch.energy[1] = -1.0F;
    const auto safe_json = smartgear::net_event_to_json(direct_event);
    require(safe_json.find("nan") == std::string::npos &&
                safe_json.find("NaN") == std::string::npos &&
                safe_json.find("-1.0000") == std::string::npos,
            "JSON serialization must not emit non-finite or negative floats");

    smartgear::NetEventAggregator saturated({0,
                                             std::numeric_limits<std::uint64_t>::max(),
                                             0,
                                             std::numeric_limits<std::uint64_t>::max()});
    saturated.set_calibration("cal-saturated", true);
    saturated.on_beam(beam(std::numeric_limits<std::uint64_t>::max() - 100,
                           std::numeric_limits<std::uint64_t>::max() - 50,
                           1, 0, 0));
    saturated.poll(std::numeric_limits<std::uint64_t>::max());
    const auto saturated_event = pop_one(saturated);
    require(saturated_event.state == smartgear::NetState::kCleanOver,
            "deadline arithmetic must saturate instead of wrapping around");

    smartgear::NetEventAggregator pending_boundary;
    pending_boundary.set_calibration("cal-pending", true);
    pending_boundary.on_beam(beam(90'000, 91'000, 1, 0, 0));
    auto bad_boundary = beam(92'000, 93'000, 1, 0, 0);
    bad_boundary.valid = false;
    pending_boundary.on_beam(bad_boundary);
    smartgear::NetEvent pending_event;
    smartgear::NetEvent bad_boundary_event;
    require(pending_boundary.pop_event(pending_event) &&
                pending_boundary.pop_event(bad_boundary_event),
            "malformed beam boundary must emit both affected events");
    require(pending_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(pending_event, "pending_beam_boundary_unknown") &&
                bad_boundary_event.state == smartgear::NetState::kUnknown &&
                has_quality_flag(bad_boundary_event, "beam_boundary_unknown"),
            "a malformed beam boundary must close old pending state explicitly");
    pending_boundary.poll(300'000);
    require(pending_boundary.pending_output_count() == 0,
            "malformed beam boundary must not leave a duplicate pending event");

    smartgear::NetEventAggregator stale_beam;
    stale_beam.set_calibration("cal-stale", true);
    stale_beam.on_beam(beam(100'000, 101'000, 1, 0, 0));
    stale_beam.poll(356'001);
    static_cast<void>(pop_one(stale_beam));
    stale_beam.on_beam(beam(90'000, 91'000, 1U << 1, 1, 1));
    const auto stale_beam_event = pop_one(stale_beam);
    require(stale_beam_event.state == smartgear::NetState::kUnknown,
            "aggregator must reject an out-of-order beam observation");

    smartgear::NetEventAggregator stale_touch;
    stale_touch.set_calibration("cal-stale-touch", true);
    stale_touch.on_touch(touch(120'000, 120'500, 1));
    stale_touch.poll(260'501);
    static_cast<void>(pop_one(stale_touch));
    stale_touch.on_touch(touch(110'000, 110'500, 2));
    const auto stale_touch_event = pop_one(stale_touch);
    require(stale_touch_event.state == smartgear::NetState::kUnknown,
            "aggregator must reject an out-of-order touch observation");
}

struct DeliverySink {
    std::vector<std::string> messages;
    bool accepting = true;
    std::size_t sends_before_failure = std::numeric_limits<std::size_t>::max();
};

bool delivery_sink(const char* json, void* context) {
    auto* sink = static_cast<DeliverySink*>(context);
    if (!sink->accepting || sink->sends_before_failure == 0) {
        return false;
    }
    if (sink->sends_before_failure != std::numeric_limits<std::size_t>::max()) {
        --sink->sends_before_failure;
    }
    sink->messages.emplace_back(json);
    return true;
}

void test_delivery_recovery_and_feedback() {
    smartgear::NetEventDelivery delivery;
    DeliverySink sink;
    const auto first = beam(70'000, 71'000, 1, 0, 0);
    const auto second = beam(72'000, 73'000, 1U << 1, 1, 1);

    smartgear::NetEvent first_event;
    first_event.event_id = "first";
    first_event.timestamp_us = first.start_us;
    first_event.state = smartgear::NetState::kCleanOver;
    smartgear::NetEvent second_event;
    second_event.event_id = "second";
    second_event.timestamp_us = second.start_us;
    second_event.state = smartgear::NetState::kTouchOver;

    require(!delivery.publish(first_event), "disconnected event must be cached");
    require(!delivery.publish(second_event), "second disconnected event must be cached");
    require(delivery.cached_count() == 2, "two events must be cached");
    delivery.set_transport(true, delivery_sink, &sink);
    require(delivery.cached_count() == 0,
            "connected transport must flush the cache");
    require(sink.messages.size() == 2,
            "recovery must send both cached events");
    require(sink.messages[0].find("first") != std::string::npos &&
                sink.messages[1].find("second") != std::string::npos,
            "recovery order must be stable");

    DeliverySink flaky_sink;
    flaky_sink.accepting = false;
    smartgear::NetEventDelivery flaky_delivery;
    flaky_delivery.set_transport(true, delivery_sink, &flaky_sink);
    smartgear::NetEvent failed_event;
    failed_event.event_id = "failed-send";
    require(!flaky_delivery.publish(failed_event),
            "failed transport send must cache the event");
    require(!flaky_delivery.connected() && flaky_delivery.cached_count() == 1,
            "failed send must disarm transport while preserving the event");
    flaky_sink.accepting = true;
    flaky_delivery.set_transport(true, delivery_sink, &flaky_sink);
    require(flaky_delivery.cached_count() == 0 &&
                flaky_sink.messages.size() == 1 &&
                flaky_sink.messages[0].find("failed-send") != std::string::npos,
            "re-arming transport must flush the failed event exactly once");

    DeliverySink mid_flush_sink;
    mid_flush_sink.sends_before_failure = 1;
    smartgear::NetEventDelivery mid_flush_delivery;
    smartgear::NetEvent queued_first;
    queued_first.event_id = "queued-first";
    smartgear::NetEvent queued_second;
    queued_second.event_id = "queued-second";
    require(!mid_flush_delivery.publish(queued_first) &&
                !mid_flush_delivery.publish(queued_second),
            "mid-flush events must begin in the disconnected cache");
    mid_flush_delivery.set_transport(true, delivery_sink, &mid_flush_sink);
    require(!mid_flush_delivery.connected() &&
                mid_flush_delivery.cached_count() == 1 &&
                mid_flush_sink.messages.size() == 1 &&
                mid_flush_sink.messages[0].find("queued-first") != std::string::npos,
            "a flush failure must retain the first unsent cached event");
    smartgear::NetEvent queued_after_failure;
    queued_after_failure.event_id = "queued-after-failure";
    require(!mid_flush_delivery.publish(queued_after_failure) &&
                mid_flush_delivery.cached_count() == 2,
            "new events must follow a cached flush failure");
    mid_flush_sink.sends_before_failure = std::numeric_limits<std::size_t>::max();
    mid_flush_delivery.set_transport(true, delivery_sink, &mid_flush_sink);
    require(mid_flush_delivery.cached_count() == 0 &&
                mid_flush_sink.messages.size() == 3 &&
                mid_flush_sink.messages[1].find("queued-second") != std::string::npos &&
                mid_flush_sink.messages[2].find("queued-after-failure") !=
                    std::string::npos,
            "recovery must resume cached delivery without reordering or duplication");

    smartgear::NetEventDelivery bounded;
    for (std::size_t index = 0;
         index < smartgear::config::kEventCacheCapacity + 2; ++index) {
        smartgear::NetEvent cached;
        cached.event_id = "cached-" + std::to_string(index);
        require(!bounded.publish(cached),
                "disconnected bounded delivery must cache every event");
    }
    require(bounded.cached_count() == smartgear::config::kEventCacheCapacity &&
                bounded.dropped_count() == 2,
            "bounded delivery must report overwritten oldest events");
    DeliverySink bounded_sink;
    bounded.set_transport(true, delivery_sink, &bounded_sink);
    require(bounded_sink.messages.size() == smartgear::config::kEventCacheCapacity &&
                bounded_sink.messages.front().find("cached-2") != std::string::npos,
            "bounded delivery must flush the newest events in order");

    require(smartgear::feedback_for(smartgear::NetState::kCleanOver).led_green,
            "clean_over must use green feedback");
    require(smartgear::feedback_for(smartgear::NetState::kTouchOver).led_red &&
                smartgear::feedback_for(smartgear::NetState::kTouchOver).led_green,
            "touch_over must use yellow feedback");
    require(smartgear::feedback_for(smartgear::NetState::kTouchNoCross).led_red,
            "touch_no_cross must use red feedback");
}

void test_ring_buffer() {
    smartgear::RingBuffer<int, 2> cache;
    require(cache.push(1), "first cache push should not overwrite");
    require(cache.push(2), "second cache push should not overwrite");
    require(!cache.push(3), "third cache push should overwrite oldest");
    require(cache.dropped_count() == 1, "cache drop count is wrong");
    int value = 0;
    require(cache.pop(value) && value == 2, "cache must retain newest order");
    require(cache.pop(value) && value == 3, "cache must retain newest event");
    require(!cache.pop(value), "empty cache pop must fail");
}

void test_pin_mapping_contract() {
    using namespace smartgear::config;
    require(kAllBeamMask == 0x03ffU, "ten optical channels must fit the beam mask");
    require(all_gpio_numbers_valid(kBeamGpioPins) &&
                all_gpio_numbers_valid(kPiezoComparatorGpioPins) &&
                all_gpio_numbers_valid(kPiezoAdcGpioPins) &&
                all_gpio_numbers_valid(kFeedbackGpioPins),
            "all placeholder pins must be valid ESP32-S3 GPIO numbers");
    require(all_unique(kBeamGpioPins) && all_unique(kPiezoComparatorGpioPins) &&
                all_unique(kPiezoAdcGpioPins) && all_unique(kFeedbackGpioPins),
            "each hardware group must have unique pins");
    require(disjoint(kBeamGpioPins, kPiezoComparatorGpioPins) &&
                disjoint(kBeamGpioPins, kPiezoAdcGpioPins) &&
                disjoint(kBeamGpioPins, kFeedbackGpioPins) &&
                disjoint(kPiezoComparatorGpioPins, kPiezoAdcGpioPins) &&
                disjoint(kPiezoComparatorGpioPins, kFeedbackGpioPins) &&
                disjoint(kPiezoAdcGpioPins, kFeedbackGpioPins),
            "placeholder sensor and feedback pins must not overlap");
}

void print_schema_events() {
    smartgear::NetEventAggregator aggregator;
    aggregator.set_calibration("cal-schema", true);
    aggregator.on_beam(beam(50'000, 51'000, 1U << 9, 9, 9));
    aggregator.poll(296'001);
    smartgear::NetEvent event;
    require(aggregator.pop_event(event), "schema event missing");
    std::cout << "JSON_EVENT " << smartgear::net_event_to_json(event) << '\n';

    smartgear::NetEventAggregator touch_aggregator;
    touch_aggregator.set_calibration("cal-schema", true);
    touch_aggregator.on_touch(touch(60'000, 60'500, 3));
    touch_aggregator.poll(200'501);
    require(touch_aggregator.pop_event(event), "touch schema event missing");
    std::cout << "JSON_EVENT " << smartgear::net_event_to_json(event) << '\n';
}

}  // namespace

int main() {
    try {
        test_beam_capture();
        test_each_beam_channel_independently();
        test_piezo_merge();
        test_clean_over_and_height_interval();
        test_every_beam_mask_interval();
        test_touch_over_before_and_after_beam();
        test_touch_no_cross_and_unknown();
        test_sequential_and_overlapping_events();
        test_waveform_window();
        test_waveform_timeout_flush();
        test_piezo_feature_extraction();
        test_waveform_archive();
        test_waveform_hook_contract();
        test_sensor_health_quality_flags();
        test_channel_self_test_and_baseline();
        test_sensor_health_gate_pipeline();
        test_sensor_pipeline_end_to_end();
        test_trigger_before_dma_dispatch_pipeline();
        test_input_shape_and_deadline_safety();
        test_delivery_recovery_and_feedback();
        test_ring_buffer();
        test_pin_mapping_contract();
        print_schema_events();
        std::cout << "HOST_TESTS_OK\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "HOST_TESTS_FAILED: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
