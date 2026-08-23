#pragma once

#include <cstdint>

#include "net_event.h"

namespace smartgear {

enum class FeedbackPattern {
    kGreenShort,
    kYellowDouble,
    kRedDouble,
    kPurpleSlow,
};

struct FeedbackCommand {
    FeedbackPattern pattern = FeedbackPattern::kPurpleSlow;
    bool led_red = false;
    bool led_green = false;
    bool led_blue = false;
    std::uint16_t buzzer_on_ms = 0;
    std::uint16_t buzzer_gap_ms = 0;
    std::uint8_t repeat_count = 0;
};

FeedbackCommand feedback_for(NetState state);
const char* feedback_pattern_name(FeedbackPattern pattern);

}  // namespace smartgear
