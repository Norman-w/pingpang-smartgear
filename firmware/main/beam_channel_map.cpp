#include "beam_channel_map.h"

namespace smartgear {

std::uint16_t remap_beam_mask(
    const std::uint16_t input_mask,
    const std::array<std::uint8_t, config::kBeamCount>& logical_index_by_input) {
    std::uint16_t logical_mask = 0;
    for (std::uint8_t input_index = 0; input_index < config::kBeamCount;
         ++input_index) {
        if ((input_mask & (static_cast<std::uint16_t>(1U) << input_index)) == 0) {
            continue;
        }
        const std::uint8_t logical_index = logical_index_by_input[input_index];
        if (logical_index < config::kBeamCount) {
            logical_mask = static_cast<std::uint16_t>(
                logical_mask | (static_cast<std::uint16_t>(1U) << logical_index));
        }
    }
    return logical_mask;
}

BeamObservation remap_beam_observation(
    const BeamObservation& observation,
    const std::array<std::uint8_t, config::kBeamCount>& logical_index_by_input) {
    BeamObservation mapped = observation;
    if (!observation.valid) {
        mapped.beam_mask = remap_beam_mask(observation.beam_mask,
                                           logical_index_by_input);
        return mapped;
    }

    if ((observation.beam_mask & static_cast<std::uint16_t>(~config::kAllBeamMask)) !=
        0) {
        mapped.valid = false;
        mapped.beam_mask = 0;
        mapped.min_index = 0;
        mapped.max_index = 0;
        return mapped;
    }

    mapped.beam_mask = remap_beam_mask(observation.beam_mask,
                                       logical_index_by_input);
    if (mapped.beam_mask == 0) {
        mapped.valid = false;
        mapped.min_index = 0;
        mapped.max_index = 0;
        return mapped;
    }

    bool found = false;
    for (std::uint8_t logical_index = 0; logical_index < config::kBeamCount;
         ++logical_index) {
        if ((mapped.beam_mask &
             (static_cast<std::uint16_t>(1U) << logical_index)) == 0) {
            continue;
        }
        if (!found) {
            mapped.min_index = logical_index;
            found = true;
        }
        mapped.max_index = logical_index;
    }
    return mapped;
}

BeamObservation remap_configured_beam_observation(
    const BeamObservation& observation) {
    return remap_beam_observation(observation,
                                  config::kBeamLogicalIndexByInput);
}

}  // namespace smartgear
