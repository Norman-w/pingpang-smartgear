#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "beam_capture.h"
#include "feedback.h"
#include "net_event.h"
#include "net_event_aggregator.h"
#include "net_event_delivery.h"
#include "piezo_capture.h"
#include "piezo_waveform.h"
#include "ring_buffer.h"
#include "sensor_self_test.h"

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
    return result;
}

smartgear::NetEvent pop_one(smartgear::NetEventAggregator& aggregator) {
    smartgear::NetEvent event;
    require(aggregator.pop_event(event), "expected one NetEvent");
    require(aggregator.pending_output_count() == 0,
            "expected the output queue to be drained");
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
    smartgear::PiezoCapture capture(5'000);
    capture.on_trigger(0, 1'000, 1.0F, 2.0F, "wave-a");
    capture.on_trigger(1, 3'000, 2.0F, 4.0F, "wave-a");
    auto result = capture.poll(8'001);
    require(result.has_value(), "PVDF event should close after merge window");
    require(result->sensor_mask == 3, "both PVDF channels must be retained");
    require(result->peak[0] == 1.0F && result->peak[1] == 2.0F,
            "PVDF peak values were not retained");
    require(result->energy[0] == 2.0F && result->energy[1] == 4.0F,
            "PVDF energy values were not retained");
    require(result->duration_us == 2'000, "PVDF duration is wrong");
}

void test_clean_over_and_height_interval() {
    smartgear::NetEventAggregator aggregator;
    aggregator.set_calibration("cal-test", true);
    aggregator.on_beam(beam(10'000, 11'000, 0b0000001001, 0, 3));
    aggregator.poll(91'001);
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
}

void test_touch_no_cross_and_unknown() {
    smartgear::NetEventAggregator no_cross;
    no_cross.set_calibration("cal-test", true);
    no_cross.on_touch(touch(30'000, 31'000, 1));
    no_cross.poll(131'001);
    const auto no_cross_event = pop_one(no_cross);
    require(no_cross_event.state == smartgear::NetState::kTouchNoCross,
            "PVDF without beam must become touch_no_cross");
    require(no_cross_event.beam_mask == 0,
            "touch_no_cross must have no beam mask");

    smartgear::NetEventAggregator invalid;
    invalid.set_calibration("pending", false);
    invalid.on_beam(beam(40'000, 41'000, 1, 0, 0));
    invalid.poll(121'001);
    const auto unknown_event = pop_one(invalid);
    require(unknown_event.state == smartgear::NetState::kUnknown,
            "invalid calibration must force unknown state");
    require(!unknown_event.quality_flags.empty(),
            "unknown event must explain its quality failure");
}

void test_sequential_and_overlapping_events() {
    smartgear::NetEventAggregator sequential;
    sequential.set_calibration("cal-test", true);
    sequential.on_beam(beam(200'000, 201'000, 1, 0, 0));
    sequential.poll(281'001);
    sequential.on_beam(beam(300'000, 301'000, 1U << 2, 2, 2));
    sequential.poll(381'001);
    smartgear::NetEvent first;
    smartgear::NetEvent second;
    require(sequential.pop_event(first) && sequential.pop_event(second),
            "two separated beam events must be emitted");
    require(sequential.pending_output_count() == 0,
            "sequential event output must be drained");
    require(first.state == smartgear::NetState::kCleanOver &&
                second.state == smartgear::NetState::kCleanOver,
            "separated single-ball events must remain separate");

    smartgear::NetEventAggregator overlapping;
    overlapping.set_calibration("cal-test", true);
    overlapping.on_beam(beam(400'000, 401'000, 1, 0, 0));
    overlapping.on_beam(beam(400'500, 401'500, 2, 1, 1));
    const auto unknown = pop_one(overlapping);
    require(unknown.state == smartgear::NetState::kUnknown,
            "overlapping beam events must not be silently merged");

    smartgear::NetEventAggregator unmatched({20'000, 80'000, 200'000});
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
}

void test_waveform_window() {
    smartgear::PiezoWaveformCapture capture({1'000, 20, 30});
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
        capture.feed_sample(0, static_cast<std::int16_t>(200 + sample), sample);
        capture.feed_sample(1, static_cast<std::int16_t>(300 + sample), sample);
    }
    require(capture.ready(), "waveform capture should become ready");
    auto frame = capture.take_ready();
    require(frame.has_value(), "ready waveform frame should be available");
    require(frame->samples[0].size() == 50 && frame->samples[1].size() == 50,
            "each channel must contain pre+post samples");
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
        partial.feed_sample(0, static_cast<std::int16_t>(30 + sample), sample);
        partial.feed_sample(1, static_cast<std::int16_t>(40 + sample), sample);
    }
    auto partial_frame = partial.take_ready();
    require(partial_frame.has_value(), "partial history waveform should complete");
    require(partial_frame->samples[0][0] == 0 &&
                partial_frame->samples[0][1] == 0 &&
                partial_frame->samples[0][2] == 0 &&
                partial_frame->samples[0][3] == 11 &&
                partial_frame->samples[0][4] == 12,
            "partial pre-trigger history must be zero-filled chronologically");
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

    const smartgear::PiezoQuietBaseline quiet{{0.2F, 0.3F}, {0.1F, 0.1F}, 1600};
    require(smartgear::piezo_baseline_is_quiet(quiet, 0.5F, 0.2F),
            "quiet PVDF baseline should pass");
    const smartgear::PiezoQuietBaseline noisy{{0.8F, 0.3F}, {0.1F, 0.1F}, 1600};
    require(!smartgear::piezo_baseline_is_quiet(noisy, 0.5F, 0.2F),
            "noisy PVDF baseline should fail");
}

struct DeliverySink {
    std::vector<std::string> messages;
    bool accepting = true;
};

bool delivery_sink(const char* json, void* context) {
    auto* sink = static_cast<DeliverySink*>(context);
    if (!sink->accepting) {
        return false;
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

void print_schema_events() {
    smartgear::NetEventAggregator aggregator;
    aggregator.set_calibration("cal-schema", true);
    aggregator.on_beam(beam(50'000, 51'000, 1U << 9, 9, 9));
    aggregator.poll(131'001);
    smartgear::NetEvent event;
    require(aggregator.pop_event(event), "schema event missing");
    std::cout << "JSON_EVENT " << smartgear::net_event_to_json(event) << '\n';

    smartgear::NetEventAggregator touch_aggregator;
    touch_aggregator.set_calibration("cal-schema", true);
    touch_aggregator.on_touch(touch(60'000, 60'500, 3));
    touch_aggregator.poll(160'501);
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
        test_touch_over_before_and_after_beam();
        test_touch_no_cross_and_unknown();
        test_sequential_and_overlapping_events();
        test_waveform_window();
        test_channel_self_test_and_baseline();
        test_delivery_recovery_and_feedback();
        test_ring_buffer();
        print_schema_events();
        std::cout << "HOST_TESTS_OK\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "HOST_TESTS_FAILED: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
