#pragma once

#include <cstdint>
#include <deque>
#include <optional>
#include <string>

#include "beam_capture.h"
#include "net_event.h"
#include "piezo_capture.h"

namespace smartgear {

struct NetEventAggregatorConfig {
    std::uint64_t touch_association_before_us = 20'000;
    std::uint64_t touch_association_after_us = 120'000;
    std::uint64_t touch_only_timeout_us = 140'000;
};

class NetEventAggregator {
  public:
    explicit NetEventAggregator(NetEventAggregatorConfig config = {});

    void set_calibration(std::string calibration_id, bool valid);
    void on_beam(const BeamObservation& observation);
    void on_touch(const PiezoObservation& observation);
    void poll(std::uint64_t timestamp_us);

    bool pop_event(NetEvent& event);
    std::size_t pending_output_count() const { return output_.size(); }

  private:
    bool touch_matches_beam(const PiezoObservation& touch,
                            const BeamObservation& beam) const;
    NetEvent build_event(const std::optional<BeamObservation>& beam,
                         const std::optional<PiezoObservation>& touch,
                         NetState state,
                         std::string extra_quality_flag = {}) const;
    void emit_pending_beam(NetState state);
    void emit_pending_touch(NetState state);
    void clear_beam_pending();
    void clear_touch_pending();
    void clear_pending();

    NetEventAggregatorConfig config_;
    std::string calibration_id_ = "uncalibrated";
    bool calibration_valid_ = false;
    std::optional<BeamObservation> pending_beam_;
    std::optional<PiezoObservation> pending_touch_;
    std::uint64_t pending_beam_deadline_us_ = 0;
    std::uint64_t pending_touch_deadline_us_ = 0;
    std::uint32_t event_sequence_ = 0;
    std::deque<NetEvent> output_;
};

}  // namespace smartgear
