#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

#include "m6_carrier_capture_core.h"

namespace smartgear::carrier {

// Platform-neutral state machine for the carrier MCU's SPI-slave side.
//
// The platform adapter is responsible for driving IRQ_N and wiring the
// returned TX buffer into its SPI/DMA peripheral. This class owns the
// transaction lifetime so a frame is not replaced while CS is active:
//
// Event path:
//   service() -> IRQ_N low -> begin_transaction() -> DMA/SPI ->
//   end_transaction(152) -> IRQ_N high
// Clock-sync path:
//   begin_clock_sync_request() -> DMA/SPI -> end_clock_sync_request(...)
//   -> IRQ_N low -> begin_clock_sync_response(t3) -> DMA/SPI ->
//   end_transaction(152) -> IRQ_N high
//
// The ESP32-S3 master always clocks the complete maximum transaction. A
// short/aborted transaction is reported as a boundary fault on the next
// frame; it is never silently treated as a valid event batch.
class M6CarrierSpiSlaveTransport {
  public:
    explicit M6CarrierSpiSlaveTransport(M6CarrierCaptureCore& capture);

    // Stage one complete frame when no previous frame is in flight. Returns
    // true only when a new TX buffer was prepared.
    bool service();

    bool frame_ready() const { return frame_ready_; }
    bool irq_asserted() const {
        return frame_ready_ || clock_sync_response_pending_;
    }
    bool transaction_active() const { return transaction_active_; }
    bool clock_sync_request_active() const {
        return transaction_kind_ == TransactionKind::kClockSyncRequest;
    }
    bool clock_sync_response_pending() const {
        return clock_sync_response_pending_;
    }
    std::size_t wire_frame_bytes() const { return wire_frame_bytes_; }
    std::size_t tx_transfer_bytes() const { return kM6CarrierMaxFrameBytes; }
    const std::uint8_t* tx_buffer() const { return tx_buffer_.data(); }

    // Called by the platform adapter at CS assertion/release. A master must
    // clock exactly the fixed maximum transaction size.
    bool begin_transaction();
    bool begin_clock_sync_request();
    bool begin_clock_sync_response(std::uint64_t carrier_sent_us);
    bool end_transaction(std::size_t transferred_bytes);
    bool end_clock_sync_request(std::size_t transferred_bytes,
                                const std::uint8_t* rx_buffer,
                                std::size_t rx_buffer_bytes,
                                std::uint64_t carrier_received_us);

    void reset();

  private:
    enum class TransactionKind : std::uint8_t {
        kNone,
        kEvent,
        kClockSyncRequest,
        kClockSyncResponse,
    };

    M6CarrierCaptureCore& capture_;
    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> tx_buffer_{};
    std::size_t wire_frame_bytes_ = 0;
    bool frame_ready_ = false;
    bool transaction_active_ = false;
    TransactionKind transaction_kind_ = TransactionKind::kNone;
    bool clock_sync_response_pending_ = false;
    bool clock_sync_response_valid_ = false;
    std::uint64_t clock_sync_carrier_received_us_ = 0;
};

}  // namespace smartgear::carrier
