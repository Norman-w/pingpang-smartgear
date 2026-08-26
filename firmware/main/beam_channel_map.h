#pragma once

#include <array>
#include <cstdint>

#include "beam_capture.h"
#include "net_sensor_config.h"

namespace smartgear {

// Convert raw GPIO input bits into logical height bits.  The aggregator and
// health mask both consume the logical representation, so a non-identity
// harness order cannot silently report the wrong height.
std::uint16_t remap_beam_mask(
    std::uint16_t input_mask,
    const std::array<std::uint8_t, config::kBeamCount>& logical_index_by_input);

BeamObservation remap_beam_observation(
    const BeamObservation& observation,
    const std::array<std::uint8_t, config::kBeamCount>& logical_index_by_input);

BeamObservation remap_configured_beam_observation(
    const BeamObservation& observation);

}  // namespace smartgear
