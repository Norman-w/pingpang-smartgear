#include "sensor_health_gate.h"

#include "net_event_aggregator.h"

namespace smartgear {
namespace {

void apply_fail_closed(NetEventAggregator& aggregator, const char* reason) {
    aggregator.set_calibration(reason, false);
    aggregator.set_beam_health(0, false);
    aggregator.set_piezo_baseline(false);
}

}  // namespace

bool apply_sensor_health_snapshot(
    NetEventAggregator& aggregator,
    const char* calibration_id,
    const std::size_t calibration_id_capacity,
    const SensorHealthSnapshot& snapshot) {
    if (!sensor_health_snapshot_is_well_formed(
            calibration_id, calibration_id_capacity, snapshot.healthy_beam_mask,
            snapshot.beam_health_valid, snapshot.calibration_valid)) {
        apply_fail_closed(aggregator, "health-snapshot-invalid");
        return false;
    }

    const std::uint16_t healthy_beam_mask = snapshot.beam_health_valid
                                                ? snapshot.healthy_beam_mask
                                                : static_cast<std::uint16_t>(0);
    aggregator.set_calibration(calibration_id, snapshot.calibration_valid);
    aggregator.set_beam_health(healthy_beam_mask, snapshot.beam_health_valid);
    aggregator.set_piezo_baseline(snapshot.piezo_baseline_valid);
    return true;
}

void apply_sensor_health_unavailable(NetEventAggregator& aggregator) {
    apply_fail_closed(aggregator, "health-snapshot-unavailable");
}

}  // namespace smartgear
