#include "m6_carrier_spi_slave_transport.h"

namespace smartgear::carrier {

M6CarrierSpiSlaveTransport::M6CarrierSpiSlaveTransport(
    M6CarrierCaptureCore& capture)
    : capture_(capture) {}

bool M6CarrierSpiSlaveTransport::service() {
    if (frame_ready_ || transaction_active_ || clock_sync_response_pending_) {
        return false;
    }

    tx_buffer_.fill(0);
    const std::size_t encoded_size = capture_.pop_encoded_frame(
        tx_buffer_.data(), tx_buffer_.size());
    if (encoded_size == 0) {
        return false;
    }
    wire_frame_bytes_ = encoded_size;
    frame_ready_ = true;
    return true;
}

bool M6CarrierSpiSlaveTransport::begin_transaction() {
    if (!frame_ready_ || transaction_active_ ||
        clock_sync_response_pending_) {
        return false;
    }
    transaction_active_ = true;
    transaction_kind_ = TransactionKind::kEvent;
    return true;
}

bool M6CarrierSpiSlaveTransport::begin_clock_sync_request() {
    if (frame_ready_ || transaction_active_ ||
        clock_sync_response_pending_) {
        return false;
    }
    tx_buffer_.fill(0);
    wire_frame_bytes_ = 0;
    transaction_active_ = true;
    transaction_kind_ = TransactionKind::kClockSyncRequest;
    return true;
}

bool M6CarrierSpiSlaveTransport::begin_clock_sync_response(
    const std::uint64_t carrier_sent_us) {
    if (!clock_sync_response_pending_ || transaction_active_) {
        return false;
    }

    tx_buffer_.fill(0);
    const M6CarrierClockSyncResponse response{
        clock_sync_response_valid_,
        clock_sync_carrier_received_us_,
        carrier_sent_us,
    };
    const std::size_t encoded_size = m6_carrier_encode_clock_sync_response(
        response, tx_buffer_.data(), tx_buffer_.size());
    if (encoded_size == 0U) {
        return false;
    }
    wire_frame_bytes_ = encoded_size;
    transaction_active_ = true;
    transaction_kind_ = TransactionKind::kClockSyncResponse;
    return true;
}

bool M6CarrierSpiSlaveTransport::end_transaction(
    const std::size_t transferred_bytes) {
    if (!transaction_active_) {
        return false;
    }

    if (transaction_kind_ == TransactionKind::kClockSyncRequest) {
        // A request must be closed through end_clock_sync_request(), which
        // supplies the RX buffer and the carrier-side t2 timestamp.
        return false;
    }
    const bool complete = transferred_bytes == kM6CarrierMaxFrameBytes;
    if (!complete && (transaction_kind_ == TransactionKind::kEvent ||
                      transaction_kind_ ==
                          TransactionKind::kClockSyncResponse)) {
        // The frame/response has already been staged. Mark the next event so
        // a partial transaction cannot disappear silently.
        capture_.mark_transport_fault();
    }
    if (transaction_kind_ == TransactionKind::kClockSyncResponse) {
        clock_sync_response_pending_ = false;
        clock_sync_response_valid_ = false;
        clock_sync_carrier_received_us_ = 0U;
    }
    transaction_active_ = false;
    transaction_kind_ = TransactionKind::kNone;
    frame_ready_ = false;
    wire_frame_bytes_ = 0;
    return complete;
}

bool M6CarrierSpiSlaveTransport::end_clock_sync_request(
    const std::size_t transferred_bytes,
    const std::uint8_t* rx_buffer,
    const std::size_t rx_buffer_bytes,
    const std::uint64_t carrier_received_us) {
    if (!transaction_active_ ||
        transaction_kind_ != TransactionKind::kClockSyncRequest) {
        return false;
    }

    const bool complete = transferred_bytes == kM6CarrierMaxFrameBytes;
    const bool request_valid =
        complete && rx_buffer != nullptr &&
        rx_buffer_bytes >= kM6CarrierMaxFrameBytes &&
        m6_carrier_decode_clock_sync_request(rx_buffer,
                                              kM6CarrierMaxFrameBytes);
    if (!complete) {
        capture_.mark_transport_fault();
    }
    clock_sync_response_pending_ = true;
    clock_sync_response_valid_ = request_valid;
    clock_sync_carrier_received_us_ =
        clock_sync_response_valid_ ? carrier_received_us : 0U;
    transaction_active_ = false;
    transaction_kind_ = TransactionKind::kNone;
    wire_frame_bytes_ = 0;
    return request_valid;
}

void M6CarrierSpiSlaveTransport::reset() {
    capture_.reset();
    tx_buffer_.fill(0);
    wire_frame_bytes_ = 0;
    frame_ready_ = false;
    transaction_active_ = false;
    transaction_kind_ = TransactionKind::kNone;
    clock_sync_response_pending_ = false;
    clock_sync_response_valid_ = false;
    clock_sync_carrier_received_us_ = 0U;
}

}  // namespace smartgear::carrier
