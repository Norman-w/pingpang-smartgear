#!/usr/bin/env python3
"""Regression tests for the M6 NPN interface margin calculator."""

from __future__ import annotations

import contextlib
import io
import unittest

import validate_m6_interface


class M6InterfaceTests(unittest.TestCase):
    def test_reference_design_passes(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            validate_m6_interface.main()
        self.assertIn("M6_INTERFACE_OK", output.getvalue())
        self.assertIn("P_R=", output.getvalue())

    def test_maximum_current_is_below_recorded_sensor_limit(self) -> None:
        r_min = validate_m6_interface.R_NOMINAL * (
            1.0 - validate_m6_interface.R_TOLERANCE
        )
        current_max = (
            validate_m6_interface.V_SENSOR_MAX
            - validate_m6_interface.LED_VF
        ) / r_min
        self.assertLess(current_max, validate_m6_interface.MAX_SENSOR_LOAD_A)


if __name__ == "__main__":
    unittest.main()
