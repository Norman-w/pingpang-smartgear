#pragma once

#ifdef ESP_PLATFORM

#include <cstdint>

#include "driver/gpio.h"
#include "esp_err.h"

#include "feedback.h"

namespace smartgear {

struct FeedbackGpioConfig {
    gpio_num_t red = GPIO_NUM_16;
    gpio_num_t green = GPIO_NUM_17;
    gpio_num_t blue = GPIO_NUM_18;
    gpio_num_t buzzer = GPIO_NUM_19;
};

class FeedbackGpio {
  public:
    explicit FeedbackGpio(FeedbackGpioConfig config = {}) : config_(config) {}

    esp_err_t init();
    void start(const FeedbackCommand& command, std::uint64_t now_us);
    void tick(std::uint64_t now_us);

  private:
    void set_led(const FeedbackCommand& command);
    void set_buzzer(bool enabled);

    FeedbackGpioConfig config_;
    FeedbackCommand command_;
    std::uint8_t remaining_repeats_ = 0;
    std::uint64_t next_transition_us_ = 0;
    bool active_ = false;
    bool buzzer_on_ = false;
};

}  // namespace smartgear

#endif  // ESP_PLATFORM
