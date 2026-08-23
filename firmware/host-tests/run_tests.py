#!/usr/bin/env python3
"""Build/run the pure C++ business layer and validate emitted NetEvent JSON."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BUILD = HERE / "build"
SCHEMA = REPO / "docs" / "net-event-v0.1.schema.json"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(command))
    return subprocess.run(command, cwd=HERE, check=True, text=True)


def main() -> None:
    run(["cmake", "-S", ".", "-B", str(BUILD), "-DCMAKE_BUILD_TYPE=Debug"])
    run(["cmake", "--build", str(BUILD), "--parallel"])
    result = subprocess.run(
        [str(BUILD / "net_event_tests")],
        cwd=HERE,
        check=True,
        text=True,
        capture_output=True,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    events = []
    for line in result.stdout.splitlines():
        if not line.startswith("JSON_EVENT "):
            continue
        event = json.loads(line.removeprefix("JSON_EVENT "))
        validator.validate(event)
        events.append(event)
    if len(events) != 2:
        raise AssertionError(f"expected 2 schema events, got {len(events)}")
    print(f"JSON_SCHEMA_OK ({len(events)} events)")


if __name__ == "__main__":
    main()
