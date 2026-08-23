#include "net_event.h"

#include <iomanip>
#include <sstream>

namespace smartgear {
namespace {

std::string escape_json(const std::string& value) {
    std::ostringstream out;
    for (const char character : value) {
        switch (character) {
            case '"':
                out << "\\\"";
                break;
            case '\\':
                out << "\\\\";
                break;
            case '\b':
                out << "\\b";
                break;
            case '\f':
                out << "\\f";
                break;
            case '\n':
                out << "\\n";
                break;
            case '\r':
                out << "\\r";
                break;
            case '\t':
                out << "\\t";
                break;
            default:
                if (static_cast<unsigned char>(character) < 0x20U) {
                    out << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                        << static_cast<int>(static_cast<unsigned char>(character))
                        << std::dec << std::setfill(' ');
                } else {
                    out << character;
                }
                break;
        }
    }
    return out.str();
}

template <typename T>
void append_array(std::ostringstream& out, const std::array<T, 2>& values) {
    out << '[' << values[0] << ',' << values[1] << ']';
}

void append_float_array(std::ostringstream& out,
                        const std::array<float, 2>& values) {
    out << '[' << std::fixed << std::setprecision(4) << values[0] << ','
        << values[1] << ']';
}

}  // namespace

const char* net_state_name(const NetState state) {
    switch (state) {
        case NetState::kCleanOver:
            return "clean_over";
        case NetState::kTouchOver:
            return "touch_over";
        case NetState::kTouchNoCross:
            return "touch_no_cross";
        case NetState::kUnknown:
        default:
            return "unknown";
    }
}

std::string net_event_to_json(const NetEvent& event) {
    std::ostringstream out;
    out << "{"
        << "\"type\":\"" << escape_json(event.type) << "\","
        << "\"schema_version\":\"" << escape_json(event.schema_version)
        << "\","
        << "\"event_id\":\"" << escape_json(event.event_id) << "\","
        << "\"timestamp_us\":" << event.timestamp_us << ","
        << "\"calibration_id\":\"" << escape_json(event.calibration_id)
        << "\","
        << "\"beam_mask\":" << event.beam_mask << ","
        << "\"beam_height_mm\":";
    append_array(out, event.beam_height_mm);
    out << ",\"ball_bottom_gap_mm\":";
    append_array(out, event.ball_bottom_gap_mm);
    out << ",\"net_touch\":{";
    out << "\"triggered\":" << (event.net_touch.triggered ? "true" : "false")
        << ",\"sensor_mask\":"
        << static_cast<unsigned int>(event.net_touch.sensor_mask)
        << ",\"peak\":";
    append_float_array(out, event.net_touch.peak);
    out << ",\"energy\":";
    append_float_array(out, event.net_touch.energy);
    out << ",\"duration_us\":" << event.net_touch.duration_us
        << ",\"waveform_ref\":\""
        << escape_json(event.net_touch.waveform_ref) << "\"},"
        << "\"state\":\"" << net_state_name(event.state) << "\","
        << "\"quality_flags\":[";
    for (std::size_t index = 0; index < event.quality_flags.size(); ++index) {
        if (index != 0) {
            out << ',';
        }
        out << '"' << escape_json(event.quality_flags[index]) << '"';
    }
    out << "]}";
    return out.str();
}

}  // namespace smartgear
