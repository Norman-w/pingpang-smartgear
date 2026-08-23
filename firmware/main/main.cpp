#include "beam_capture.h"
#include "feedback.h"
#include "feedback_gpio.h"
#include "net_event_aggregator.h"
#include "net_event_delivery.h"
#include "net_sensor_config.h"
#include "piezo_capture.h"
#include "piezo_adc_continuous.h"
#include "piezo_waveform.h"
#include "piezo_waveform_archive.h"

#ifdef ESP_PLATFORM

#include <array>
#include <cstdio>
#include <string>
#include <utility>

#include "driver/gpio.h"
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
std::array<SensorRoute, smartgear::config::kBeamCount +
                            smartgear::config::kPiezoCount>
    s_routes{};

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
        xQueueSendFromISR(s_sensor_queue, &edge, &higher_priority_task_woken);
    }
    if (higher_priority_task_woken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
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

void configure_sensor_inputs() {
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
    for (std::size_t channel = 0; channel < smartgear::config::kBeamCount;
         ++channel, ++route_index) {
        auto& route = s_routes[route_index];
        route = {SensorKind::kBeam,
                 static_cast<std::uint8_t>(channel),
                 static_cast<gpio_num_t>(smartgear::config::kBeamGpioPins[channel])};
        gpio_set_direction(route.pin, GPIO_MODE_INPUT);
        gpio_set_pull_mode(route.pin, GPIO_PULLUP_ONLY);
        gpio_set_intr_type(route.pin, GPIO_INTR_ANYEDGE);
        ESP_ERROR_CHECK(gpio_isr_handler_add(route.pin, sensor_isr, &route));
    }
    for (std::size_t channel = 0; channel < smartgear::config::kPiezoCount;
         ++channel, ++route_index) {
        auto& route = s_routes[route_index];
        route = {SensorKind::kPiezo,
                 static_cast<std::uint8_t>(channel),
                 static_cast<gpio_num_t>(
                     smartgear::config::kPiezoComparatorGpioPins[channel])};
        gpio_set_direction(route.pin, GPIO_MODE_INPUT);
        gpio_set_pull_mode(route.pin, GPIO_FLOATING);
        gpio_set_intr_type(route.pin, GPIO_INTR_POSEDGE);
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
#ifdef ESP_PLATFORM
    FeedbackGpio feedback_gpio({
        static_cast<gpio_num_t>(config::kFeedbackLedRedGpio),
        static_cast<gpio_num_t>(config::kFeedbackLedGreenGpio),
        static_cast<gpio_num_t>(config::kFeedbackLedBlueGpio),
        static_cast<gpio_num_t>(config::kFeedbackBuzzerGpio),
    });
#endif

    // 启动自检完成并使用机械参考件确认 10 路光栅前，事件统一标记 unknown。
    // 校准成功后由设备状态层调用：
    //   aggregator.set_calibration("cal-<version>", true);
    aggregator.set_calibration("boot-self-test-pending", false);
    aggregator.set_beam_health(0, false);
    aggregator.set_piezo_baseline(false);
    configure_sensor_inputs();
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
    while (true) {
        const std::uint64_t now_us =
            static_cast<std::uint64_t>(esp_timer_get_time());
        if (adc_continuous.initialized()) {
            const esp_err_t adc_read_error = adc_continuous.read_and_dispatch(0);
            if (adc_read_error != ESP_OK && adc_read_error != ESP_ERR_TIMEOUT) {
                ESP_LOGW(kTag, "ADC1 continuous read: %s",
                         esp_err_to_name(adc_read_error));
            }
        }
        while (auto frame = waveform_capture.take_ready()) {
            const auto features =
                extract_piezo_features(*frame, config::kPiezoSampleRateHz);
            const std::string reference = frame->reference;
            waveform_archive.store(std::move(*frame));
            piezo_capture.on_waveform_ready(reference, features);
        }
        if (xQueueReceive(s_sensor_queue, &edge, pdMS_TO_TICKS(1)) == pdTRUE) {
            std::size_t processed_edges = 0;
            do {
                if (edge.kind == SensorKind::kBeam) {
                    const bool blocked =
                        edge.level == config::kBeamBlockedLevel;
                    if (auto observation = beam_capture.on_edge(
                            edge.channel, blocked, edge.timestamp_us)) {
                        aggregator.on_beam(*observation);
                    }
                } else if (edge.level == config::kPiezoTriggeredLevel) {
                    char waveform_reference[48] = {};
                    std::snprintf(
                        waveform_reference,
                        sizeof(waveform_reference),
                        "wave-%llu",
                        static_cast<unsigned long long>(edge.timestamp_us));
                    const bool waveform_started =
                        adc_continuous.initialized() &&
                        waveform_capture.start_capture(edge.timestamp_us,
                                                       waveform_reference);
                    std::string effective_waveform_reference;
                    if (waveform_started) {
                        effective_waveform_reference = waveform_reference;
                    } else {
                        effective_waveform_reference =
                            waveform_capture.active_reference();
                    }
                    if (effective_waveform_reference.empty()) {
                        // 没有可用波形帧时也必须走“未完成”路径，不能把比较器
                        // 时间点和零特征误报成已完成的波形证据。
                        effective_waveform_reference = "wave-unavailable";
                    }

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

        if (auto observation = beam_capture.poll(now_us)) {
            aggregator.on_beam(*observation);
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
