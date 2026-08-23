#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "beam_capture.h"
#include "net_event.h"
#include "net_event_aggregator.h"
#include "piezo_capture.h"

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
        : beam_capture_(5'000, 250'000), piezo_capture_(5'000, 120'000) {
        aggregator_.set_calibration("trace-calibration", true);
        aggregator_.set_beam_health(0x03ffU, true);
        aggregator_.set_piezo_baseline(true);
    }

    void apply(const TraceRow& row) {
        require(row.timestamp_us >= last_timestamp_us_,
                "trace timestamps must be monotonic");
        last_timestamp_us_ = row.timestamp_us;
        if (row.kind == "beam") {
            if (auto observation = beam_capture_.on_edge(
                    row.channel, row.value != 0, row.timestamp_us)) {
                aggregator_.on_beam(*observation);
            }
        } else if (row.kind == "touch") {
            const std::string reference =
                "trace-wave-" + std::to_string(row.timestamp_us);
            if (auto observation = piezo_capture_.on_trigger(
                    row.channel, row.timestamp_us, 0.0F, 0.0F, reference)) {
                aggregator_.on_touch(*observation);
            }
            smartgear::PiezoFeatureSummary features;
            features.peak[row.channel] = 6.0F;
            features.energy[row.channel] = 36.0F;
            features.duration_us = 500;
            features.complete = true;
            piezo_capture_.on_waveform_ready(reference, features);
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
        if (auto observation = beam_capture_.poll(timestamp_us)) {
            aggregator_.on_beam(*observation);
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

    smartgear::BeamCapture beam_capture_;
    smartgear::PiezoCapture piezo_capture_;
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
