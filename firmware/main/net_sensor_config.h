#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace smartgear::config {

constexpr std::size_t kBeamCount = 10;
constexpr std::size_t kPiezoCount = 2;
constexpr std::uint16_t kAllBeamMask = static_cast<std::uint16_t>(
    (1U << kBeamCount) - 1U);

// 首轮占位引脚映射。最终值必须和 PCB、SmartPaddle 既有约束及启动脚复核后冻结。
constexpr std::array<int, kBeamCount> kBeamGpioPins = {
    4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
constexpr std::array<int, kPiezoCount> kPiezoComparatorGpioPins = {14, 15};
constexpr std::array<int, kPiezoCount> kPiezoAdcGpioPins = {1, 2};
constexpr int kFeedbackLedRedGpio = 16;
constexpr int kFeedbackLedGreenGpio = 17;
constexpr int kFeedbackLedBlueGpio = 18;
constexpr int kFeedbackBuzzerGpio = 19;
constexpr std::array<int, 4> kFeedbackGpioPins = {
    kFeedbackLedRedGpio,
    kFeedbackLedGreenGpio,
    kFeedbackLedBlueGpio,
    kFeedbackBuzzerGpio,
};

template <std::size_t Size>
constexpr bool all_gpio_numbers_valid(const std::array<int, Size>& pins) {
    for (const int pin : pins) {
        // ESP32-S3 exposes GPIO numbers 0..48. This is only a range check;
        // strapping, USB and board-specific reservations still belong to the
        // final PCB review.
        if (pin < 0 || pin > 48) {
            return false;
        }
    }
    return true;
}

template <std::size_t Size>
constexpr bool all_unique(const std::array<int, Size>& pins) {
    for (std::size_t left = 0; left < Size; ++left) {
        for (std::size_t right = left + 1; right < Size; ++right) {
            if (pins[left] == pins[right]) {
                return false;
            }
        }
    }
    return true;
}

template <std::size_t LeftSize, std::size_t RightSize>
constexpr bool disjoint(const std::array<int, LeftSize>& left,
                        const std::array<int, RightSize>& right) {
    for (const int left_pin : left) {
        for (const int right_pin : right) {
            if (left_pin == right_pin) {
                return false;
            }
        }
    }
    return true;
}

static_assert(all_gpio_numbers_valid(kBeamGpioPins),
              "beam GPIO mapping contains an invalid ESP32-S3 GPIO number");
static_assert(all_gpio_numbers_valid(kPiezoComparatorGpioPins),
              "PVDF comparator mapping contains an invalid GPIO number");
static_assert(all_gpio_numbers_valid(kPiezoAdcGpioPins),
              "PVDF ADC mapping contains an invalid GPIO number");
static_assert(all_gpio_numbers_valid(kFeedbackGpioPins),
              "feedback mapping contains an invalid GPIO number");
static_assert(all_unique(kBeamGpioPins), "beam GPIO mapping contains duplicates");
static_assert(all_unique(kPiezoComparatorGpioPins),
              "PVDF comparator mapping contains duplicates");
static_assert(all_unique(kPiezoAdcGpioPins),
              "PVDF ADC mapping contains duplicates");
static_assert(all_unique(kFeedbackGpioPins),
              "feedback mapping contains duplicates");
static_assert(disjoint(kBeamGpioPins, kPiezoComparatorGpioPins) &&
                  disjoint(kBeamGpioPins, kPiezoAdcGpioPins) &&
                  disjoint(kBeamGpioPins, kFeedbackGpioPins) &&
                  disjoint(kPiezoComparatorGpioPins, kPiezoAdcGpioPins) &&
                  disjoint(kPiezoComparatorGpioPins, kFeedbackGpioPins) &&
                  disjoint(kPiezoAdcGpioPins, kFeedbackGpioPins),
              "sensor and feedback GPIO mappings must be disjoint");

// Physical MCU input bit -> logical height index.  The acceptance channel map
// records this same relationship as output_bit for each +10..+100 mm row.  It
// is identity for the provisional harness; if the delivered cable/PCB order
// differs, change this permutation after evidence is captured and rebuild.
constexpr std::array<std::uint8_t, kBeamCount> kBeamLogicalIndexByInput = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

template <std::size_t Size>
constexpr bool is_permutation_0_to_n_minus_1(
    const std::array<std::uint8_t, Size>& values) {
    for (std::size_t left = 0; left < Size; ++left) {
        if (values[left] >= Size) {
            return false;
        }
        for (std::size_t right = left + 1; right < Size; ++right) {
            if (values[left] == values[right]) {
                return false;
            }
        }
    }
    return true;
}

static_assert(is_permutation_0_to_n_minus_1(kBeamLogicalIndexByInput),
              "beam input-to-height mapping must be a 0..9 permutation");

// M6 传感器的最终常开/常闭后缀和隔离前端极性仍待卖家/实物确认。
// 先把当前参考拓扑的“遮挡为低”保存为可审计的候选配置，但在证据
// 到位并重新编译前，main.cpp 不允许健康快照授权有效高度事件。
enum class BeamInputPolarity : std::uint8_t {
    kBlockedLow,
    kBlockedHigh,
};

constexpr BeamInputPolarity kBeamInputPolarity =
    BeamInputPolarity::kBlockedLow;
constexpr bool kBeamPolarityConfirmed = false;

constexpr int beam_blocked_level_for(const BeamInputPolarity polarity) {
    return polarity == BeamInputPolarity::kBlockedLow ? 0 : 1;
}

constexpr bool beam_blocked_at_level(const BeamInputPolarity polarity,
                                     const int level) {
    return level == beam_blocked_level_for(polarity);
}

constexpr int kBeamBlockedLevel = beam_blocked_level_for(kBeamInputPolarity);
// PVDF 比较器触发仍按上升沿处理。
constexpr int kPiezoTriggeredLevel = 1;

constexpr int kBeamFirstHeightMm = 10;
constexpr int kBeamPitchMm = 10;
constexpr int kBeamLastHeightMm =
    kBeamFirstHeightMm + static_cast<int>(kBeamCount - 1) * kBeamPitchMm;

constexpr std::uint32_t kPiezoSampleRateHz = 16'000;
constexpr std::uint32_t kPiezoPreTriggerMs = 20;
constexpr std::uint32_t kPiezoPostTriggerMs = 80;
constexpr std::size_t kPiezoPreTriggerSamples =
    kPiezoSampleRateHz * kPiezoPreTriggerMs / 1'000;
constexpr std::size_t kPiezoPostTriggerSamples =
    kPiezoSampleRateHz * kPiezoPostTriggerMs / 1'000;

// 光束全部恢复后用于结束一次事件的安静窗口；它不是 M6 传感器的
// 响应时间，也不是要求物体连续遮挡的最小脉宽。M6 的 5 ms 响应和
// 最小输入/输出脉宽必须按 docs/m6-response-time-validation-v0.1.zh-CN.md
// 用实物波形确认。
constexpr std::uint64_t kBeamQuietUs = 5'000;
constexpr std::uint64_t kBeamMaxEventUs = 250'000;
constexpr std::uint64_t kTouchMergeUs = 5'000;
constexpr std::uint64_t kTouchAssociationBeforeUs = 20'000;
// 关联窗口覆盖 20 ms 预触发 + 80 ms 后触发，并留出 ADC/DMA 调度裕量。
constexpr std::uint64_t kTouchAssociationAfterUs = 120'000;
constexpr std::uint64_t kTouchOnlyTimeoutUs = 140'000;
constexpr std::uint64_t kPiezoWaveformTimeoutUs = 120'000;
// 光栅待决边界还要覆盖 PVDF 最坏波形超时和最后一次归并间隔，避免
// 关联窗口末端的擦网候选因异步 ADC 完成而先被判为 clean_over。
constexpr std::uint64_t kTouchCompletionGraceUs =
    kPiezoWaveformTimeoutUs + kTouchMergeUs;
constexpr std::size_t kWaveformArchiveCapacity = 4;

constexpr std::size_t kEventCacheCapacity = 16;

}  // namespace smartgear::config
