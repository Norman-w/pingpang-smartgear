#include "m6_carrier_capture_core.h"

#include <limits>

#if defined(ESP_PLATFORM)
#include "esp_attr.h"
#define SMARTGEAR_CARRIER_IRAM_ATTR IRAM_ATTR
#else
#define SMARTGEAR_CARRIER_IRAM_ATTR
#endif

namespace smartgear::carrier {

bool SMARTGEAR_CARRIER_IRAM_ATTR M6CarrierCaptureCore::on_edge(
    const std::uint8_t channel,
    const std::uint8_t level,
    const std::uint64_t timestamp_us) {
    if (channel >= 10U || level > 1U) {
        pending_flags_.fetch_or(kM6CarrierFlagTimestampInvalid,
                                std::memory_order_acq_rel);
        dropped_edge_count_.fetch_add(1, std::memory_order_acq_rel);
        return false;
    }
    if (has_last_timestamp_ && timestamp_us < last_timestamp_us_) {
        pending_flags_.fetch_or(kM6CarrierFlagTimestampInvalid,
                                std::memory_order_acq_rel);
        dropped_edge_count_.fetch_add(1, std::memory_order_acq_rel);
        return false;
    }

    const std::uint32_t head = head_.load(std::memory_order_relaxed);
    const std::uint32_t tail = tail_.load(std::memory_order_acquire);
    if (head - tail >= kCaptureFifoCapacity) {
        pending_flags_.fetch_or(kM6CarrierFlagFifoOverflow,
                                std::memory_order_acq_rel);
        dropped_edge_count_.fetch_add(1, std::memory_order_acq_rel);
        return false;
    }

    fifo_[head % kCaptureFifoCapacity] = {channel, level, timestamp_us};
    head_.store(head + 1U, std::memory_order_release);
    last_timestamp_us_ = timestamp_us;
    has_last_timestamp_ = true;
    return true;
}

bool M6CarrierCaptureCore::pop_frame(M6CarrierFrame* frame) {
    if (frame == nullptr) {
        return false;
    }
    const std::uint32_t tail = tail_.load(std::memory_order_relaxed);
    const std::uint32_t head = head_.load(std::memory_order_acquire);
    if (tail == head) {
        return false;
    }

    const std::uint32_t available = head - tail;
    const std::size_t requested_count =
        available < kM6CarrierMaxEdgesPerFrame
            ? static_cast<std::size_t>(available)
            : kM6CarrierMaxEdgesPerFrame;

    M6CarrierFrame output;
    output.sequence = sequence_++;
    output.flags = pending_flags_.exchange(0, std::memory_order_acq_rel);
    output.base_timestamp_us = fifo_[tail % kCaptureFifoCapacity].timestamp_us;

    std::size_t count = 0;
    for (; count < requested_count; ++count) {
        const M6CarrierEdge edge =
            fifo_[(tail + static_cast<std::uint32_t>(count)) %
                  kCaptureFifoCapacity];
        const bool representable =
            edge.timestamp_us >= output.base_timestamp_us &&
            edge.timestamp_us - output.base_timestamp_us <=
                std::numeric_limits<std::uint32_t>::max();
        if (!representable) {
            output.flags = static_cast<std::uint8_t>(
                output.flags | kM6CarrierFlagTimestampInvalid);
            break;
        }
        output.edges[count] = edge;
    }
    // The first edge always has a zero delta, so count is at least one here.
    output.edge_count = static_cast<std::uint8_t>(count);
    tail_.store(tail + static_cast<std::uint32_t>(count),
                std::memory_order_release);
    *frame = output;
    return true;
}

std::size_t M6CarrierCaptureCore::pop_encoded_frame(
    std::uint8_t* output,
    const std::size_t capacity) {
    if (output == nullptr || capacity < kM6CarrierMaxFrameBytes) {
        return 0;
    }
    M6CarrierFrame frame;
    if (!pop_frame(&frame)) {
        return 0;
    }
    return m6_carrier_encode_edges(frame, output, capacity);
}

void M6CarrierCaptureCore::mark_transport_fault() {
    pending_flags_.fetch_or(kM6CarrierFlagTimestampInvalid,
                            std::memory_order_acq_rel);
}

bool M6CarrierCaptureCore::has_pending_edges() const {
    return head_.load(std::memory_order_acquire) !=
           tail_.load(std::memory_order_acquire);
}

void M6CarrierCaptureCore::reset() {
    head_.store(0, std::memory_order_release);
    tail_.store(0, std::memory_order_release);
    pending_flags_.store(0, std::memory_order_release);
    dropped_edge_count_.store(0, std::memory_order_release);
    sequence_ = 0;
    last_timestamp_us_ = 0;
    has_last_timestamp_ = false;
}

}  // namespace smartgear::carrier
