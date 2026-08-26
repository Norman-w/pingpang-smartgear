#include "m6_carrier_protocol.h"
#include "m6_carrier_adapter.h"
#include "m6_carrier_capture_core.h"
#include "m6_carrier_spi_slave_transport.h"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <optional>
#include <string>

namespace {

void require(const bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

smartgear::M6CarrierFrame sample_frame() {
    smartgear::M6CarrierFrame frame;
    frame.sequence = 41;
    frame.flags = smartgear::kM6CarrierFlagFifoOverflow;
    frame.base_timestamp_us = 2'000'000;
    frame.edge_count = 3;
    frame.edges[0] = {2, 1, 2'000'000};
    frame.edges[1] = {2, 0, 2'001'250};
    frame.edges[2] = {7, 1, 2'004'000};
    return frame;
}

}  // namespace

int main() {
    using namespace smartgear;

    const M6CarrierFrame source = sample_frame();
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> bytes{};
    const std::size_t size =
        m6_carrier_encode_edges(source, bytes.data(), bytes.size());
    require(size > kM6CarrierHeaderBytes, "sample frame must encode");

    M6CarrierFrame decoded;
    require(m6_carrier_decode_edges(bytes.data(), size, &decoded) ==
                M6CarrierDecodeStatus::kOk,
            "encoded frame must decode");
    require(decoded.sequence == source.sequence &&
                decoded.flags == source.flags &&
                decoded.edge_count == source.edge_count,
            "frame metadata must round-trip");
    require(decoded.edges[1].channel == 2 && decoded.edges[1].level == 0 &&
                decoded.edges[1].timestamp_us == 2'001'250,
            "edge timestamp delta must round-trip");

    M6CarrierStreamDecoder stream;
    std::optional<M6CarrierFrame> streamed;
    const std::array<std::uint8_t, 3> noise = {0x00, 0xA5, 0x00};
    for (const auto byte : noise) {
        streamed = stream.feed(byte);
    }
    for (std::size_t index = 0; index < size; ++index) {
        streamed = stream.feed(bytes[index]);
    }
    require(streamed.has_value() && streamed->sequence == source.sequence,
            "fragmented stream with noise must recover one frame");

    auto corrupt = bytes;
    corrupt[size - 1] ^= 0x01U;
    M6CarrierStreamDecoder bad_stream;
    for (std::size_t index = 0; index < size; ++index) {
        require(!bad_stream.feed(corrupt[index]).has_value(),
                "CRC-corrupt frame must not be emitted");
    }
    require(bad_stream.crc_error_count() == 1,
            "CRC corruption must be counted");

    M6CarrierFrame invalid_channel = source;
    invalid_channel.edges[0].channel = 10;
    require(m6_carrier_encode_edges(invalid_channel, bytes.data(), bytes.size()) ==
                0,
            "channel outside ten logical inputs must not encode");

    M6CarrierFrame invalid_flags = source;
    invalid_flags.flags = kM6CarrierFlagSequenceGap;
    require(m6_carrier_encode_edges(invalid_flags, bytes.data(), bytes.size()) ==
                0,
            "host-only sequence flag must not be emitted on the wire");

    M6CarrierFrame invalid_time = source;
    invalid_time.base_timestamp_us = 0;
    invalid_time.edges[0].timestamp_us =
        static_cast<std::uint64_t>(std::numeric_limits<std::uint32_t>::max()) +
        1U;
    require(m6_carrier_encode_edges(invalid_time, bytes.data(), bytes.size()) ==
                0,
            "timestamp delta beyond uint32 must not encode");

    const auto offset = m6_carrier_estimate_clock_offset({
        1'000'000,
        1'002'000,
        500'000,
        500'100,
    });
    require(offset.has_value() && *offset == 500'950,
            "symmetric clock exchange must produce a host-carrier offset");
    require(!m6_carrier_estimate_clock_offset({2, 1, 3, 4}).has_value(),
            "reverse host clock exchange must be rejected");

    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> sync_request{};
    require(m6_carrier_encode_clock_sync_request(sync_request.data(),
                                                 sync_request.size()) ==
                kM6CarrierClockSyncRequestBytes &&
                m6_carrier_decode_clock_sync_request(
                    sync_request.data(), sync_request.size()),
            "clock-sync request must round-trip through a padded SPI frame");
    M6CarrierClockSyncResponse sync_source{
        true,
        700'000,
        700'125,
    };
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> sync_response_bytes{};
    const std::size_t sync_response_size = m6_carrier_encode_clock_sync_response(
        sync_source, sync_response_bytes.data(), sync_response_bytes.size());
    M6CarrierClockSyncResponse sync_decoded;
    require(sync_response_size == kM6CarrierClockSyncResponseBytes &&
                m6_carrier_decode_clock_sync_response(
                    sync_response_bytes.data(), sync_response_size,
                    &sync_decoded) &&
                sync_decoded.valid &&
                sync_decoded.carrier_received_us == 700'000 &&
                sync_decoded.carrier_sent_us == 700'125,
            "clock-sync response must preserve carrier t2/t3 timestamps");
    sync_response_bytes[sync_response_size - 1U] ^= 0x01U;
    require(!m6_carrier_decode_clock_sync_response(
                sync_response_bytes.data(), sync_response_size, &sync_decoded),
            "clock-sync response CRC corruption must be rejected");

    M6CarrierClockCalibration calibration;
    require(calibration.add_sample({
                1'000'000,
                1'002'000,
                500'000,
                500'100,
            }) &&
                !calibration.confirmed() && !calibration.confirm(),
            "one clock exchange must not confirm a calibration");
    require(calibration.add_sample({
                2'000'000,
                2'001'000,
                1'499'500,
                1'499'600,
            }) &&
                calibration.add_sample({
                    3'000'000,
                    3'000'800,
                    2'499'400,
                    2'499'500,
                }) &&
                calibration.confirm(),
            "three stable exchanges must confirm a calibration");
    require(calibration.confirmed() &&
                calibration.confirmed_offset_us().has_value() &&
                *calibration.confirmed_offset_us() == 500'950 &&
                calibration.best_round_trip_us() == 800 &&
                calibration.offset_spread_us() == 0 &&
                calibration.inter_sample_drift_us() == 0,
            "confirmed calibration must choose the lowest-latency stable sample");

    M6CarrierClockCalibration unstable({3, 50'000, 10, 500});
    require(unstable.add_sample({
                1'000'000,
                1'001'000,
                500'000,
                500'100,
            }) &&
                unstable.add_sample({
                    2'000'000,
                    2'001'000,
                    1'499'950,
                    1'500'050,
                }) &&
                unstable.add_sample({
                    3'000'000,
                    3'001'000,
                    2'499'950,
                    2'500'050,
                }) &&
                !unstable.confirm() && unstable.offset_spread_us() == 50,
            "offset spread above the gate must stay unconfirmed");
    require(!unstable.add_sample({2, 1, 3, 4}) &&
                unstable.sample_count() == 0 && !unstable.confirmed(),
            "an invalid runtime exchange must clear calibration state");

    M6CarrierSequenceTracker tracker;
    M6CarrierFrame first = source;
    M6CarrierFrame second = source;
    second.sequence = first.sequence + 1;
    M6CarrierFrame gap = source;
    gap.sequence = first.sequence + 3;
    require(tracker.apply(first) && tracker.apply(second),
            "contiguous carrier sequence must pass");
    require(!tracker.apply(gap) &&
                (gap.flags & kM6CarrierFlagSequenceGap) != 0,
            "sequence gap must be marked as an input failure");

    BeamCapture capture(5'000, 250'000);
    M6CarrierBeamAdapter adapter(capture, 100);
    M6CarrierFrame beam_frame;
    beam_frame.sequence = 1;
    beam_frame.base_timestamp_us = 100'000;
    beam_frame.edge_count = 2;
    beam_frame.edges[0] = {3, 0, 100'000};
    beam_frame.edges[1] = {3, 1, 101'000};
    const auto beam_result = adapter.ingest(beam_frame);
    require(beam_result.input_boundary_valid &&
                beam_result.observation_count == 0,
            "valid carrier edges must enter BeamCapture");
    const auto observation = adapter.poll(106'100);
    require(observation.has_value() && observation->valid &&
                observation->beam_mask == (1U << 3) &&
                observation->start_us == 100'100,
            "carrier clock offset and active-low edge pair must form a beam event");

    M6CarrierFrame overflow_frame = beam_frame;
    overflow_frame.sequence = 2;
    overflow_frame.flags = kM6CarrierFlagFifoOverflow;
    const auto overflow_result = adapter.ingest(overflow_frame);
    require(!overflow_result.input_boundary_valid,
            "carrier FIFO overflow must invalidate the input boundary");

    adapter.set_clock_offset(200);
    require(adapter.clock_offset_us() == 200,
            "runtime clock calibration must update the adapter offset");
    M6CarrierFrame recalibrated_frame = beam_frame;
    recalibrated_frame.base_timestamp_us = 200'000;
    recalibrated_frame.edges[0].timestamp_us = 200'000;
    recalibrated_frame.edges[1].timestamp_us = 201'000;
    const auto recalibrated_result = adapter.ingest(recalibrated_frame);
    require(recalibrated_result.input_boundary_valid,
            "a new sequence must be accepted after offset replacement");
    const auto recalibrated_observation = adapter.poll(206'200);
    require(recalibrated_observation.has_value() &&
                recalibrated_observation->start_us == 200'200,
            "updated carrier offset must translate new edge timestamps");

    carrier::M6CarrierCaptureCore capture_core;
    require(capture_core.on_edge(4, 0, 10'000) &&
                capture_core.on_edge(4, 1, 10'750) &&
                capture_core.on_edge(9, 0, 11'000),
            "carrier ISR edges must enter the local FIFO");
    M6CarrierFrame carrier_frame;
    require(capture_core.pop_frame(&carrier_frame) &&
                carrier_frame.sequence == 0 && carrier_frame.edge_count == 3 &&
                carrier_frame.edges[1].timestamp_us == 10'750 &&
                carrier_frame.flags == 0,
            "carrier core must batch ordered edges without filtering");
    require(!capture_core.has_pending_edges(),
            "carrier FIFO must be empty after its frame is popped");

    carrier::M6CarrierCaptureCore sync_capture;
    carrier::M6CarrierSpiSlaveTransport sync_transport(sync_capture);
    require(!sync_transport.frame_ready() &&
                sync_transport.begin_clock_sync_request() &&
                sync_transport.clock_sync_request_active(),
            "carrier must accept a clock-sync request when no event is staged");
    require(sync_transport.end_clock_sync_request(
                kM6CarrierMaxFrameBytes, sync_request.data(),
                sync_request.size(), 800'000) &&
                sync_transport.clock_sync_response_pending() &&
                sync_transport.irq_asserted(),
            "valid clock-sync request must stage an IRQ response");
    require(sync_transport.begin_clock_sync_response(800'125) &&
                sync_transport.transaction_active(),
            "clock-sync response must capture carrier t3 at CS assertion");
    M6CarrierClockSyncResponse staged_sync_response;
    require(m6_carrier_decode_clock_sync_response(
                sync_transport.tx_buffer(),
                kM6CarrierClockSyncResponseBytes, &staged_sync_response) &&
                staged_sync_response.valid &&
                staged_sync_response.carrier_received_us == 800'000 &&
                staged_sync_response.carrier_sent_us == 800'125 &&
                sync_transport.end_transaction(kM6CarrierMaxFrameBytes) &&
                !sync_transport.clock_sync_response_pending() &&
                !sync_transport.irq_asserted(),
            "clock-sync response must release IRQ after the fixed transaction");

    carrier::M6CarrierCaptureCore slave_capture;
    carrier::M6CarrierSpiSlaveTransport slave_transport(slave_capture);
    require(slave_capture.on_edge(1, 0, 50'000) &&
                slave_capture.on_edge(1, 1, 50'800),
            "SPI slave contract must receive edges before staging");
    require(slave_transport.service() && slave_transport.frame_ready() &&
                slave_transport.irq_asserted() &&
                slave_transport.tx_transfer_bytes() == kM6CarrierMaxFrameBytes,
            "SPI slave contract must stage a fixed maximum TX frame");
    M6CarrierFrame staged_frame;
    require(m6_carrier_decode_edges(slave_transport.tx_buffer(),
                                    slave_transport.wire_frame_bytes(),
                                    &staged_frame) == M6CarrierDecodeStatus::kOk &&
                staged_frame.edge_count == 2,
            "staged SPI TX buffer must contain a complete CRC frame");
    require(slave_transport.begin_transaction() &&
                slave_transport.transaction_active() &&
                !slave_transport.service(),
            "SPI slave contract must hold a frame while CS is active");
    require(slave_transport.end_transaction(kM6CarrierMaxFrameBytes) &&
                !slave_transport.frame_ready() &&
                !slave_transport.irq_asserted(),
            "complete fixed-size CS transaction must release IRQ");
    require(!slave_transport.begin_transaction(),
            "SPI slave must not begin without a staged frame");

    require(slave_capture.on_edge(1, 0, 60'000),
            "SPI slave contract must accept a later edge batch");
    require(slave_transport.service() && slave_transport.begin_transaction(),
            "SPI slave contract must stage the next frame");
    require(!slave_transport.end_transaction(kM6CarrierMaxFrameBytes - 1U),
            "short SPI transaction must fail closed");
    require(slave_capture.on_edge(1, 1, 60'800) && slave_transport.service(),
            "transport fault must not stop later edge capture");
    M6CarrierFrame fault_frame;
    require(m6_carrier_decode_edges(slave_transport.tx_buffer(),
                                    slave_transport.wire_frame_bytes(),
                                    &fault_frame) == M6CarrierDecodeStatus::kOk &&
                (fault_frame.flags & kM6CarrierFlagTimestampInvalid) != 0U,
            "short SPI transaction must mark the next frame invalid");
    require(slave_transport.begin_transaction() &&
                slave_transport.end_transaction(kM6CarrierMaxFrameBytes),
            "fault frame must still complete through a fixed transaction");
    slave_transport.reset();
    require(!slave_transport.frame_ready() && !slave_transport.transaction_active() &&
                !slave_capture.has_pending_edges(),
            "SPI slave reset must clear staging and capture state");

    carrier::M6CarrierCaptureCore burst_core;
    for (std::uint8_t channel = 0; channel < 10U; ++channel) {
        require(burst_core.on_edge(channel, 0, 70'000),
                "ten-channel burst must accept every falling edge");
    }
    for (std::uint8_t channel = 0; channel < 10U; ++channel) {
        require(burst_core.on_edge(channel, 1, 70'900),
                "ten-channel burst must accept every rising edge");
    }
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> burst_bytes{};
    std::size_t burst_edges = 0;
    std::uint32_t previous_sequence = 0;
    bool first_burst_frame = true;
    while (burst_core.has_pending_edges()) {
        const std::size_t burst_size = burst_core.pop_encoded_frame(
            burst_bytes.data(), burst_bytes.size());
        require(burst_size > 0,
                "ten-channel burst must encode each frame without overflow");
        M6CarrierFrame burst_frame;
        require(m6_carrier_decode_edges(burst_bytes.data(), burst_size,
                                         &burst_frame) ==
                    M6CarrierDecodeStatus::kOk &&
                (first_burst_frame ||
                 burst_frame.sequence == previous_sequence + 1U),
            "ten-channel burst frames must decode with contiguous sequence");
        require((burst_frame.flags & kM6CarrierFlagFifoOverflow) == 0U,
                "ten-channel burst must not raise FIFO overflow");
        burst_edges += burst_frame.edge_count;
        previous_sequence = burst_frame.sequence;
        first_burst_frame = false;
    }
    require(burst_edges == 20,
            "ten-channel rising/falling burst must preserve all twenty edges");

    carrier::M6CarrierCaptureCore encoded_core;
    require(encoded_core.on_edge(6, 0, 40'000) &&
                encoded_core.on_edge(6, 1, 40'900),
            "carrier edges must be available to the encoded transport path");
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> encoded_bytes{};
    require(encoded_core.pop_encoded_frame(
                encoded_bytes.data(), kM6CarrierMaxFrameBytes - 1U) == 0 &&
                encoded_core.has_pending_edges(),
            "undersized SPI staging buffer must not consume carrier edges");
    const std::size_t encoded_size = encoded_core.pop_encoded_frame(
        encoded_bytes.data(), encoded_bytes.size());
    M6CarrierFrame encoded_frame;
    require(encoded_size > 0 &&
                m6_carrier_decode_edges(encoded_bytes.data(), encoded_size,
                                         &encoded_frame) ==
                    M6CarrierDecodeStatus::kOk &&
                encoded_frame.edge_count == 2 &&
                encoded_frame.edges[1].timestamp_us == 40'900,
            "carrier transport helper must encode a complete CRC frame");

    carrier::M6CarrierCaptureCore overflow_core;
    for (std::size_t index = 0; index < carrier::kCaptureFifoCapacity; ++index) {
        require(overflow_core.on_edge(0, static_cast<std::uint8_t>(index & 1U),
                                      20'000 + index),
                "carrier FIFO must accept its declared capacity");
    }
    require(!overflow_core.on_edge(0, 1, 21'000) &&
                overflow_core.dropped_edge_count() == 1,
            "carrier FIFO overflow must drop and count the edge");
    require(overflow_core.pop_frame(&carrier_frame) &&
                (carrier_frame.flags & kM6CarrierFlagFifoOverflow) != 0U,
            "carrier FIFO overflow must travel on the next frame");

    carrier::M6CarrierCaptureCore invalid_timestamp_core;
    require(invalid_timestamp_core.on_edge(0, 0, 30'000) &&
                !invalid_timestamp_core.on_edge(0, 1, 29'999),
            "carrier core must reject timestamp reversal");
    require(invalid_timestamp_core.pop_frame(&carrier_frame) &&
                (carrier_frame.flags & kM6CarrierFlagTimestampInvalid) != 0U,
            "carrier timestamp reversal must be explicit");

    std::cout << "M6_CARRIER_PROTOCOL_OK (frame, stream, CRC, sequence, clock, clock-sync-wire, runtime-calibration, carrier-core, tx-encode, spi-slave-contract, ten-channel-burst, bounds)\n";
    return 0;
}
