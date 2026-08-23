#pragma once

#include <array>
#include <cstdint>
#include <optional>
#include <string>

namespace smartgear {

struct PiezoObservation {
    bool valid = false;
    bool triggered = false;
    std::uint8_t sensor_mask = 0;
    std::array<float, 2> peak = {0.0F, 0.0F};
    std::array<float, 2> energy = {0.0F, 0.0F};
    std::uint64_t first_trigger_us = 0;
    std::uint64_t last_trigger_us = 0;
    std::uint64_t duration_us = 0;
    std::string waveform_ref;
};

class PiezoCapture {
  public:
    explicit PiezoCapture(std::uint64_t merge_window_us);

    // 比较器 ISR/ADC 业务适配器调用此方法；这里不直接操作 GPIO 或 ADC。
    std::optional<PiezoObservation> on_trigger(
        std::uint8_t channel,
        std::uint64_t timestamp_us,
        float peak,
        float energy,
        const std::string& waveform_ref);
    std::optional<PiezoObservation> poll(std::uint64_t timestamp_us);
    void reset();

  private:
    std::optional<PiezoObservation> finish();

    std::uint64_t merge_window_us_;
    bool pending_ = false;
    PiezoObservation pending_observation_;
};

}  // namespace smartgear
