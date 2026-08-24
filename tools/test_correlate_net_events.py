#!/usr/bin/env python3
"""Regression tests for the timestamp-only replay correlator."""

from __future__ import annotations

import io
import unittest

from correlate_net_events import (
    ExternalMarker,
    correlate,
    load_events,
    load_external_markers,
)


class CorrelateNetEventsTests(unittest.TestCase):
    def test_offset_and_inclusive_window(self) -> None:
        events = load_events(
            io.StringIO(
                '{"type":"net_event","event_id":"e-1","timestamp_us":1000}\n'
                'JSON_EVENT {"type":"net_event","event_id":"e-2","timestamp_us":5000}\n'
            )
        )
        markers = load_external_markers(
            io.StringIO(
                "record_id,external_timestamp_us,source\n"
                "exact,1100,camera\n"
                "edge,1150,camera\n"
                "far,1400,camera\n"
                "second,5100,camera\n"
            )
        )

        results = correlate(
            events, markers, external_offset_us=-100, window_us=50
        )

        self.assertEqual(
            [item["record_id"] for item in results[0]["matches"]],
            ["exact", "edge"],
        )
        self.assertEqual(results[0]["matches"][0]["delta_us"], 0)
        self.assertEqual(results[0]["matches"][1]["delta_us"], 50)
        self.assertEqual(
            [item["record_id"] for item in results[1]["matches"]], ["second"]
        )

    def test_empty_and_default_metadata_are_deterministic(self) -> None:
        markers = load_external_markers(
            io.StringIO("external_timestamp_us\n42\n")
        )
        self.assertEqual(markers, [ExternalMarker("row-2", 42, "external")])
        result = correlate(
            [{"event_id": "event", "timestamp_us": 100}],
            markers,
            window_us=0,
        )
        self.assertEqual(result[0]["matches"], [])

    def test_malformed_input_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            load_events(io.StringIO('{"type":"net_event"}\n'))
        with self.assertRaises(ValueError):
            load_external_markers(io.StringIO("record_id\nmarker\n"))
        with self.assertRaises(ValueError):
            correlate(
                [{"event_id": "event", "timestamp_us": 100}],
                [ExternalMarker("marker", 100, "camera")],
                window_us=-1,
            )


if __name__ == "__main__":
    unittest.main()
