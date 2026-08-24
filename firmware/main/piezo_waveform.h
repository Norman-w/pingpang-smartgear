#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <optional>
#include <string>
#include <vector>

#include "piezo_features.h"

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
    std::size_t pre_trigger_samples = 0;
    std::array<std::vector<std::int16_t>, 2> samples;
    std::array<std::size_t, 2> pre_samples_available = {0, 0};
    std::array<std::size_t, 2> post_samples = {0, 0};
    // A frame with an out-of-order sample is retained for diagnostics, but
    // cannot be used as complete waveform evidence. Samples outside the
    // configured window are simply ignored for this frame.
    bool sample_timestamps_valid = true;
    bool complete = false;
};

PiezoFeatureSummary extract_piezo_features(const PiezoWaveformFrame& frame,
                                           std::uint32_t sample_rate_hz);

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
    // Flush a frame whose ADC stream stopped before the complete post window.
    // The partial frame is still archived and its features remain incomplete.
    bool expire(std::uint64_t timestamp_us);
    void abort();

    const PiezoWaveformConfig& config() const { return config_; }

  private:
    void snapshot_pre_trigger();
    bool all_post_samples_written() const;
    void enqueue_current_frame(bool complete);
    void clear_history();
    void record_history(std::uint8_t channel, std::int16_t sample);
    void append_late_pre_trigger_sample(std::uint8_t channel,
                                        std::int16_t sample);

    PiezoWaveformConfig config_;
    std::array<std::vector<std::int16_t>, 2> history_;
    std::array<std::size_t, 2> history_cursor_ = {0, 0};
    std::array<std::size_t, 2> history_count_ = {0, 0};
    std::array<std::size_t, 2> post_written_ = {0, 0};
    std::array<std::uint64_t, 2> frame_last_sample_timestamp_ = {0, 0};
    std::array<bool, 2> frame_has_sample_timestamp_ = {false, false};
    std::optional<PiezoWaveformFrame> frame_;
    std::deque<PiezoWaveformFrame> ready_frames_;
    std::size_t dropped_ready_count_ = 0;
    bool active_ = false;
};

}  // namespace smartgear
