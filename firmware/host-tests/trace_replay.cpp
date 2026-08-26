#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "beam_capture.h"
#include "beam_channel_map.h"
#include "net_event.h"
#include "net_event_aggregator.h"
#include "piezo_capture.h"
#include "piezo_waveform.h"

namespace {

struct TraceRow {
    std::uint64_t timestamp_us = 0;
    std::string kind;
    std::uint8_t channel = 0;
    int value = 0;
};

void require(const bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

TraceRow parse_row(const std::string& line, const std::size_t line_number) {
    std::stringstream input(line);
    std::string field;
    TraceRow row;
    require(static_cast<bool>(std::getline(input, field, ',')),
            "trace line " + std::to_string(line_number) + " has no timestamp");
    row.timestamp_us = std::stoull(field);
    require(static_cast<bool>(std::getline(input, row.kind, ',')),
            "trace line " + std::to_string(line_number) + " has no kind");
    require(static_cast<bool>(std::getline(input, field, ',')),
            "trace line " + std::to_string(line_number) + " has no channel");
    row.channel = static_cast<std::uint8_t>(std::stoul(field));
    require(static_cast<bool>(std::getline(input, field)),
            "trace line " + std::to_string(line_number) + " has no value");
    row.value = std::stoi(field);
    return row;
}

class TraceReplay {
  public:
    TraceReplay()
        : beam_capture_(5'000, 250'000),
          piezo_capture_(5'000, 120'000),
          waveform_capture_({1'000, 2, 3}) {
        aggregator_.set_calibration("trace-calibration", true);
        aggregator_.set_beam_health(0x03ffU, true);
        aggregator_.set_piezo_baseline(true);
        waveform_capture_.feed_sample(0, 100, 0);
        waveform_capture_.feed_sample(1, 200, 0);
        waveform_capture_.feed_sample(0, 101, 1'000);
        waveform_capture_.feed_sample(1, 201, 1'000);
    }

    void seed_waveform_prehistory(const std::uint64_t trigger_us) {
        constexpr std::uint64_t kFirstSampleOffsetUs = 2'000U;
        constexpr std::uint64_t kSecondSampleOffsetUs = 1'000U;
        if (trigger_us < kFirstSampleOffsetUs) {
            // There is no representable two-sample prehistory before this
            // trace timestamp. Leave the rolling history untouched so the
            // resulting frame remains explicitly incomplete.
            return;
        }
        waveform_capture_.feed_sample(0, 100,
                                       trigger_us - kFirstSampleOffsetUs);
        waveform_capture_.feed_sample(1, 200,
                                       trigger_us - kFirstSampleOffsetUs);
        waveform_capture_.feed_sample(0, 101,
                                       trigger_us - kSecondSampleOffsetUs);
        waveform_capture_.feed_sample(1, 201,
                                       trigger_us - kSecondSampleOffsetUs);
    }

    void apply(const TraceRow& row) {
        require(row.timestamp_us >= last_timestamp_us_,
                "trace timestamps must be monotonic");
        last_timestamp_us_ = row.timestamp_us;
        if (row.kind == "beam") {
            if (auto observation = beam_capture_.on_edge(
                    row.channel, row.value != 0, row.timestamp_us)) {
                aggregator_.on_beam(
                    smartgear::remap_configured_beam_observation(*observation));
            }
        } else if (row.kind == "touch") {
            const std::string reference =
                "trace-wave-" + std::to_string(row.timestamp_us);
            const bool should_start_waveform =
                piezo_capture_.will_start_new_observation(row.timestamp_us);
            if (should_start_waveform) {
                // The trace represents a continuously sampled ADC stream.
                // Provide the two samples immediately before this comparator
                // edge instead of reusing history from an earlier, unrelated
                // event. This keeps the replay's pre-trigger evidence inside
                // the waveform capture time window.
                seed_waveform_prehistory(row.timestamp_us);
            }
            const bool waveform_started =
                should_start_waveform &&
                waveform_capture_.start_capture(row.timestamp_us, reference);
            const std::string effective_reference =
                waveform_started ? reference : waveform_capture_.active_reference();
            if (auto observation = piezo_capture_.on_trigger(
                    row.channel, row.timestamp_us, 0.0F, 0.0F,
                    effective_reference.empty() ? "trace-no-waveform"
                                                : effective_reference)) {
                aggregator_.on_touch(*observation);
            }
            if (waveform_started) {
                for (std::uint64_t sample = 0; sample < 3; ++sample) {
                    const std::uint64_t sample_timestamp =
                        row.timestamp_us + sample * 1'000U;
                    waveform_capture_.feed_sample(
                        0, static_cast<std::int16_t>(110 + sample),
                        sample_timestamp);
                    waveform_capture_.feed_sample(
                        1, static_cast<std::int16_t>(220 + sample),
                        sample_timestamp);
                    last_timestamp_us_ =
                        std::max(last_timestamp_us_, sample_timestamp);
                }
                process_ready_waveforms();
            }
        } else {
            require(row.kind == "tick",
                    "unsupported trace kind: " + row.kind);
        }

        advance(row.timestamp_us);
    }

    void finish() { advance(last_timestamp_us_ + 300'000ULL); }

    std::size_t emitted_count() const { return emitted_count_; }

  private:
    void advance(const std::uint64_t timestamp_us) {
        waveform_capture_.expire(timestamp_us);
        process_ready_waveforms();
        if (auto observation = beam_capture_.poll(timestamp_us)) {
            aggregator_.on_beam(
                smartgear::remap_configured_beam_observation(*observation));
        }
        if (auto observation = piezo_capture_.poll(timestamp_us)) {
            aggregator_.on_touch(*observation);
        }
        aggregator_.poll(timestamp_us);
        smartgear::NetEvent event;
        while (aggregator_.pop_event(event)) {
            std::cout << "TRACE_EVENT " << smartgear::net_event_to_json(event)
                      << '\n';
            ++emitted_count_;
        }
    }

    void process_ready_waveforms() {
        while (auto frame = waveform_capture_.take_ready()) {
            const auto features =
                smartgear::extract_piezo_features(*frame, 1'000);
            piezo_capture_.on_waveform_ready(frame->reference, features);
        }
    }

    smartgear::BeamCapture beam_capture_;
    smartgear::PiezoCapture piezo_capture_;
    smartgear::PiezoWaveformCapture waveform_capture_;
    smartgear::NetEventAggregator aggregator_;
    std::uint64_t last_timestamp_us_ = 0;
    std::size_t emitted_count_ = 0;
};

}  // namespace

int main(int argc, char** argv) {
    try {
        require(argc == 2, "usage: net_event_trace <trace.csv>");
        std::ifstream input(argv[1]);
        require(input.is_open(), "cannot open trace file: " + std::string(argv[1]));

        TraceReplay replay;
        std::string line;
        std::size_t line_number = 0;
        while (std::getline(input, line)) {
            ++line_number;
            if (line.empty() || line[0] == '#') {
                continue;
            }
            replay.apply(parse_row(line, line_number));
        }
        replay.finish();
        std::cout << "TRACE_SUMMARY events=" << replay.emitted_count() << '\n';
        require(replay.emitted_count() == 3,
                "reference trace must emit clean_over, touch_over and touch_no_cross");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "TRACE_FAILED: " << error.what() << '\n';
        return 1;
    }
}
