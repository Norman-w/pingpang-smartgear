#include "m6_carrier_stm32g031_port.h"

namespace smartgear::carrier::stm32g031 {

M6CarrierStm32G031Port::M6CarrierStm32G031Port()
    : transport_(capture_) {}

bool M6CarrierStm32G031Port::initialize(const PlatformHooks& hooks) {
    if (hooks.configure_input_exti == nullptr ||
        hooks.configure_timer_1mhz == nullptr ||
        hooks.configure_spi1_slave_dma == nullptr ||
        hooks.configure_irq_output == nullptr || hooks.drive_irq_n == nullptr) {
        return false;
    }

    hooks_ = hooks;
    initialized_ = false;
    transport_.reset();

    for (std::uint8_t channel = 0;
         channel < static_cast<std::uint8_t>(kCarrierInputPins.size());
         ++channel) {
        if (!hooks_.configure_input_exti(channel,
                                         kCarrierInputPins[channel])) {
            return false;
        }
    }
    if (!hooks_.configure_timer_1mhz()) {
        return false;
    }
    if (!hooks_.configure_irq_output(kCarrierIrqN)) {
        return false;
    }
    if (!hooks_.configure_spi1_slave_dma(
            kSpi1PinMap, transport_.tx_buffer(), kM6CarrierMaxFrameBytes,
            kSpiMode)) {
        return false;
    }

    initialized_ = true;
    update_irq();
    return true;
}

bool M6CarrierStm32G031Port::on_input_edge(
    const std::uint8_t logical_channel,
    const std::uint8_t level,
    const std::uint64_t timestamp_us) {
    if (!initialized_) {
        return false;
    }
    return capture_.on_edge(logical_channel, level, timestamp_us);
}

void M6CarrierStm32G031Port::mark_capture_fault() {
    capture_.mark_transport_fault();
}

bool M6CarrierStm32G031Port::service() {
    if (!initialized_) {
        return false;
    }
    const bool staged = transport_.service();
    update_irq();
    return staged;
}

bool M6CarrierStm32G031Port::on_cs_asserted() {
    return on_cs_asserted(0U);
}

bool M6CarrierStm32G031Port::on_cs_asserted(
    const std::uint64_t carrier_timestamp_us) {
    if (!initialized_) {
        return false;
    }
    bool started = false;
    if (transport_.clock_sync_response_pending()) {
        started =
            transport_.begin_clock_sync_response(carrier_timestamp_us);
    } else if (transport_.frame_ready()) {
        started = transport_.begin_transaction();
    } else {
        started = transport_.begin_clock_sync_request();
    }
    update_irq();
    return started;
}

bool M6CarrierStm32G031Port::on_cs_released(
    const std::size_t transferred_bytes) {
    return on_cs_released(transferred_bytes, nullptr, 0U, 0U);
}

bool M6CarrierStm32G031Port::on_cs_released(
    const std::size_t transferred_bytes,
    const std::uint8_t* rx_buffer,
    const std::size_t rx_buffer_bytes,
    const std::uint64_t carrier_timestamp_us) {
    if (!initialized_) {
        return false;
    }
    const bool complete = transport_.clock_sync_request_active()
                              ? transport_.end_clock_sync_request(
                                    transferred_bytes, rx_buffer,
                                    rx_buffer_bytes, carrier_timestamp_us)
                              : transport_.end_transaction(transferred_bytes);
    update_irq();
    return complete;
}

void M6CarrierStm32G031Port::reset_runtime_state() {
    transport_.reset();
    if (initialized_) {
        update_irq();
    }
}

void M6CarrierStm32G031Port::update_irq() {
    if (hooks_.drive_irq_n != nullptr) {
        // irq_asserted() means the active-low line must be driven low.
        hooks_.drive_irq_n(!transport_.irq_asserted());
    }
}

}  // namespace smartgear::carrier::stm32g031
