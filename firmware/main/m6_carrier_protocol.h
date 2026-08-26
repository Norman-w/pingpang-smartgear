#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace smartgear {

// M6 capture-carrier wire format. The carrier owns edge timing; the
// SmartPaddle/ESP32 adapter is responsible for translating that clock into
// the esp_timer monotonic domain before calling BeamCapture.
constexpr std::uint8_t kM6CarrierProtocolVersion = 1;
constexpr std::uint8_t kM6CarrierMagic0 = 0xA5;
constexpr std::uint8_t kM6CarrierMagic1 = 0x5A;
constexpr std::uint8_t kM6CarrierFrameTypeEdges = 0x01;
constexpr std::uint8_t kM6CarrierFrameTypeClockSyncRequest = 0x02;
constexpr std::uint8_t kM6CarrierFrameTypeClockSyncResponse = 0x03;
constexpr std::size_t kM6CarrierHeaderBytes = 10;
constexpr std::size_t kM6CarrierFooterBytes = 2;
constexpr std::size_t kM6CarrierPayloadFixedBytes = 12;
constexpr std::size_t kM6CarrierEdgeRecordBytes = 8;
constexpr std::size_t kM6CarrierMaxEdgesPerFrame = 16;
constexpr std::size_t kM6CarrierMaxPayloadBytes =
    kM6CarrierPayloadFixedBytes +
    kM6CarrierMaxEdgesPerFrame * kM6CarrierEdgeRecordBytes;
constexpr std::size_t kM6CarrierMaxFrameBytes =
    kM6CarrierHeaderBytes + kM6CarrierMaxPayloadBytes +
    kM6CarrierFooterBytes;
constexpr std::size_t kM6CarrierClockCalibrationMaxSamples = 8;
constexpr std::size_t kM6CarrierClockSyncRequestPayloadBytes = 4;
constexpr std::size_t kM6CarrierClockSyncResponsePayloadBytes = 20;
constexpr std::size_t kM6CarrierClockSyncRequestBytes =
    kM6CarrierHeaderBytes + kM6CarrierClockSyncRequestPayloadBytes +
    kM6CarrierFooterBytes;
constexpr std::size_t kM6CarrierClockSyncResponseBytes =
    kM6CarrierHeaderBytes + kM6CarrierClockSyncResponsePayloadBytes +
    kM6CarrierFooterBytes;

enum M6CarrierFrameFlags : std::uint8_t {
    kM6CarrierFlagFifoOverflow = 1U << 0,
    kM6CarrierFlagTimestampInvalid = 1U << 1,
    // Set by the host-side sequence tracker, not by the carrier wire frame.
    kM6CarrierFlagSequenceGap = 1U << 2,
};

constexpr std::uint8_t kM6CarrierKnownWireFlags =
    kM6CarrierFlagFifoOverflow | kM6CarrierFlagTimestampInvalid;

struct M6CarrierEdge {
    std::uint8_t channel = 0;
    std::uint8_t level = 0;
    std::uint64_t timestamp_us = 0;
};

struct M6CarrierFrame {
    std::uint32_t sequence = 0;
    std::uint8_t flags = 0;
    std::uint64_t base_timestamp_us = 0;
    std::uint8_t edge_count = 0;
    std::array<M6CarrierEdge, kM6CarrierMaxEdgesPerFrame> edges{};
};

enum class M6CarrierDecodeStatus : std::uint8_t {
    kOk,
    kInvalidArgument,
    kTooShort,
    kBadMagic,
    kUnsupportedVersion,
    kUnsupportedType,
    kLengthMismatch,
    kInvalidPayload,
    kTimestampOverflow,
    kCrcMismatch,
};

std::uint16_t m6_carrier_crc16(const std::uint8_t* bytes, std::size_t size);

struct M6CarrierClockSyncSample {
    std::uint64_t host_sent_us = 0;
    std::uint64_t host_received_us = 0;
    std::uint64_t carrier_received_us = 0;
    std::uint64_t carrier_sent_us = 0;
};

struct M6CarrierClockSyncResponse {
    bool valid = false;
    std::uint64_t carrier_received_us = 0;
    std::uint64_t carrier_sent_us = 0;
};

struct M6CarrierClockCalibrationConfig {
    // A single exchange is not enough to distinguish clock offset from an
    // asymmetric SPI/IRQ delay. Keep the runtime gate deliberately small and
    // deterministic so it is easy to reproduce on a logic analyser.
    std::uint8_t minimum_samples = 3;
    std::uint64_t max_round_trip_us = 50'000;
    std::uint64_t max_offset_spread_us = 250;
    std::uint64_t max_inter_sample_drift_us = 500;
};

// Estimate host_time - carrier_time under a symmetric transaction-delay
// assumption. The result is only a starting offset; drift must be checked on
// the real carrier and refreshed periodically.
std::optional<std::int64_t> m6_carrier_estimate_clock_offset(
    const M6CarrierClockSyncSample& sample);

// The request/response exchange uses the same CRC-protected fixed-size SPI
// transaction as the event path. The request is sent in one transaction; the
// carrier captures t2 at request CS release, then prepares the response. The
// following transaction captures t3 at response CS assertion and returns
// both carrier timestamps to the host.
std::size_t m6_carrier_encode_clock_sync_request(
    std::uint8_t* output, std::size_t capacity);
bool m6_carrier_decode_clock_sync_request(const std::uint8_t* bytes,
                                          std::size_t size);
std::size_t m6_carrier_encode_clock_sync_response(
    const M6CarrierClockSyncResponse& response,
    std::uint8_t* output,
    std::size_t capacity);
bool m6_carrier_decode_clock_sync_response(
    const std::uint8_t* bytes,
    std::size_t size,
    M6CarrierClockSyncResponse* response);

// Collects independently completed host<->carrier exchanges. The estimator
// never becomes confirmed merely because samples were supplied: the board
// integration must call confirm() after its exchange path has produced real
// timestamps and any board-level evidence gate has passed. Invalid samples
// clear confirmation and are never used to translate beam events.
class M6CarrierClockCalibration {
  public:
    explicit M6CarrierClockCalibration(
        M6CarrierClockCalibrationConfig config = {});

    bool add_sample(const M6CarrierClockSyncSample& sample);
    bool confirm();
    void reset();

    bool confirmed() const { return confirmed_; }
    bool ready_for_confirmation() const;
    std::optional<std::int64_t> confirmed_offset_us() const;
    std::uint8_t sample_count() const { return sample_count_; }
    std::uint64_t offset_spread_us() const;
    std::uint64_t inter_sample_drift_us() const;
    std::uint64_t best_round_trip_us() const;

  private:
    struct SampleMetrics {
        std::int64_t offset_us = 0;
        std::uint64_t host_midpoint_us = 0;
        std::uint64_t carrier_midpoint_us = 0;
        std::uint64_t round_trip_us = 0;
    };

    static std::optional<SampleMetrics> measure(
        const M6CarrierClockSyncSample& sample);
    bool metrics_are_monotonic(const SampleMetrics& metrics) const;
    std::size_t best_sample_index() const;

    M6CarrierClockCalibrationConfig config_;
    std::array<SampleMetrics, kM6CarrierClockCalibrationMaxSamples> samples_{};
    std::uint8_t sample_count_ = 0;
    bool has_previous_sample_ = false;
    SampleMetrics previous_sample_{};
    bool confirmed_ = false;
};

// Returns the exact frame length, or zero when the frame cannot be encoded.
std::size_t m6_carrier_encode_edges(const M6CarrierFrame& frame,
                                    std::uint8_t* output,
                                    std::size_t capacity);

M6CarrierDecodeStatus m6_carrier_decode_edges(const std::uint8_t* bytes,
                                               std::size_t size,
                                               M6CarrierFrame* frame);

// Accepts arbitrary byte-sized chunks from SPI/UART framing and returns a
// complete frame only after magic, length and CRC validation.
class M6CarrierStreamDecoder {
  public:
    std::optional<M6CarrierFrame> feed(std::uint8_t byte);
    void reset();

    std::uint32_t crc_error_count() const { return crc_error_count_; }
    std::uint32_t invalid_frame_count() const { return invalid_frame_count_; }

  private:
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> buffer_{};
    std::size_t size_ = 0;
    std::size_t expected_size_ = 0;
    std::uint32_t crc_error_count_ = 0;
    std::uint32_t invalid_frame_count_ = 0;
};

// Frame loss is an input-boundary failure. The caller must mark the next
// business event unknown when this tracker reports a gap.
class M6CarrierSequenceTracker {
  public:
    bool apply(M6CarrierFrame& frame);
    void reset();

  private:
    bool has_sequence_ = false;
    std::uint32_t last_sequence_ = 0;
};

}  // namespace smartgear
