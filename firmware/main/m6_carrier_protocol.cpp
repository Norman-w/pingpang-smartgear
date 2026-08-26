#include "m6_carrier_protocol.h"

#include <limits>

#include "net_sensor_config.h"

namespace smartgear {
namespace {

constexpr std::size_t kPayloadOffset = kM6CarrierHeaderBytes;
constexpr std::size_t kBaseTimestampOffset = kPayloadOffset + 4;
constexpr std::size_t kRecordsOffset =
    kPayloadOffset + kM6CarrierPayloadFixedBytes;

std::uint16_t read_u16(const std::uint8_t* bytes) {
    return static_cast<std::uint16_t>(bytes[0]) |
           static_cast<std::uint16_t>(static_cast<std::uint16_t>(bytes[1]) << 8U);
}

std::uint32_t read_u32(const std::uint8_t* bytes) {
    return static_cast<std::uint32_t>(bytes[0]) |
           (static_cast<std::uint32_t>(bytes[1]) << 8U) |
           (static_cast<std::uint32_t>(bytes[2]) << 16U) |
           (static_cast<std::uint32_t>(bytes[3]) << 24U);
}

std::uint64_t read_u64(const std::uint8_t* bytes) {
    std::uint64_t value = 0;
    for (std::size_t index = 0; index < 8; ++index) {
        value |= static_cast<std::uint64_t>(bytes[index]) << (index * 8U);
    }
    return value;
}

void write_u16(std::uint8_t* bytes, const std::uint16_t value) {
    bytes[0] = static_cast<std::uint8_t>(value & 0xFFU);
    bytes[1] = static_cast<std::uint8_t>((value >> 8U) & 0xFFU);
}

void write_u32(std::uint8_t* bytes, const std::uint32_t value) {
    for (std::size_t index = 0; index < 4; ++index) {
        bytes[index] = static_cast<std::uint8_t>((value >> (index * 8U)) & 0xFFU);
    }
}

void write_u64(std::uint8_t* bytes, const std::uint64_t value) {
    for (std::size_t index = 0; index < 8; ++index) {
        bytes[index] = static_cast<std::uint8_t>((value >> (index * 8U)) & 0xFFU);
    }
}

bool payload_shape_is_valid(const std::uint16_t payload_size,
                            const std::uint8_t edge_count) {
    return edge_count <= kM6CarrierMaxEdgesPerFrame &&
           payload_size == kM6CarrierPayloadFixedBytes +
                               static_cast<std::size_t>(edge_count) *
                                   kM6CarrierEdgeRecordBytes;
}

}  // namespace

std::uint16_t m6_carrier_crc16(const std::uint8_t* bytes,
                               const std::size_t size) {
    if (bytes == nullptr && size != 0) {
        return 0;
    }
    std::uint16_t crc = 0xFFFFU;
    for (std::size_t index = 0; index < size; ++index) {
        crc ^= static_cast<std::uint16_t>(bytes[index]) << 8U;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000U) != 0U
                      ? static_cast<std::uint16_t>((crc << 1U) ^ 0x1021U)
                      : static_cast<std::uint16_t>(crc << 1U);
        }
    }
    return crc;
}

std::optional<std::int64_t> m6_carrier_estimate_clock_offset(
    const M6CarrierClockSyncSample& sample) {
    if (sample.host_received_us < sample.host_sent_us ||
        sample.carrier_sent_us < sample.carrier_received_us) {
        return std::nullopt;
    }
    const std::uint64_t host_half_rtt =
        (sample.host_received_us - sample.host_sent_us) / 2U;
    const std::uint64_t carrier_half_rtt =
        (sample.carrier_sent_us - sample.carrier_received_us) / 2U;
    if (sample.host_sent_us >
            std::numeric_limits<std::uint64_t>::max() - host_half_rtt ||
        sample.carrier_received_us >
            std::numeric_limits<std::uint64_t>::max() - carrier_half_rtt) {
        return std::nullopt;
    }
    const std::uint64_t host_midpoint = sample.host_sent_us + host_half_rtt;
    const std::uint64_t carrier_midpoint =
        sample.carrier_received_us + carrier_half_rtt;
    if (host_midpoint >= carrier_midpoint) {
        const std::uint64_t difference = host_midpoint - carrier_midpoint;
        if (difference >
            static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max())) {
            return std::nullopt;
        }
        return static_cast<std::int64_t>(difference);
    }
    const std::uint64_t difference = carrier_midpoint - host_midpoint;
    if (difference >
        static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max()) +
            1U) {
        return std::nullopt;
    }
    if (difference ==
        static_cast<std::uint64_t>(std::numeric_limits<std::int64_t>::max()) +
            1U) {
        return std::numeric_limits<std::int64_t>::min();
    }
    return -static_cast<std::int64_t>(difference);
}

namespace {

bool padded_sync_frame_tail_is_zero(const std::uint8_t* bytes,
                                    const std::size_t wire_size,
                                    const std::size_t received_size) {
    if (bytes == nullptr || received_size < wire_size ||
        received_size > kM6CarrierMaxFrameBytes) {
        return false;
    }
    for (std::size_t index = wire_size; index < received_size; ++index) {
        if (bytes[index] != 0U) {
            return false;
        }
    }
    return true;
}

bool sync_frame_header_is_valid(const std::uint8_t* bytes,
                                const std::size_t size,
                                const std::uint8_t frame_type,
                                const std::uint16_t payload_size,
                                const std::size_t wire_size) {
    if (bytes == nullptr ||
        (size != wire_size && size != kM6CarrierMaxFrameBytes) ||
        bytes[0] != kM6CarrierMagic0 || bytes[1] != kM6CarrierMagic1 ||
        bytes[2] != kM6CarrierProtocolVersion || bytes[3] != frame_type ||
        read_u16(bytes + 4) != payload_size || read_u32(bytes + 6) != 0U ||
        m6_carrier_crc16(bytes, wire_size - kM6CarrierFooterBytes) !=
            read_u16(bytes + wire_size - kM6CarrierFooterBytes) ||
        !padded_sync_frame_tail_is_zero(bytes, wire_size, size)) {
        return false;
    }
    return true;
}

}  // namespace

std::size_t m6_carrier_encode_clock_sync_request(
    std::uint8_t* output,
    const std::size_t capacity) {
    if (output == nullptr || capacity < kM6CarrierClockSyncRequestBytes) {
        return 0;
    }
    output[0] = kM6CarrierMagic0;
    output[1] = kM6CarrierMagic1;
    output[2] = kM6CarrierProtocolVersion;
    output[3] = kM6CarrierFrameTypeClockSyncRequest;
    write_u16(output + 4,
              static_cast<std::uint16_t>(
                  kM6CarrierClockSyncRequestPayloadBytes));
    write_u32(output + 6, 0U);
    output[10] = 1U;
    output[11] = 0U;
    output[12] = 0U;
    output[13] = 0U;
    write_u16(output + kM6CarrierClockSyncRequestBytes -
                  kM6CarrierFooterBytes,
              m6_carrier_crc16(
                  output,
                  kM6CarrierClockSyncRequestBytes - kM6CarrierFooterBytes));
    return kM6CarrierClockSyncRequestBytes;
}

bool m6_carrier_decode_clock_sync_request(const std::uint8_t* bytes,
                                          const std::size_t size) {
    if (!sync_frame_header_is_valid(
            bytes, size, kM6CarrierFrameTypeClockSyncRequest,
            static_cast<std::uint16_t>(kM6CarrierClockSyncRequestPayloadBytes),
            kM6CarrierClockSyncRequestBytes)) {
        return false;
    }
    return bytes[10] == 1U && bytes[11] == 0U && bytes[12] == 0U &&
           bytes[13] == 0U;
}

std::size_t m6_carrier_encode_clock_sync_response(
    const M6CarrierClockSyncResponse& response,
    std::uint8_t* output,
    const std::size_t capacity) {
    if (output == nullptr || capacity < kM6CarrierClockSyncResponseBytes) {
        return 0;
    }
    output[0] = kM6CarrierMagic0;
    output[1] = kM6CarrierMagic1;
    output[2] = kM6CarrierProtocolVersion;
    output[3] = kM6CarrierFrameTypeClockSyncResponse;
    write_u16(output + 4,
              static_cast<std::uint16_t>(
                  kM6CarrierClockSyncResponsePayloadBytes));
    write_u32(output + 6, 0U);
    output[10] = response.valid ? 1U : 0U;
    output[11] = 0U;
    output[12] = 0U;
    output[13] = 0U;
    write_u64(output + 14, response.carrier_received_us);
    write_u64(output + 22, response.carrier_sent_us);
    write_u16(output + kM6CarrierClockSyncResponseBytes -
                  kM6CarrierFooterBytes,
              m6_carrier_crc16(
                  output,
                  kM6CarrierClockSyncResponseBytes - kM6CarrierFooterBytes));
    return kM6CarrierClockSyncResponseBytes;
}

bool m6_carrier_decode_clock_sync_response(
    const std::uint8_t* bytes,
    const std::size_t size,
    M6CarrierClockSyncResponse* response) {
    if (response == nullptr ||
        !sync_frame_header_is_valid(
            bytes, size, kM6CarrierFrameTypeClockSyncResponse,
            static_cast<std::uint16_t>(
                kM6CarrierClockSyncResponsePayloadBytes),
            kM6CarrierClockSyncResponseBytes) ||
        bytes[11] != 0U || bytes[12] != 0U || bytes[13] != 0U ||
        bytes[10] > 1U) {
        return false;
    }
    response->valid = bytes[10] != 0U;
    response->carrier_received_us = read_u64(bytes + 14);
    response->carrier_sent_us = read_u64(bytes + 22);
    return true;
}

M6CarrierClockCalibration::M6CarrierClockCalibration(
    M6CarrierClockCalibrationConfig config)
    : config_(config) {
    if (config_.minimum_samples == 0) {
        config_.minimum_samples = 1;
    }
    if (config_.minimum_samples > kM6CarrierClockCalibrationMaxSamples) {
        config_.minimum_samples =
            static_cast<std::uint8_t>(kM6CarrierClockCalibrationMaxSamples);
    }
}

std::optional<M6CarrierClockCalibration::SampleMetrics>
M6CarrierClockCalibration::measure(const M6CarrierClockSyncSample& sample) {
    if (sample.host_received_us < sample.host_sent_us ||
        sample.carrier_sent_us < sample.carrier_received_us) {
        return std::nullopt;
    }
    const std::uint64_t host_half_rtt =
        (sample.host_received_us - sample.host_sent_us) / 2U;
    const std::uint64_t carrier_half_rtt =
        (sample.carrier_sent_us - sample.carrier_received_us) / 2U;
    if (sample.host_sent_us >
            std::numeric_limits<std::uint64_t>::max() - host_half_rtt ||
        sample.carrier_received_us >
            std::numeric_limits<std::uint64_t>::max() - carrier_half_rtt) {
        return std::nullopt;
    }
    const std::uint64_t host_midpoint = sample.host_sent_us + host_half_rtt;
    const std::uint64_t carrier_midpoint =
        sample.carrier_received_us + carrier_half_rtt;
    const auto offset = m6_carrier_estimate_clock_offset(sample);
    if (!offset.has_value()) {
        return std::nullopt;
    }
    return SampleMetrics{
        *offset,
        host_midpoint,
        carrier_midpoint,
        sample.host_received_us - sample.host_sent_us,
    };
}

bool M6CarrierClockCalibration::metrics_are_monotonic(
    const SampleMetrics& metrics) const {
    return !has_previous_sample_ ||
           (metrics.host_midpoint_us >= previous_sample_.host_midpoint_us &&
            metrics.carrier_midpoint_us >=
                previous_sample_.carrier_midpoint_us);
}

bool M6CarrierClockCalibration::add_sample(
    const M6CarrierClockSyncSample& sample) {
    const auto metrics = measure(sample);
    if (!metrics.has_value() ||
        metrics->round_trip_us > config_.max_round_trip_us ||
        !metrics_are_monotonic(*metrics)) {
        // A bad exchange must not leave an older calibration looking valid.
        reset();
        return false;
    }

    if (sample_count_ < kM6CarrierClockCalibrationMaxSamples) {
        samples_[sample_count_++] = *metrics;
    } else {
        for (std::size_t index = 1;
             index < kM6CarrierClockCalibrationMaxSamples; ++index) {
            samples_[index - 1] = samples_[index];
        }
        samples_[kM6CarrierClockCalibrationMaxSamples - 1] = *metrics;
    }
    previous_sample_ = *metrics;
    has_previous_sample_ = true;
    confirmed_ = false;
    return true;
}

bool M6CarrierClockCalibration::confirm() {
    confirmed_ = ready_for_confirmation();
    return confirmed_;
}

void M6CarrierClockCalibration::reset() {
    samples_.fill({});
    sample_count_ = 0;
    has_previous_sample_ = false;
    previous_sample_ = {};
    confirmed_ = false;
}

bool M6CarrierClockCalibration::ready_for_confirmation() const {
    return sample_count_ >= config_.minimum_samples &&
           offset_spread_us() <= config_.max_offset_spread_us &&
           inter_sample_drift_us() <= config_.max_inter_sample_drift_us;
}

std::uint64_t M6CarrierClockCalibration::offset_spread_us() const {
    std::uint64_t spread = 0;
    for (std::size_t left = 0; left < sample_count_; ++left) {
        for (std::size_t right = left + 1; right < sample_count_; ++right) {
            const std::int64_t first = samples_[left].offset_us;
            const std::int64_t second = samples_[right].offset_us;
            const std::uint64_t difference =
                first >= second
                    ? static_cast<std::uint64_t>(first) -
                          static_cast<std::uint64_t>(second)
                    : static_cast<std::uint64_t>(second) -
                          static_cast<std::uint64_t>(first);
            if (difference > spread) {
                spread = difference;
            }
        }
    }
    return spread;
}

std::uint64_t M6CarrierClockCalibration::inter_sample_drift_us() const {
    std::uint64_t drift = 0;
    for (std::size_t index = 1; index < sample_count_; ++index) {
        const std::uint64_t host_elapsed =
            samples_[index].host_midpoint_us -
            samples_[index - 1].host_midpoint_us;
        const std::uint64_t carrier_elapsed =
            samples_[index].carrier_midpoint_us -
            samples_[index - 1].carrier_midpoint_us;
        const std::uint64_t difference =
            host_elapsed >= carrier_elapsed
                ? host_elapsed - carrier_elapsed
                : carrier_elapsed - host_elapsed;
        if (difference > drift) {
            drift = difference;
        }
    }
    return drift;
}

std::uint64_t M6CarrierClockCalibration::best_round_trip_us() const {
    if (sample_count_ == 0) {
        return 0;
    }
    std::uint64_t best = samples_[0].round_trip_us;
    for (std::size_t index = 1; index < sample_count_; ++index) {
        if (samples_[index].round_trip_us < best) {
            best = samples_[index].round_trip_us;
        }
    }
    return best;
}

std::size_t M6CarrierClockCalibration::best_sample_index() const {
    if (sample_count_ == 0) {
        return 0;
    }
    std::size_t best = 0;
    for (std::size_t index = 1; index < sample_count_; ++index) {
        if (samples_[index].round_trip_us < samples_[best].round_trip_us) {
            best = index;
        }
    }
    return best;
}

std::optional<std::int64_t>
M6CarrierClockCalibration::confirmed_offset_us() const {
    if (!confirmed_ || sample_count_ == 0) {
        return std::nullopt;
    }
    return samples_[best_sample_index()].offset_us;
}

std::size_t m6_carrier_encode_edges(const M6CarrierFrame& frame,
                                    std::uint8_t* output,
                                    const std::size_t capacity) {
    if (output == nullptr || frame.edge_count > kM6CarrierMaxEdgesPerFrame ||
        (frame.flags & static_cast<std::uint8_t>(~kM6CarrierKnownWireFlags)) !=
            0U) {
        return 0;
    }
    const std::size_t payload_size =
        kM6CarrierPayloadFixedBytes +
        static_cast<std::size_t>(frame.edge_count) * kM6CarrierEdgeRecordBytes;
    const std::size_t frame_size =
        kM6CarrierHeaderBytes + payload_size + kM6CarrierFooterBytes;
    if (capacity < frame_size) {
        return 0;
    }

    for (std::size_t index = 0; index < frame.edge_count; ++index) {
        const M6CarrierEdge& edge = frame.edges[index];
        if (edge.channel >= config::kBeamCount || edge.level > 1U ||
            edge.timestamp_us < frame.base_timestamp_us ||
            edge.timestamp_us - frame.base_timestamp_us >
                std::numeric_limits<std::uint32_t>::max()) {
            return 0;
        }
    }

    output[0] = kM6CarrierMagic0;
    output[1] = kM6CarrierMagic1;
    output[2] = kM6CarrierProtocolVersion;
    output[3] = kM6CarrierFrameTypeEdges;
    write_u16(output + 4, static_cast<std::uint16_t>(payload_size));
    write_u32(output + 6, frame.sequence);

    output[kPayloadOffset] = frame.edge_count;
    output[kPayloadOffset + 1] = frame.flags;
    output[kPayloadOffset + 2] = 0;
    output[kPayloadOffset + 3] = 0;
    write_u64(output + kBaseTimestampOffset, frame.base_timestamp_us);

    for (std::size_t index = 0; index < frame.edge_count; ++index) {
        const std::size_t offset =
            kRecordsOffset + index * kM6CarrierEdgeRecordBytes;
        const M6CarrierEdge& edge = frame.edges[index];
        const std::uint64_t delta = edge.timestamp_us - frame.base_timestamp_us;
        output[offset] = edge.channel;
        output[offset + 1] = edge.level;
        output[offset + 2] = 0;
        output[offset + 3] = 0;
        write_u32(output + offset + 4, static_cast<std::uint32_t>(delta));
    }

    const std::uint16_t crc = m6_carrier_crc16(output, frame_size - 2);
    write_u16(output + frame_size - 2, crc);
    return frame_size;
}

M6CarrierDecodeStatus m6_carrier_decode_edges(const std::uint8_t* bytes,
                                               const std::size_t size,
                                               M6CarrierFrame* frame) {
    if (bytes == nullptr || frame == nullptr) {
        return M6CarrierDecodeStatus::kInvalidArgument;
    }
    if (size < kM6CarrierHeaderBytes + kM6CarrierFooterBytes) {
        return M6CarrierDecodeStatus::kTooShort;
    }
    if (bytes[0] != kM6CarrierMagic0 || bytes[1] != kM6CarrierMagic1) {
        return M6CarrierDecodeStatus::kBadMagic;
    }
    if (bytes[2] != kM6CarrierProtocolVersion) {
        return M6CarrierDecodeStatus::kUnsupportedVersion;
    }
    if (bytes[3] != kM6CarrierFrameTypeEdges) {
        return M6CarrierDecodeStatus::kUnsupportedType;
    }

    const std::uint16_t payload_size = read_u16(bytes + 4);
    const std::size_t expected_size =
        kM6CarrierHeaderBytes + payload_size + kM6CarrierFooterBytes;
    if (expected_size != size || payload_size > kM6CarrierMaxPayloadBytes) {
        return M6CarrierDecodeStatus::kLengthMismatch;
    }

    const std::uint8_t edge_count = bytes[kPayloadOffset];
    if (!payload_shape_is_valid(payload_size, edge_count) ||
        bytes[kPayloadOffset + 2] != 0 || bytes[kPayloadOffset + 3] != 0) {
        return M6CarrierDecodeStatus::kInvalidPayload;
    }

    const std::uint16_t expected_crc = read_u16(bytes + size - 2);
    if (m6_carrier_crc16(bytes, size - 2) != expected_crc) {
        return M6CarrierDecodeStatus::kCrcMismatch;
    }

    M6CarrierFrame decoded;
    decoded.sequence = read_u32(bytes + 6);
    decoded.flags = bytes[kPayloadOffset + 1];
    if ((decoded.flags & ~kM6CarrierKnownWireFlags) != 0U) {
        return M6CarrierDecodeStatus::kInvalidPayload;
    }
    decoded.base_timestamp_us = read_u64(bytes + kBaseTimestampOffset);
    decoded.edge_count = edge_count;
    for (std::size_t index = 0; index < edge_count; ++index) {
        const std::size_t offset =
            kRecordsOffset + index * kM6CarrierEdgeRecordBytes;
        const std::uint8_t channel = bytes[offset];
        const std::uint8_t level = bytes[offset + 1];
        if (channel >= config::kBeamCount || level > 1U ||
            bytes[offset + 2] != 0 || bytes[offset + 3] != 0) {
            return M6CarrierDecodeStatus::kInvalidPayload;
        }
        const std::uint64_t delta = read_u32(bytes + offset + 4);
        if (decoded.base_timestamp_us >
            std::numeric_limits<std::uint64_t>::max() - delta) {
            return M6CarrierDecodeStatus::kTimestampOverflow;
        }
        decoded.edges[index] = {
            channel,
            level,
            decoded.base_timestamp_us + delta,
        };
    }
    *frame = decoded;
    return M6CarrierDecodeStatus::kOk;
}

std::optional<M6CarrierFrame> M6CarrierStreamDecoder::feed(
    const std::uint8_t byte) {
    if (size_ == 0) {
        if (byte == kM6CarrierMagic0) {
            buffer_[0] = byte;
            size_ = 1;
        }
        return std::nullopt;
    }

    if (size_ == 1 && byte != kM6CarrierMagic1) {
        size_ = byte == kM6CarrierMagic0 ? 1 : 0;
        if (size_ == 1) {
            buffer_[0] = byte;
        }
        return std::nullopt;
    }

    if (size_ >= buffer_.size()) {
        reset();
        ++invalid_frame_count_;
        return std::nullopt;
    }
    buffer_[size_++] = byte;

    if (size_ == kM6CarrierHeaderBytes) {
        const std::uint16_t payload_size = read_u16(buffer_.data() + 4);
        if (payload_size > kM6CarrierMaxPayloadBytes) {
            reset();
            ++invalid_frame_count_;
            return std::nullopt;
        }
        expected_size_ = kM6CarrierHeaderBytes + payload_size +
                         kM6CarrierFooterBytes;
    }
    if (expected_size_ == 0 || size_ != expected_size_) {
        return std::nullopt;
    }

    M6CarrierFrame frame;
    const auto status =
        m6_carrier_decode_edges(buffer_.data(), size_, &frame);
    reset();
    if (status == M6CarrierDecodeStatus::kOk) {
        return frame;
    }
    if (status == M6CarrierDecodeStatus::kCrcMismatch) {
        ++crc_error_count_;
    } else {
        ++invalid_frame_count_;
    }
    return std::nullopt;
}

void M6CarrierStreamDecoder::reset() {
    size_ = 0;
    expected_size_ = 0;
}

bool M6CarrierSequenceTracker::apply(M6CarrierFrame& frame) {
    const bool contiguous = !has_sequence_ ||
                            frame.sequence == last_sequence_ + 1U;
    if (!contiguous) {
        frame.flags = static_cast<std::uint8_t>(
            frame.flags | kM6CarrierFlagSequenceGap);
    }
    last_sequence_ = frame.sequence;
    has_sequence_ = true;
    return contiguous;
}

void M6CarrierSequenceTracker::reset() {
    has_sequence_ = false;
    last_sequence_ = 0;
}

}  // namespace smartgear
