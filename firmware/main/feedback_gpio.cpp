#ifdef ESP_PLATFORM

#include "feedback_gpio.h"

namespace smartgear {

esp_err_t FeedbackGpio::init() {
    const std::uint64_t mask =
        (1ULL << config_.red) | (1ULL << config_.green) |
        (1ULL << config_.blue) | (1ULL << config_.buzzer);
    gpio_config_t output{};
    output.pin_bit_mask = mask;
    output.mode = GPIO_MODE_OUTPUT;
    output.pull_up_en = GPIO_PULLUP_DISABLE;
    output.pull_down_en = GPIO_PULLDOWN_DISABLE;
    output.intr_type = GPIO_INTR_DISABLE;
    const esp_err_t error = gpio_config(&output);
    if (error != ESP_OK) {
        return error;
    }
    gpio_set_level(config_.red, 0);
    gpio_set_level(config_.green, 0);
    gpio_set_level(config_.blue, 0);
    gpio_set_level(config_.buzzer, 0);
    return ESP_OK;
}

void FeedbackGpio::start(const FeedbackCommand& command,
                         const std::uint64_t now_us) {
    command_ = command;
    remaining_repeats_ = command.repeat_count;
    active_ = remaining_repeats_ > 0;
    buzzer_on_ = active_;
    set_led(command_);
    set_buzzer(buzzer_on_);
    next_transition_us_ =
        now_us + static_cast<std::uint64_t>(command.buzzer_on_ms) * 1'000ULL;
}

void FeedbackGpio::tick(const std::uint64_t now_us) {
    if (!active_ || now_us < next_transition_us_) {
        return;
    }
    if (buzzer_on_) {
        buzzer_on_ = false;
        set_buzzer(false);
        next_transition_us_ =
            now_us + static_cast<std::uint64_t>(command_.buzzer_gap_ms) * 1'000ULL;
        return;
    }

    if (remaining_repeats_ > 0) {
        --remaining_repeats_;
    }
    if (remaining_repeats_ == 0) {
        active_ = false;
        return;
    }
    buzzer_on_ = true;
    set_buzzer(true);
    next_transition_us_ =
        now_us + static_cast<std::uint64_t>(command_.buzzer_on_ms) * 1'000ULL;
}

void FeedbackGpio::set_led(const FeedbackCommand& command) {
    gpio_set_level(config_.red, command.led_red ? 1 : 0);
    gpio_set_level(config_.green, command.led_green ? 1 : 0);
    gpio_set_level(config_.blue, command.led_blue ? 1 : 0);
}

void FeedbackGpio::set_buzzer(const bool enabled) {
    gpio_set_level(config_.buzzer, enabled ? 1 : 0);
}

}  // namespace smartgear

#endif  // ESP_PLATFORM
