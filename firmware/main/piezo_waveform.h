#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <optional>
#include <string>
#include <vector>

namespace smartgear {

struct PiezoWaveformConfig {
    std::uint32_t sample_rate_hz = 16'000;
    std::uint32_t pre_trigger_ms = 20;
    std::uint32_t post_trigger_ms = 80;

    std::size_t pre_trigger_samples() const {
        return static_cast<std::size_t>(sample_rate_hz) * pre_trigger_ms / 1'000U;
    }
    std::size_t post_trigger_samples() const {
        return static_cast<std::size_t>(sample_rate_hz) * post_trigger_ms / 1'000U;
    }
};

struct PiezoWaveformFrame {
    std::string reference;
    std::uint64_t trigger_us = 0;
    std::array<std::vector<std::int16_t>, 2> samples;
};

class PiezoWaveformCapture {
  public:
    explicit PiezoWaveformCapture(PiezoWaveformConfig config);

    // ADC1 continuous 解析器按通道把样本交给这里。
    void feed_sample(std::uint8_t channel,
                     std::int16_t sample,
                     std::uint64_t timestamp_us);
    bool start_capture(std::uint64_t trigger_us, const std::string& reference);
    bool active() const { return active_; }
    bool ready() const { return !ready_frames_.empty(); }
    std::size_t ready_count() const { return ready_frames_.size(); }
    std::size_t dropped_ready_count() const { return dropped_ready_count_; }
    std::string active_reference() const;
    std::optional<PiezoWaveformFrame> take_ready();
    void abort();

    const PiezoWaveformConfig& config() const { return config_; }

  private:
    void snapshot_pre_trigger();
    bool all_post_samples_written() const;

    PiezoWaveformConfig config_;
    std::array<std::vector<std::int16_t>, 2> history_;
    std::array<std::size_t, 2> history_cursor_ = {0, 0};
    std::array<std::size_t, 2> history_count_ = {0, 0};
    std::array<std::size_t, 2> post_written_ = {0, 0};
    std::optional<PiezoWaveformFrame> frame_;
    std::deque<PiezoWaveformFrame> ready_frames_;
    std::size_t dropped_ready_count_ = 0;
    bool active_ = false;
};

}  // namespace smartgear
