#pragma once

#include <array>
#include <cstdint>
#include <optional>

#include "beam_capture.h"
#include "m6_carrier_config.h"
#include "m6_carrier_protocol.h"

namespace smartgear {

struct M6CarrierFrameResult {
    bool input_boundary_valid = true;
    std::uint8_t observation_count = 0;
    std::array<BeamObservation, kM6CarrierMaxEdgesPerFrame> observations{};
};

// Pure business-side adapter. A board-specific SPI task can feed decoded
// frames here without putting bus parsing, clock conversion, or sequence
// handling into BeamCapture itself.
class M6CarrierBeamAdapter {
  public:
    M6CarrierBeamAdapter(BeamCapture& capture,
                         std::int64_t carrier_to_host_offset_us);

    M6CarrierFrameResult ingest(const M6CarrierFrame& frame);
    std::optional<BeamObservation> poll(std::uint64_t host_timestamp_us);
    // Clock calibration is a runtime boundary. Changing it discards the
    // partial event and sequence state that was built in the old time domain.
    void set_clock_offset(std::int64_t carrier_to_host_offset_us);
    std::int64_t clock_offset_us() const {
        return carrier_to_host_offset_us_;
    }
    void reset_sequence();

  private:
    bool translate_timestamp(std::uint64_t carrier_timestamp_us,
                             std::uint64_t* host_timestamp_us) const;

    BeamCapture& capture_;
    std::int64_t carrier_to_host_offset_us_;
    M6CarrierSequenceTracker sequence_tracker_;
};

}  // namespace smartgear
