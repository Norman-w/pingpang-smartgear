#pragma once

#include <cstddef>
#include <cstdint>

// The board/app layer may synchronously copy a completed or partial waveform
// to its existing diagnostics/replay store. The sample pointers are valid only
// for the duration of the call; the hook must copy them before returning.
// Returning false leaves the frame available in the local RAM archive.
extern "C" {

bool smartgear_board_on_piezo_waveform(
    const char* reference,
    std::uint64_t trigger_us,
    std::size_t pre_trigger_samples,
    const std::int16_t* left_samples,
    std::size_t left_count,
    const std::int16_t* right_samples,
    std::size_t right_count,
    bool complete);

}
