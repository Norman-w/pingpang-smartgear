#pragma once

#include <cstddef>
#include <cstdint>

// A board-specific implementation fills one complete four-timestamp
// exchange. `exchange_verified` is intentionally explicit: the weak default
// is unavailable, and the firmware must not infer synchronization from a
// compile-time offset or from an event frame.
struct SmartgearM6CarrierClockSyncReading {
    std::uint64_t host_sent_us = 0;
    std::uint64_t host_received_us = 0;
    std::uint64_t carrier_received_us = 0;
    std::uint64_t carrier_sent_us = 0;
    bool exchange_verified = false;
};

// The board/app layer supplies calibration and self-test state through this
// weak C hook. Returning false means the snapshot is unavailable; firmware
// must remain fail-closed and keep NetEvent state unknown.
extern "C" {

bool smartgear_board_read_sensor_health(char* calibration_id,
                                        std::size_t calibration_id_capacity,
                                        std::uint16_t* healthy_beam_mask,
                                        bool* beam_health_valid,
                                        bool* piezo_baseline_valid,
                                        bool* calibration_valid);

bool smartgear_board_read_m6_carrier_clock_sync(
    SmartgearM6CarrierClockSyncReading* reading);

}
