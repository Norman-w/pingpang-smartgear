#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace smartgear::carrier_config {

// Candidate only: this mapping is for the SmartPaddle ESP32-S3-WROOM-1
// reference board. It becomes a production mapping only after the final PCB
// and boot log are checked.
constexpr int kSpiSckGpio = 10;
constexpr int kSpiMosiGpio = 11;
constexpr int kSpiMisoGpio = 12;
constexpr int kSpiCsGpio = 13;
constexpr int kIrqGpio = 14;
constexpr int kResetGpio = 5;

// Keep the production path disabled until the carrier PCB, reset/IRQ
// waveform, NPN polarity and a measured host<->carrier clock sync are all
// signed off. This is deliberately a build-time gate: a stale candidate pin
// map must not steal the direct GPIOs or create plausible timestamps.
constexpr bool kUseM6Carrier = false;
constexpr int kSpiClockHz = 1'000'000;
// The carrier protocol now has a real two-transaction sync request/response.
// Set this false only when a custom board supplies the four timestamps through
// smartgear_board_read_m6_carrier_clock_sync() instead.
constexpr bool kUseCarrierSpiClockSync = true;
// Optional fallback for a separately recorded calibration constant. The
// normal path keeps this false and confirms a runtime four-timestamp exchange
// through smartgear_board_read_m6_carrier_clock_sync().
constexpr bool kCarrierClockOffsetConfirmed = false;
constexpr std::int64_t kCarrierToHostOffsetUs = 0;

constexpr std::array<int, 6> kSmartPaddleCarrierGpioPins = {
    kSpiSckGpio,
    kSpiMosiGpio,
    kSpiMisoGpio,
    kSpiCsGpio,
    kIrqGpio,
    kResetGpio,
};

constexpr bool all_unique(const std::array<int, 6>& pins) {
    for (std::size_t left = 0; left < pins.size(); ++left) {
        for (std::size_t right = left + 1; right < pins.size(); ++right) {
            if (pins[left] == pins[right]) {
                return false;
            }
        }
    }
    return true;
}

constexpr bool all_valid(const std::array<int, 6>& pins) {
    for (const int pin : pins) {
        if (pin < 0 || pin > 48) {
            return false;
        }
    }
    return true;
}

static_assert(all_unique(kSmartPaddleCarrierGpioPins),
              "carrier SPI/control GPIOs must be unique");
static_assert(all_valid(kSmartPaddleCarrierGpioPins),
              "carrier candidate GPIO is outside ESP32-S3 range");

}  // namespace smartgear::carrier_config
