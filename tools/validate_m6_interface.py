#!/usr/bin/env python3
"""Validate first-pass electrical margins for the M6 NPN optocoupler input."""

from __future__ import annotations


V_SENSOR_MIN = 10.0
V_SENSOR_MAX = 30.0
LED_VF = 1.2
R_NOMINAL = 1_800.0
R_TOLERANCE = 0.01
R_POWER_RATING = 1.0
MAX_SENSOR_LOAD_A = 0.150
MIN_LED_CURRENT_A = 0.0045
MAX_LED_CURRENT_A = 0.020
MAX_RESISTOR_POWER_W = 0.5
PULLUP_OHM = 4_700.0
FILTER_CAP_F = 1e-9
MAX_ALLOWED_RC_US = 10.0


def main() -> None:
    r_min = R_NOMINAL * (1.0 - R_TOLERANCE)
    r_max = R_NOMINAL * (1.0 + R_TOLERANCE)
    current_min = (V_SENSOR_MIN - LED_VF) / r_max
    current_max = (V_SENSOR_MAX - LED_VF) / r_min
    resistor_power_max = (V_SENSOR_MAX - LED_VF) ** 2 / r_min
    rc_us = PULLUP_OHM * FILTER_CAP_F * 1e6

    assert current_min >= MIN_LED_CURRENT_A, (
        f"minimum optocoupler LED current too low: {current_min:.6f} A"
    )
    assert current_max <= MAX_LED_CURRENT_A, (
        f"maximum optocoupler LED current too high: {current_max:.6f} A"
    )
    assert current_max < MAX_SENSOR_LOAD_A, (
        f"input load exceeds recorded sensor limit: {current_max:.6f} A"
    )
    assert resistor_power_max <= MAX_RESISTOR_POWER_W, (
        f"resistor power margin too small: {resistor_power_max:.3f} W"
    )
    assert resistor_power_max < R_POWER_RATING, (
        f"resistor rating too small: {resistor_power_max:.3f} W"
    )
    assert rc_us <= MAX_ALLOWED_RC_US, f"input RC too slow: {rc_us:.3f} us"

    print(
        "M6_INTERFACE_OK "
        f"(Iled={current_min * 1e3:.2f}..{current_max * 1e3:.2f}mA, "
        f"P_R={resistor_power_max:.3f}W, RC={rc_us:.2f}us)"
    )


if __name__ == "__main__":
    main()
