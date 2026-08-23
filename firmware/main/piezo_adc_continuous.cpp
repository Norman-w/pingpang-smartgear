#ifdef ESP_PLATFORM

#include "piezo_adc_continuous.h"

#include <array>

#include "esp_idf_version.h"
#include "esp_timer.h"
#include "soc/soc_caps.h"

namespace smartgear {

PiezoAdcContinuous::~PiezoAdcContinuous() {
    deinit();
}

esp_err_t PiezoAdcContinuous::init(const PiezoAdcContinuousConfig& config,
                                   PiezoAdcSampleSink sink,
                                   void* context) {
    if (handle_ != nullptr || sink == nullptr || config.sample_rate_hz == 0) {
        return ESP_ERR_INVALID_STATE;
    }

    adc_continuous_handle_cfg_t handle_config{};
    handle_config.max_store_buf_size = config.max_store_buffer_bytes;
    handle_config.conv_frame_size = config.conversion_frame_bytes;
    esp_err_t error = adc_continuous_new_handle(&handle_config, &handle_);
    if (error != ESP_OK) {
        handle_ = nullptr;
        return error;
    }

    std::array<adc_digi_pattern_config_t, 2> patterns{};
    for (std::size_t index = 0; index < config.gpio.size(); ++index) {
        adc_unit_t unit = ADC_UNIT_1;
        adc_channel_t channel = ADC_CHANNEL_0;
        error = adc_continuous_io_to_channel(config.gpio[index], &unit, &channel);
        if (error != ESP_OK || unit != ADC_UNIT_1) {
            deinit();
            return error == ESP_OK ? ESP_ERR_INVALID_ARG : error;
        }
        channels_[index] = channel;
        patterns[index].atten = ADC_ATTEN_DB_12;
        patterns[index].channel = channel;
        patterns[index].unit = unit;
        patterns[index].bit_width = ADC_BITWIDTH_12;
    }

    adc_continuous_config_t adc_config{};
    adc_config.pattern_num = patterns.size();
    adc_config.adc_pattern = patterns.data();
    adc_config.sample_freq_hz = config.sample_rate_hz;
    adc_config.conv_mode = ADC_CONV_SINGLE_UNIT_1;
    adc_config.format = ADC_DIGI_OUTPUT_FORMAT_TYPE2;
    error = adc_continuous_config(handle_, &adc_config);
    if (error != ESP_OK) {
        deinit();
        return error;
    }

    sample_rate_hz_ = config.sample_rate_hz;
    sink_ = sink;
    context_ = context;
    return ESP_OK;
}

esp_err_t PiezoAdcContinuous::start() {
    if (handle_ == nullptr) {
        return ESP_ERR_INVALID_STATE;
    }
    const esp_err_t error = adc_continuous_start(handle_);
    if (error == ESP_OK) {
        started_ = true;
    }
    return error;
}

esp_err_t PiezoAdcContinuous::read_and_dispatch(const std::uint32_t timeout_ms) {
    if (handle_ == nullptr || !started_) {
        return ESP_ERR_INVALID_STATE;
    }

    std::array<std::uint8_t, 256> raw_buffer{};
    std::uint32_t bytes_read = 0;
    esp_err_t error = adc_continuous_read(handle_,
                                          raw_buffer.data(),
                                          raw_buffer.size(),
                                          &bytes_read,
                                          timeout_ms);
    if (error != ESP_OK) {
        return error;
    }

    const std::uint64_t frame_end_us =
        static_cast<std::uint64_t>(esp_timer_get_time());

#if ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(6, 0, 0)
    std::array<adc_continuous_data_t, 64> parsed{};
    std::uint32_t sample_count = 0;
    error = adc_continuous_parse_data(handle_,
                                      raw_buffer.data(),
                                      bytes_read,
                                      parsed.data(),
                                      &sample_count);
    if (error != ESP_OK) {
        return error;
    }
    for (std::uint32_t index = 0; index < sample_count; ++index) {
        if (!parsed[index].valid || parsed[index].unit != ADC_UNIT_1) {
            continue;
        }
        const int business_channel = channel_index(parsed[index].channel);
        if (business_channel < 0 || sink_ == nullptr) {
            continue;
        }
        const std::uint64_t sample_age_us =
            static_cast<std::uint64_t>(sample_count - 1U - index) * 1'000'000ULL /
            sample_rate_hz_;
        const std::uint64_t timestamp_us =
            frame_end_us >= sample_age_us ? frame_end_us - sample_age_us
                                          : frame_end_us;
        sink_(static_cast<std::uint8_t>(business_channel),
              static_cast<std::int16_t>(parsed[index].raw_data),
              timestamp_us,
              context_);
    }
#else
    // SmartPaddle 当前使用 ESP-IDF 5.5.x；该版本返回 adc_digi_output_data_t，
    // 而 ESP-IDF 6.x 提供 adc_continuous_parse_data()。两者都保持同一业务
    // sink，避免因为基础工程版本差异改变波形窗口逻辑。
    constexpr std::size_t result_bytes = SOC_ADC_DIGI_RESULT_BYTES;
    if (result_bytes == 0 || bytes_read % result_bytes != 0) {
        return ESP_ERR_INVALID_SIZE;
    }
    const auto* results = reinterpret_cast<const adc_digi_output_data_t*>(
        raw_buffer.data());
    const std::uint32_t sample_count = bytes_read / result_bytes;
    for (std::uint32_t index = 0; index < sample_count; ++index) {
        const auto& result = results[index].type2;
        if (result.unit != ADC_UNIT_1 || sink_ == nullptr) {
            continue;
        }
        const int business_channel =
            channel_index(static_cast<adc_channel_t>(result.channel));
        if (business_channel < 0) {
            continue;
        }
        const std::uint64_t sample_age_us =
            static_cast<std::uint64_t>(sample_count - 1U - index) * 1'000'000ULL /
            sample_rate_hz_;
        const std::uint64_t timestamp_us =
            frame_end_us >= sample_age_us ? frame_end_us - sample_age_us
                                          : frame_end_us;
        sink_(static_cast<std::uint8_t>(business_channel),
              static_cast<std::int16_t>(result.data),
              timestamp_us,
              context_);
    }
#endif
    return ESP_OK;
}

esp_err_t PiezoAdcContinuous::stop() {
    if (handle_ == nullptr || !started_) {
        return ESP_OK;
    }
    const esp_err_t error = adc_continuous_stop(handle_);
    if (error == ESP_OK) {
        started_ = false;
    }
    return error;
}

esp_err_t PiezoAdcContinuous::deinit() {
    if (handle_ == nullptr) {
        return ESP_OK;
    }
    const esp_err_t stop_error = stop();
    if (stop_error != ESP_OK) {
        return stop_error;
    }
    const esp_err_t error = adc_continuous_deinit(handle_);
    if (error == ESP_OK) {
        handle_ = nullptr;
        sink_ = nullptr;
        context_ = nullptr;
    }
    return error;
}

int PiezoAdcContinuous::channel_index(const adc_channel_t channel) const {
    for (std::size_t index = 0; index < channels_.size(); ++index) {
        if (channels_[index] == channel) {
            return static_cast<int>(index);
        }
    }
    return -1;
}

}  // namespace smartgear

#endif  // ESP_PLATFORM
