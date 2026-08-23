#pragma once

#ifdef ESP_PLATFORM

#include <array>
#include <cstddef>
#include <cstdint>

#include "esp_adc/adc_continuous.h"
#include "esp_err.h"

namespace smartgear {

struct PiezoAdcContinuousConfig {
    std::array<int, 2> gpio = {1, 2};
    std::uint32_t sample_rate_hz = 16'000;
    std::size_t conversion_frame_bytes = 256;
    std::size_t max_store_buffer_bytes = 2048;
};

using PiezoAdcSampleSink = void (*)(std::uint8_t channel,
                                    std::int16_t raw_sample,
                                    std::uint64_t timestamp_us,
                                    void* context);

// ESP-IDF ADC1 continuous/DMA 的薄适配器。sample_rate_hz 表示每个 PVDF
// 通道的有效采样率；底层扫描总频率会乘以通道数。它只负责把有效样本送到
// PiezoWaveformCapture，峰值/能量仍由业务层按窗口计算。
class PiezoAdcContinuous {
  public:
    static constexpr std::size_t kReadBufferCapacityBytes = 256;

    ~PiezoAdcContinuous();

    esp_err_t init(const PiezoAdcContinuousConfig& config,
                   PiezoAdcSampleSink sink,
                   void* context);
    esp_err_t start();
    esp_err_t read_and_dispatch(std::uint32_t timeout_ms);
    esp_err_t stop();
    esp_err_t deinit();

    bool initialized() const { return handle_ != nullptr; }

  private:
    int channel_index(adc_channel_t channel) const;

    adc_continuous_handle_t handle_ = nullptr;
    std::array<adc_channel_t, 2> channels_{};
    std::uint32_t conversion_rate_hz_ = 32'000;
    std::size_t conversion_frame_bytes_ = 0;
    PiezoAdcSampleSink sink_ = nullptr;
    void* context_ = nullptr;
    bool started_ = false;
};

}  // namespace smartgear

#endif  // ESP_PLATFORM
