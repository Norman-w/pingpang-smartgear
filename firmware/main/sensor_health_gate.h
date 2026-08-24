#pragma once

#include <cstddef>

#include "sensor_self_test.h"

namespace smartgear {

class NetEventAggregator;

// Apply one board health snapshot to the event state machine. The same gate is
// used by the ESP32 runtime and host tests so a malformed board hook cannot be
// accidentally treated differently in production and replay code.
//
// On failure the aggregator is put into a deterministic fail-closed state and
// false is returned. The calibration ID is only read when its bounded buffer
// passes the snapshot shape check.
bool apply_sensor_health_snapshot(NetEventAggregator& aggregator,
                                  const char* calibration_id,
                                  std::size_t calibration_id_capacity,
                                  const SensorHealthSnapshot& snapshot);

// Apply the state used when the board hook is absent or reports an I/O error.
void apply_sensor_health_unavailable(NetEventAggregator& aggregator);

}  // namespace smartgear
