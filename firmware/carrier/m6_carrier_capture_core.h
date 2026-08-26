#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>

#include "m6_carrier_protocol.h"

namespace smartgear::carrier {

constexpr std::size_t kCaptureFifoCapacity = 64;

// Platform-neutral carrier-side capture core. GPIO/timer ISR glue calls
// on_edge(); the SPI slave task calls pop_frame(). There is deliberately no
// debounce or minimum-pulse filter here: the M6 response and the actual
// produced pulse width are hardware evidence, not software assumptions.
class M6CarrierCaptureCore {
  public:
    bool on_edge(std::uint8_t channel,
                 std::uint8_t level,
                 std::uint64_t timestamp_us);
    bool pop_frame(M6CarrierFrame* frame);

    // The SPI-slave task can use this directly when its TX staging buffer is
    // at least one maximum frame. A too-small buffer returns zero without
    // consuming the FIFO, so a transport-size mistake cannot silently lose
    // captured edges.
    std::size_t pop_encoded_frame(std::uint8_t* output,
                                  std::size_t capacity);

    // A platform transport can mark an aborted SPI transaction as an input
    // boundary failure. The flag is attached to the next available frame.
    void mark_transport_fault();

    bool has_pending_edges() const;
    std::uint32_t dropped_edge_count() const {
        return dropped_edge_count_.load(std::memory_order_acquire);
    }
    void reset();

  private:
    std::array<M6CarrierEdge, kCaptureFifoCapacity> fifo_{};
    std::atomic<std::uint32_t> head_{0};
    std::atomic<std::uint32_t> tail_{0};
    std::atomic<std::uint8_t> pending_flags_{0};
    std::atomic<std::uint32_t> dropped_edge_count_{0};
    std::uint32_t sequence_ = 0;
    std::uint64_t last_timestamp_us_ = 0;
    bool has_last_timestamp_ = false;
};

}  // namespace smartgear::carrier
