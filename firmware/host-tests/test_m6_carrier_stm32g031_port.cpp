#include "m6_carrier_protocol.h"
#include "m6_carrier_stm32g031_port.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>

namespace {

using Port = smartgear::carrier::stm32g031::M6CarrierStm32G031Port;
using Pin = smartgear::carrier::stm32g031::PinDescriptor;
using SpiMap = smartgear::carrier::stm32g031::Spi1PinMap;

struct FakePlatform {
    static inline std::size_t input_count = 0;
    static inline std::size_t timer_count = 0;
    static inline std::size_t spi_count = 0;
    static inline std::size_t irq_config_count = 0;
    static inline std::size_t irq_drive_count = 0;
    static inline bool irq_high = true;
    static inline const std::uint8_t* tx_buffer = nullptr;
    static inline std::size_t tx_bytes = 0;
    static inline std::uint8_t spi_mode = 0xffU;
    static inline bool map_ok = false;
    static inline bool fail_input = false;

    static void reset() {
        input_count = 0;
        timer_count = 0;
        spi_count = 0;
        irq_config_count = 0;
        irq_drive_count = 0;
        irq_high = true;
        tx_buffer = nullptr;
        tx_bytes = 0;
        spi_mode = 0xffU;
        map_ok = false;
        fail_input = false;
    }

    static bool configure_input(std::uint8_t channel, Pin pin) {
        ++input_count;
        constexpr std::array<std::uint8_t, 10> expected_exti = {
            1U, 2U, 3U, 4U, 5U, 6U, 7U, 9U, 10U, 15U,
        };
        if (fail_input || channel >= expected_exti.size() ||
            pin.exti_line != expected_exti[channel]) {
            return false;
        }
        return pin.port == smartgear::carrier::stm32g031::GpioPort::kA;
    }

    static bool configure_timer() {
        ++timer_count;
        return true;
    }

    static bool configure_spi(SpiMap map,
                              const std::uint8_t* buffer,
                              std::size_t bytes,
                              std::uint8_t mode) {
        ++spi_count;
        tx_buffer = buffer;
        tx_bytes = bytes;
        spi_mode = mode;
        map_ok =
            map.cs_n.package_pin == 15U && map.sck.package_pin == 27U &&
            map.miso.package_pin == 28U && map.mosi.package_pin == 29U;
        return map_ok && buffer != nullptr && bytes == 152U && mode == 0U;
    }

    static bool configure_irq(Pin pin) {
        ++irq_config_count;
        return pin.package_pin == 32U;
    }

    static void drive_irq(bool high) {
        ++irq_drive_count;
        irq_high = high;
    }
};

void require(bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

smartgear::carrier::stm32g031::PlatformHooks hooks() {
    return {
        &FakePlatform::configure_input,
        &FakePlatform::configure_timer,
        &FakePlatform::configure_spi,
        &FakePlatform::configure_irq,
        &FakePlatform::drive_irq,
    };
}

}  // namespace

int main() {
    using namespace smartgear;
    using namespace smartgear::carrier::stm32g031;

    static_assert(kCarrierInputPins[9].exti_line == 15U);
    require(kCarrierInputPins.size() == 10U,
            "STM32G031 port must expose ten input descriptors");
    require(kHostSpiClockHz == 1'000'000U && kSpiMode == 0U,
            "STM32G031 port constants must match the carrier contract");
    require(kSpiCsN.exti_line == 0U && kCarrierInputPins[0].exti_line == 1U,
            "PB0 must own EXTI0 while the ten input lines remain unique");

    FakePlatform::reset();
    Port port;
    require(!port.on_input_edge(0, 0, 100),
            "edges before port initialization must be rejected");
    require(port.initialize(hooks()),
            "complete STM32G031 platform hooks must initialize");
    require(port.initialized() && FakePlatform::input_count == 10U &&
                FakePlatform::timer_count == 1U &&
                FakePlatform::spi_count == 1U &&
                FakePlatform::irq_config_count == 1U &&
                FakePlatform::tx_buffer == port.tx_buffer() &&
                FakePlatform::tx_bytes == kM6CarrierMaxFrameBytes &&
                FakePlatform::spi_mode == kSpiMode && FakePlatform::map_ok &&
                FakePlatform::irq_high,
            "initialization must bind the exact pin map and release IRQ");

    std::array<std::uint8_t, kM6CarrierMaxFrameBytes> sync_request{};
    require(m6_carrier_encode_clock_sync_request(sync_request.data(),
                                                 sync_request.size()) ==
                kM6CarrierClockSyncRequestBytes &&
                port.on_cs_asserted() &&
                port.clock_sync_request_active() &&
                port.on_cs_released(kM6CarrierMaxFrameBytes,
                                    sync_request.data(), sync_request.size(),
                                    900'000) &&
                port.irq_asserted() && !FakePlatform::irq_high,
            "STM32 port must receive a fixed clock-sync request and assert IRQ");
    require(port.on_cs_asserted(900'125),
            "STM32 port must start the clock-sync response at CS assertion");
    M6CarrierClockSyncResponse sync_response{};
    require(m6_carrier_decode_clock_sync_response(
                port.tx_buffer(), kM6CarrierClockSyncResponseBytes,
                &sync_response) &&
                sync_response.valid &&
                sync_response.carrier_received_us == 900'000 &&
                sync_response.carrier_sent_us == 900'125 &&
                port.on_cs_released(kM6CarrierMaxFrameBytes) &&
                !port.irq_asserted() && FakePlatform::irq_high,
            "STM32 port must return t2/t3 and release IRQ after sync");

    require(port.on_input_edge(0, 0, 1'000) &&
                port.on_input_edge(0, 1, 1'800) &&
                port.on_input_edge(9, 0, 2'000),
            "initialized port must forward valid ISR edges");
    require(port.service() && port.frame_ready() && port.irq_asserted() &&
                !FakePlatform::irq_high &&
                port.wire_frame_bytes() > kM6CarrierHeaderBytes,
            "service must stage a frame and assert active-low IRQ");

    M6CarrierFrame staged{};
    require(m6_carrier_decode_edges(port.tx_buffer(), port.wire_frame_bytes(),
                                    &staged) == M6CarrierDecodeStatus::kOk &&
                staged.edge_count == 3U && staged.edges[1].timestamp_us == 1'800,
            "staged STM32G031 TX must contain the captured edges");
    require(port.on_cs_asserted() && port.transaction_active() &&
                !port.service(),
            "CS assertion must lock the TX staging buffer");
    require(port.on_cs_released(kM6CarrierMaxFrameBytes) &&
                !port.frame_ready() && !port.transaction_active() &&
                !port.irq_asserted() && FakePlatform::irq_high,
            "complete fixed-size transaction must release IRQ");

    require(port.on_input_edge(1, 0, 3'000) && port.service() &&
                port.on_cs_asserted() &&
                !port.on_cs_released(kM6CarrierMaxFrameBytes - 1U),
            "short transaction must be rejected at the port boundary");
    require(port.on_input_edge(1, 1, 3'700) && port.service(),
            "capture must continue after a short transaction");
    M6CarrierFrame fault{};
    require(m6_carrier_decode_edges(port.tx_buffer(), port.wire_frame_bytes(),
                                    &fault) == M6CarrierDecodeStatus::kOk &&
                (fault.flags & kM6CarrierFlagTimestampInvalid) != 0U,
            "short transaction must mark the next staged frame invalid");
    require(port.on_cs_asserted() &&
                port.on_cs_released(kM6CarrierMaxFrameBytes),
            "fault frame must still be consumable at fixed length");

    require(port.on_input_edge(2, 0, 4'000) && port.service() &&
                port.frame_ready(),
            "a later frame must still be stageable");
    port.mark_capture_fault();
    require(port.on_cs_asserted() &&
                port.on_cs_released(kM6CarrierMaxFrameBytes),
            "an explicitly marked capture fault must remain consumable");
    require(port.on_input_edge(2, 1, 4'700) && port.service(),
            "capture must continue after an input-side fault");
    M6CarrierFrame input_fault{};
    require(m6_carrier_decode_edges(port.tx_buffer(), port.wire_frame_bytes(),
                                    &input_fault) ==
                M6CarrierDecodeStatus::kOk &&
                (input_fault.flags & kM6CarrierFlagTimestampInvalid) != 0U,
            "an input-side ambiguity must mark the next frame invalid");
    require(port.on_cs_asserted() &&
                port.on_cs_released(kM6CarrierMaxFrameBytes),
            "the input-fault frame must remain consumable at fixed length");
    port.reset_runtime_state();
    require(!port.frame_ready() && !port.transaction_active() &&
                !port.irq_asserted() && FakePlatform::irq_high,
            "runtime reset must clear FIFO, staging and IRQ");

    FakePlatform::reset();
    FakePlatform::fail_input = true;
    Port failed;
    require(!failed.initialize(hooks()) && !failed.initialized() &&
                FakePlatform::input_count == 1U,
            "a failed input hook must stop initialization before peripherals");

    std::cout << "M6_CARRIER_STM32G031_PORT_OK (pinmap, init, EXTI, SPI-DMA-contract, clock-sync, IRQ-CS, reset, fail-closed)\n";
    return 0;
}
