#include "beam_capture.h"
#include "beam_channel_map.h"
#include "feedback.h"
#include "feedback_gpio.h"
#include "m6_carrier_adapter.h"
#include "m6_carrier_config.h"
#include "net_event_aggregator.h"
#include "net_event_delivery.h"
#include "net_event_transport.h"
#include "net_sensor_config.h"
#include "piezo_capture.h"
#include "piezo_adc_continuous.h"
#include "piezo_waveform.h"
#include "piezo_waveform_archive.h"
#include "piezo_waveform_hook.h"
#include "sensor_board_hooks.h"
#include "sensor_health_gate.h"
#include "sensor_self_test.h"

#ifdef ESP_PLATFORM

#include <array>
#include <cstdio>
#include <string>
#include <utility>

#include "driver/gpio.h"
#include "m6_carrier_spi.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"

namespace {

constexpr char kTag[] = "smartgear";

enum class SensorKind : std::uint8_t {
    kBeam,
    kPiezo,
};

struct SensorRoute {
    SensorKind kind;
    std::uint8_t channel;
    gpio_num_t pin;
};

struct SensorEdge {
    SensorKind kind;
    std::uint8_t channel;
    int level;
    std::uint64_t timestamp_us;
};

QueueHandle_t s_sensor_queue = nullptr;
portMUX_TYPE s_sensor_queue_overflow_mux = portMUX_INITIALIZER_UNLOCKED;
volatile bool s_sensor_queue_overflow = false;
std::array<SensorRoute, smartgear::config::kBeamCount +
                            smartgear::config::kPiezoCount>
    s_routes{};

constexpr bool carrier_candidate_is_disjoint_from_direct_io() {
    for (const int carrier_pin :
         smartgear::carrier_config::kSmartPaddleCarrierGpioPins) {
        for (const int beam_pin : smartgear::config::kBeamGpioPins) {
            if (carrier_pin == beam_pin) {
                return false;
            }
        }
        for (const int piezo_pin :
             smartgear::config::kPiezoComparatorGpioPins) {
            if (carrier_pin == piezo_pin) {
                return false;
            }
        }
        for (const int adc_pin : smartgear::config::kPiezoAdcGpioPins) {
            if (carrier_pin == adc_pin) {
                return false;
            }
        }
        for (const int feedback_pin : smartgear::config::kFeedbackGpioPins) {
            if (carrier_pin == feedback_pin) {
                return false;
            }
        }
    }
    return true;
}

static_assert(!smartgear::carrier_config::kUseM6Carrier ||
                  carrier_candidate_is_disjoint_from_direct_io(),
              "M6 carrier candidate pins conflict with direct sensor or "
              "feedback GPIOs; audit the final board mapping first");

void IRAM_ATTR sensor_isr(void* argument) {
    auto* route = static_cast<SensorRoute*>(argument);
    const SensorEdge edge{
        route->kind,
        route->channel,
        gpio_get_level(route->pin),
        static_cast<std::uint64_t>(esp_timer_get_time()),
    };
    BaseType_t higher_priority_task_woken = pdFALSE;
    if (s_sensor_queue != nullptr) {
        if (xQueueSendFromISR(s_sensor_queue, &edge, &higher_priority_task_woken) !=
            pdTRUE) {
            portENTER_CRITICAL_ISR(&s_sensor_queue_overflow_mux);
            s_sensor_queue_overflow = true;
            portEXIT_CRITICAL_ISR(&s_sensor_queue_overflow_mux);
        }
    }
    if (higher_priority_task_woken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}

bool consume_sensor_queue_overflow() {
    portENTER_CRITICAL(&s_sensor_queue_overflow_mux);
    const bool overflowed = s_sensor_queue_overflow;
    s_sensor_queue_overflow = false;
    portEXIT_CRITICAL(&s_sensor_queue_overflow_mux);
    return overflowed;
}

void on_piezo_adc_sample(const std::uint8_t channel,
                         const std::int16_t raw_sample,
                         const std::uint64_t timestamp_us,
                         void* context) {
    auto* waveform = static_cast<smartgear::PiezoWaveformCapture*>(context);
    if (waveform != nullptr) {
        waveform->feed_sample(channel, raw_sample, timestamp_us);
    }
}

void configure_sensor_inputs(const bool use_m6_carrier) {
    s_sensor_queue = xQueueCreate(32, sizeof(SensorEdge));
    ESP_ERROR_CHECK(s_sensor_queue != nullptr ? ESP_OK : ESP_ERR_NO_MEM);

    // 既有 SmartPaddle 固件也采用 GPIO comparator + 时间戳模式；这里保留
    // 同一采集边界，后续由业务层消费，不在 ISR 中做事件归并或 JSON 序列化。
    const esp_err_t isr_service_error =
        gpio_install_isr_service(ESP_INTR_FLAG_IRAM);
    ESP_ERROR_CHECK(isr_service_error == ESP_OK ||
                            isr_service_error == ESP_ERR_INVALID_STATE
                        ? ESP_OK
                        : isr_service_error);

    std::size_t route_index = 0;
    if (!use_m6_carrier) {
        for (std::size_t channel = 0; channel < smartgear::config::kBeamCount;
             ++channel, ++route_index) {
            auto& route = s_routes[route_index];
            route = {SensorKind::kBeam,
                     static_cast<std::uint8_t>(channel),
                     static_cast<gpio_num_t>(
                         smartgear::config::kBeamGpioPins[channel])};
            ESP_ERROR_CHECK(gpio_set_direction(route.pin, GPIO_MODE_INPUT));
            ESP_ERROR_CHECK(gpio_set_pull_mode(route.pin, GPIO_PULLUP_ONLY));
            ESP_ERROR_CHECK(gpio_set_intr_type(route.pin, GPIO_INTR_ANYEDGE));
            ESP_ERROR_CHECK(gpio_isr_handler_add(route.pin, sensor_isr, &route));
        }
    }
    for (std::size_t channel = 0; channel < smartgear::config::kPiezoCount;
         ++channel, ++route_index) {
        auto& route = s_routes[route_index];
        route = {SensorKind::kPiezo,
                 static_cast<std::uint8_t>(channel),
                     static_cast<gpio_num_t>(
                         smartgear::config::kPiezoComparatorGpioPins[channel])};
        ESP_ERROR_CHECK(gpio_set_direction(route.pin, GPIO_MODE_INPUT));
        ESP_ERROR_CHECK(gpio_set_pull_mode(route.pin, GPIO_FLOATING));
        ESP_ERROR_CHECK(gpio_set_intr_type(route.pin, GPIO_INTR_POSEDGE));
        ESP_ERROR_CHECK(gpio_isr_handler_add(route.pin, sensor_isr, &route));
    }
}

void log_and_cache_event(const smartgear::NetEvent& event,
                         smartgear::NetEventDelivery& delivery) {
    const std::string json = smartgear::net_event_to_json(event);
    ESP_LOGI(kTag, "%s", json.c_str());
    const auto feedback = smartgear::feedback_for(event.state);
    ESP_LOGI(kTag,
             "feedback=%s led=%d%d%d buzzer=%ums x%u",
             smartgear::feedback_pattern_name(feedback.pattern),
             feedback.led_red,
             feedback.led_green,
             feedback.led_blue,
             feedback.buzzer_on_ms,
             feedback.repeat_count);

    // SmartPaddle WebSocket 的连接回调调用 delivery.set_transport(true, send_fn,
    // context)，断链期间 NetEventDelivery 会保留事件并在恢复时按序补发。
    delivery.publish(event);
}

bool send_board_event(const char* json, void* /*context*/) {
    return smartgear_board_transport_send_json(json);
}

void sync_transport(smartgear::NetEventDelivery& delivery) {
    const bool connected = smartgear_board_transport_connected();
    if (connected == delivery.connected()) {
        return;
    }
    delivery.set_transport(connected, connected ? send_board_event : nullptr);
}

void sync_sensor_health(smartgear::NetEventAggregator& aggregator) {
    // The raw beam mapping is still a provisional active-low candidate. Do
    // not let a board adapter accidentally authorize height events before the
    // purchased SKU, NPN NO/NC polarity, isolator path and a real channel
    // self-test have frozen that mapping and this firmware is rebuilt.
    if (!smartgear::config::kBeamPolarityConfirmed) {
        smartgear::apply_sensor_health_unavailable(aggregator);
        return;
    }

    char calibration_id[64] = {};
    std::uint16_t healthy_beam_mask = 0;
    bool beam_health_valid = false;
    bool piezo_baseline_valid = false;
    bool calibration_valid = false;
    if (!smartgear_board_read_sensor_health(
            calibration_id, sizeof(calibration_id), &healthy_beam_mask,
            &beam_health_valid, &piezo_baseline_valid, &calibration_valid)) {
        smartgear::apply_sensor_health_unavailable(aggregator);
        return;
    }
    const smartgear::SensorHealthSnapshot snapshot{
        healthy_beam_mask,
        beam_health_valid,
        piezo_baseline_valid,
        calibration_valid,
    };
    smartgear::apply_sensor_health_snapshot(
        aggregator, calibration_id, sizeof(calibration_id), snapshot);
}

}  // namespace

extern "C" void app_main() {
    using namespace smartgear;

    BeamCapture beam_capture(config::kBeamQuietUs, config::kBeamMaxEventUs);
    PiezoCapture piezo_capture(config::kTouchMergeUs,
                               config::kPiezoWaveformTimeoutUs);
    PiezoWaveformCapture waveform_capture({config::kPiezoSampleRateHz,
                                           config::kPiezoPreTriggerMs,
                                           config::kPiezoPostTriggerMs});
    PiezoWaveformArchive waveform_archive(config::kWaveformArchiveCapacity);
    PiezoAdcContinuous adc_continuous;
    NetEventAggregator aggregator({config::kTouchAssociationBeforeUs,
                                   config::kTouchAssociationAfterUs,
                                   config::kTouchOnlyTimeoutUs,
                                   config::kTouchCompletionGraceUs});
    NetEventDelivery delivery;
    M6CarrierBeamAdapter carrier_adapter(
        beam_capture, carrier_config::kCarrierToHostOffsetUs);
#ifdef ESP_PLATFORM
    FeedbackGpio feedback_gpio({
        static_cast<gpio_num_t>(config::kFeedbackLedRedGpio),
        static_cast<gpio_num_t>(config::kFeedbackLedGreenGpio),
        static_cast<gpio_num_t>(config::kFeedbackLedBlueGpio),
        static_cast<gpio_num_t>(config::kFeedbackBuzzerGpio),
    });
    M6CarrierSpiMaster carrier_spi({
        SPI2_HOST,
        static_cast<gpio_num_t>(carrier_config::kSpiSckGpio),
        static_cast<gpio_num_t>(carrier_config::kSpiMosiGpio),
        static_cast<gpio_num_t>(carrier_config::kSpiMisoGpio),
        static_cast<gpio_num_t>(carrier_config::kSpiCsGpio),
        static_cast<gpio_num_t>(carrier_config::kIrqGpio),
        static_cast<gpio_num_t>(carrier_config::kResetGpio),
        carrier_config::kSpiClockHz,
    });
    bool carrier_ready = false;
    M6CarrierClockCalibration carrier_clock_calibration;
    bool carrier_clock_ready = carrier_config::kCarrierClockOffsetConfirmed;
    if (carrier_clock_ready) {
        // This path is reserved for a separately recorded, board-specific
        // calibration constant. The default remains false; runtime samples
        // below are the normal way to establish the offset.
        carrier_adapter.set_clock_offset(
            carrier_config::kCarrierToHostOffsetUs);
    }
#endif

    // 启动自检完成并使用机械参考件确认 10 路 M6 光电通道前，事件统一标记 unknown。
    // 校准成功后由设备状态层调用：
    //   aggregator.set_calibration("cal-<version>", true);
    aggregator.set_calibration("boot-self-test-pending", false);
    aggregator.set_beam_health(0, false);
    aggregator.set_piezo_baseline(false);
    configure_sensor_inputs(carrier_config::kUseM6Carrier);
#ifdef ESP_PLATFORM
    if (carrier_config::kUseM6Carrier) {
        const auto carrier_error = carrier_spi.init();
        if (carrier_error == ESP_OK) {
            carrier_ready = true;
        } else {
            ESP_LOGW(kTag, "M6 carrier SPI init deferred: %s",
                     esp_err_to_name(carrier_error));
        }
    }
#endif
    sync_transport(delivery);
    sync_sensor_health(aggregator);
#ifdef ESP_PLATFORM
    const auto feedback_error = feedback_gpio.init();
    if (feedback_error != ESP_OK) {
        ESP_LOGW(kTag, "feedback GPIO init deferred: %s",
                 esp_err_to_name(feedback_error));
    }
#endif
    const auto adc_error = adc_continuous.init(
        {config::kPiezoAdcGpioPins, config::kPiezoSampleRateHz, 256, 2048},
        on_piezo_adc_sample,
        &waveform_capture);
    if (adc_error == ESP_OK) {
        ESP_ERROR_CHECK(adc_continuous.start());
    } else {
        ESP_LOGW(kTag, "ADC1 continuous init deferred: %s", esp_err_to_name(adc_error));
    }
    ESP_LOGI(kTag, "ESP32-S3 net sensor business layer started");

    SensorEdge edge{};
    std::uint64_t next_health_poll_us = 0;
    std::uint64_t next_clock_sync_poll_us = 0;
    while (true) {
        const std::uint64_t now_us =
            static_cast<std::uint64_t>(esp_timer_get_time());
        if (consume_sensor_queue_overflow()) {
            // Dropped edges invalidate the current boundaries. Discard every
            // edge that was already queued before the overflow as well;
            // otherwise stale pre-overflow edges could be combined with fresh
            // input into a plausible but false event. The aggregator retains
            // the overflow marker so the next emitted boundary is unknown.
            xQueueReset(s_sensor_queue);
            beam_capture.reset();
            piezo_capture.reset();
            waveform_capture.abort();
            aggregator.mark_input_overflow();
            ESP_LOGW(kTag, "sensor GPIO queue overflow; next event is unknown");
        }
#ifdef ESP_PLATFORM
        if (carrier_ready) {
            if (now_us >= next_clock_sync_poll_us) {
                const bool was_clock_ready = carrier_clock_ready;
                M6CarrierClockSyncSample sample{};
                bool sample_available = false;
                SmartgearM6CarrierClockSyncReading reading;
                if (smartgear_board_read_m6_carrier_clock_sync(&reading) &&
                    reading.exchange_verified) {
                    sample = {
                        reading.host_sent_us,
                        reading.host_received_us,
                        reading.carrier_received_us,
                        reading.carrier_sent_us,
                    };
                    sample_available = true;
                }
                if (!sample_available &&
                    carrier_config::kUseCarrierSpiClockSync) {
                    sample_available =
                        carrier_spi.exchange_clock_sync(&sample) == ESP_OK;
                }
                if (sample_available) {
                    const bool accepted =
                        carrier_clock_calibration.add_sample(sample);
                    const bool confirmed =
                        accepted && carrier_clock_calibration.confirm();
                    const auto offset = confirmed
                                             ? carrier_clock_calibration
                                                   .confirmed_offset_us()
                                             : std::nullopt;
                    if (offset.has_value()) {
                        carrier_adapter.set_clock_offset(*offset);
                        carrier_clock_ready = true;
                        ESP_LOGI(
                            kTag,
                            "M6 carrier clock confirmed: offset=%lldus samples=%u best_rtt=%lluus spread=%lluus drift=%lluus",
                            static_cast<long long>(*offset),
                            static_cast<unsigned>(
                                carrier_clock_calibration.sample_count()),
                            static_cast<unsigned long long>(
                                carrier_clock_calibration.best_round_trip_us()),
                            static_cast<unsigned long long>(
                                carrier_clock_calibration.offset_spread_us()),
                            static_cast<unsigned long long>(
                                carrier_clock_calibration
                                    .inter_sample_drift_us()));
                    } else {
                        carrier_clock_ready = false;
                    }
                }
                if (was_clock_ready && !carrier_clock_ready) {
                    carrier_adapter.reset_sequence();
                    beam_capture.reset();
                    aggregator.mark_input_overflow();
                    ESP_LOGW(kTag,
                             "M6 carrier clock calibration lost; events remain unknown");
                }
                next_clock_sync_poll_us = now_us + 1'000'000ULL;
            }
            M6CarrierFrame carrier_frame{};
            const auto carrier_result = carrier_spi.poll(&carrier_frame);
            if (carrier_result == M6CarrierSpiPollResult::kFrame) {
                if (!carrier_clock_ready) {
                    // A carrier timestamp cannot be compared with esp_timer
                    // until the runtime estimator has confirmed a real sync
                    // exchange. Keep collecting neither a plausible event
                    // nor a stale BeamCapture boundary in that state.
                    carrier_adapter.reset_sequence();
                    beam_capture.reset();
                    aggregator.mark_input_overflow();
                } else {
                    const auto adapted = carrier_adapter.ingest(carrier_frame);
                    if (!adapted.input_boundary_valid) {
                        carrier_adapter.reset_sequence();
                        aggregator.mark_input_overflow();
                    } else {
                        for (std::size_t index = 0;
                             index < adapted.observation_count; ++index) {
                            aggregator.on_beam(remap_configured_beam_observation(
                                adapted.observations[index]));
                        }
                    }
                }
            } else if (carrier_result == M6CarrierSpiPollResult::kBoundaryError ||
                       carrier_result == M6CarrierSpiPollResult::kSpiError) {
                carrier_adapter.reset_sequence();
                beam_capture.reset();
                aggregator.mark_input_overflow();
            }
        }
#endif
        sync_transport(delivery);
        if (now_us >= next_health_poll_us) {
            sync_sensor_health(aggregator);
            next_health_poll_us = now_us + 1'000'000ULL;
        }

        // Consume comparator/beam edges before dispatching the next ADC DMA
        // batch. A comparator edge and its ADC samples can arrive in the same
        // scheduler slice; starting the frame first lets the timestamped DMA
        // backlog backfill the pre-trigger tail instead of completing an
        // unassociated frame before PiezoCapture sees the trigger.
        if (xQueueReceive(s_sensor_queue, &edge, pdMS_TO_TICKS(1)) == pdTRUE) {
            std::size_t processed_edges = 0;
            do {
                if (edge.kind == SensorKind::kBeam) {
                    const bool blocked =
                        config::beam_blocked_at_level(
                            config::kBeamInputPolarity, edge.level);
                    if (auto observation = beam_capture.on_edge(
                            edge.channel, blocked, edge.timestamp_us)) {
                        aggregator.on_beam(
                            remap_configured_beam_observation(*observation));
                    }
                } else if (edge.level == config::kPiezoTriggeredLevel) {
                    char waveform_reference[48] = {};
                    std::snprintf(
                        waveform_reference,
                        sizeof(waveform_reference),
                        "wave-%llu",
                        static_cast<unsigned long long>(edge.timestamp_us));
                    const bool new_piezo_observation =
                        piezo_capture.will_start_new_observation(edge.timestamp_us);
                    const bool waveform_started =
                        new_piezo_observation && adc_continuous.initialized() &&
                        waveform_capture.start_capture(edge.timestamp_us,
                                                       waveform_reference);
                    std::string effective_waveform_reference;
                    if (waveform_started) {
                        effective_waveform_reference = waveform_reference;
                    } else {
                        effective_waveform_reference =
                            waveform_capture.active_reference();
                    }

                    // 没有可用波形帧时保留空引用；PiezoCapture 会继续保留
                    // 这个比较器候选，但因为没有完整波形而最终 fail-closed。
                    // 不使用固定的 "wave-unavailable" 占位字符串，避免多个
                    // 无波形事件看起来像引用了同一份可回放帧。

                    // comparator 只给低延迟时间点；peak/energy 和 waveform_ref 的
                    // 完整内容由 ADC1 continuous 解析任务补入。这里保留业务接口，
                    // 以便直接接既有 SmartPaddle 的 ADC/时间戳采集模式。
                    if (auto observation = piezo_capture.on_trigger(
                            edge.channel, edge.timestamp_us, 0.0F, 0.0F,
                            effective_waveform_reference)) {
                        aggregator.on_touch(*observation);
                    }
                }
                ++processed_edges;
            } while (processed_edges < 32 &&
                     xQueueReceive(s_sensor_queue, &edge, 0) == pdTRUE);
        }

        if (adc_continuous.initialized()) {
            const esp_err_t adc_read_error = adc_continuous.read_and_dispatch(0);
            if (adc_read_error != ESP_OK && adc_read_error != ESP_ERR_TIMEOUT) {
                ESP_LOGW(kTag, "ADC1 continuous read: %s",
                         esp_err_to_name(adc_read_error));
            }
        }
        waveform_capture.expire(static_cast<std::uint64_t>(esp_timer_get_time()));
        while (auto frame = waveform_capture.take_ready()) {
            const auto features =
                extract_piezo_features(*frame, config::kPiezoSampleRateHz);
            const std::string reference = frame->reference;
            smartgear_board_on_piezo_waveform(
                frame->reference.c_str(), frame->trigger_us,
                frame->pre_trigger_samples, frame->samples[0].data(),
                frame->samples[0].size(), frame->samples[1].data(),
                frame->samples[1].size(), frame->complete);
            waveform_archive.store(std::move(*frame));
            piezo_capture.on_waveform_ready(reference, features);
        }

        if (auto observation = beam_capture.poll(now_us)) {
            aggregator.on_beam(
                remap_configured_beam_observation(*observation));
        }
        if (auto observation = piezo_capture.poll(now_us)) {
            aggregator.on_touch(*observation);
        }
        aggregator.poll(now_us);

        NetEvent event;
        while (aggregator.pop_event(event)) {
#ifdef ESP_PLATFORM
            feedback_gpio.start(feedback_for(event.state), now_us);
#endif
            log_and_cache_event(event, delivery);
        }
#ifdef ESP_PLATFORM
        feedback_gpio.tick(now_us);
#endif
    }
}

#else

int main() { return 0; }

#endif
