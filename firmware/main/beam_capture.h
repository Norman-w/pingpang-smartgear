#pragma once

#include <cstdint>
#include <optional>

namespace smartgear {

struct BeamObservation {
    bool valid = false;
    bool timed_out = false;
    std::uint64_t start_us = 0;
    std::uint64_t end_us = 0;
    std::uint16_t beam_mask = 0;
    std::uint8_t min_index = 0;
    std::uint8_t max_index = 0;
};

class BeamCapture {
  public:
    explicit BeamCapture(std::uint64_t quiet_us, std::uint64_t max_event_us);

    // blocked=true 表示该通道当前被球/遮挡物打断。
    std::optional<BeamObservation> on_edge(std::uint8_t channel,
                                            bool blocked,
                                            std::uint64_t timestamp_us);
    // 用于在全部光束恢复后等待安静时间，并处理超长事件。
    std::optional<BeamObservation> poll(std::uint64_t timestamp_us);
    void reset();

  private:
    std::optional<BeamObservation> finish(std::uint64_t timestamp_us,
                                          bool timed_out);

    std::uint64_t quiet_us_;
    std::uint64_t max_event_us_;
    bool active_ = false;
    std::uint16_t active_mask_ = 0;
    std::uint16_t latched_mask_ = 0;
    std::uint64_t start_us_ = 0;
    std::uint64_t last_change_us_ = 0;
    // Keep the last observed/polled stream boundary across event resets so a
    // late GPIO edge cannot be mistaken for a fresh valid ball path.
    std::uint64_t stream_last_timestamp_us_ = 0;
    bool stream_has_timestamp_ = false;
    bool timestamp_order_valid_ = true;
};

}  // namespace smartgear
