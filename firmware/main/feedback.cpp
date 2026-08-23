#include "feedback.h"

namespace smartgear {

FeedbackCommand feedback_for(const NetState state) {
    switch (state) {
        case NetState::kCleanOver:
            return {FeedbackPattern::kGreenShort, false, true, false, 60, 0, 1};
        case NetState::kTouchOver:
            return {FeedbackPattern::kYellowDouble, true, true, false, 80, 80, 2};
        case NetState::kTouchNoCross:
            return {FeedbackPattern::kRedDouble, true, false, false, 120, 100, 2};
        case NetState::kUnknown:
        default:
            return {FeedbackPattern::kPurpleSlow, true, false, true, 200, 150, 3};
    }
}

const char* feedback_pattern_name(const FeedbackPattern pattern) {
    switch (pattern) {
        case FeedbackPattern::kGreenShort:
            return "green_short";
        case FeedbackPattern::kYellowDouble:
            return "yellow_double";
        case FeedbackPattern::kRedDouble:
            return "red_double";
        case FeedbackPattern::kPurpleSlow:
        default:
            return "purple_slow";
    }
}

}  // namespace smartgear
