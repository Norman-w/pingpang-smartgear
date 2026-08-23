#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace smartgear {

enum class NetState {
    kCleanOver,
    kTouchOver,
    kTouchNoCross,
    kUnknown,
};

const char* net_state_name(NetState state);

struct NetTouch {
    bool triggered = false;
    std::uint8_t sensor_mask = 0;
    std::array<float, 2> peak = {0.0F, 0.0F};
    std::array<float, 2> energy = {0.0F, 0.0F};
    std::uint64_t duration_us = 0;
    std::string waveform_ref;
};

struct NetEvent {
    std::string type = "net_event";
    std::string schema_version = "0.1";
    std::string event_id;
    std::uint64_t timestamp_us = 0;
    std::string calibration_id = "uncalibrated";
    std::uint16_t beam_mask = 0;
    std::array<int, 2> beam_height_mm = {0, 0};
    std::array<int, 2> ball_bottom_gap_mm = {0, 0};
    NetTouch net_touch;
    NetState state = NetState::kUnknown;
    std::vector<std::string> quality_flags;
};

// 传输层使用的稳定文本表示。业务层不依赖 BLE、Wi-Fi、WebSocket、MQTT 或 SSE。
std::string net_event_to_json(const NetEvent& event);

}  // namespace smartgear
