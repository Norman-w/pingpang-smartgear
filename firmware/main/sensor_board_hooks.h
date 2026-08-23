#pragma once

#include <cstddef>
#include <cstdint>

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

}
