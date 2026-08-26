#include "m6_carrier_adapter.h"

#include <limits>

#include "net_sensor_config.h"

namespace smartgear {

M6CarrierBeamAdapter::M6CarrierBeamAdapter(
    BeamCapture& capture,
    const std::int64_t carrier_to_host_offset_us)
    : capture_(capture), carrier_to_host_offset_us_(carrier_to_host_offset_us) {}

M6CarrierFrameResult M6CarrierBeamAdapter::ingest(
    const M6CarrierFrame& input_frame) {
    M6CarrierFrameResult result;
    M6CarrierFrame frame = input_frame;
    const bool sequence_contiguous = sequence_tracker_.apply(frame);
    const std::uint8_t fatal_flags = static_cast<std::uint8_t>(
        kM6CarrierFlagFifoOverflow | kM6CarrierFlagTimestampInvalid |
        kM6CarrierFlagSequenceGap);
    if (!sequence_contiguous ||
        (frame.flags & static_cast<std::uint8_t>(~kM6CarrierKnownWireFlags)) !=
            0U ||
        (frame.flags & fatal_flags) != 0U ||
        frame.edge_count > kM6CarrierMaxEdgesPerFrame) {
        capture_.reset();
        result.input_boundary_valid = false;
        return result;
    }

    std::array<std::uint64_t, kM6CarrierMaxEdgesPerFrame> host_timestamps{};
    for (std::size_t index = 0; index < frame.edge_count; ++index) {
        if (frame.edges[index].channel >= config::kBeamCount ||
            frame.edges[index].level > 1U) {
            capture_.reset();
            result.input_boundary_valid = false;
            return result;
        }
        if (!translate_timestamp(frame.edges[index].timestamp_us,
                                 &host_timestamps[index]) ||
            (index > 0 && host_timestamps[index] < host_timestamps[index - 1])) {
            capture_.reset();
            result.input_boundary_valid = false;
            return result;
        }
    }

    for (std::size_t index = 0; index < frame.edge_count; ++index) {
        const M6CarrierEdge& edge = frame.edges[index];
        const bool blocked = config::beam_blocked_at_level(
            config::kBeamInputPolarity, edge.level);
        if (auto observation = capture_.on_edge(
                edge.channel, blocked, host_timestamps[index])) {
            result.observations[result.observation_count++] = *observation;
        }
    }
    return result;
}

std::optional<BeamObservation> M6CarrierBeamAdapter::poll(
    const std::uint64_t host_timestamp_us) {
    return capture_.poll(host_timestamp_us);
}

void M6CarrierBeamAdapter::set_clock_offset(
    const std::int64_t carrier_to_host_offset_us) {
    if (carrier_to_host_offset_us_ == carrier_to_host_offset_us) {
        return;
    }
    carrier_to_host_offset_us_ = carrier_to_host_offset_us;
    // A partial blocked/unblocked pair translated with the old offset must
    // never be joined to an edge translated with the new one.
    capture_.reset();
    sequence_tracker_.reset();
}

void M6CarrierBeamAdapter::reset_sequence() {
    sequence_tracker_.reset();
}

bool M6CarrierBeamAdapter::translate_timestamp(
    const std::uint64_t carrier_timestamp_us,
    std::uint64_t* host_timestamp_us) const {
    if (host_timestamp_us == nullptr) {
        return false;
    }
    if (carrier_to_host_offset_us_ >= 0) {
        const auto offset = static_cast<std::uint64_t>(
            carrier_to_host_offset_us_);
        if (carrier_timestamp_us >
            std::numeric_limits<std::uint64_t>::max() - offset) {
            return false;
        }
        *host_timestamp_us = carrier_timestamp_us + offset;
        return true;
    }

    // Avoid negating INT64_MIN directly.
    const auto magnitude = static_cast<std::uint64_t>(
        -(carrier_to_host_offset_us_ + 1)) + 1U;
    if (carrier_timestamp_us < magnitude) {
        return false;
    }
    *host_timestamp_us = carrier_timestamp_us - magnitude;
    return true;
}

}  // namespace smartgear
