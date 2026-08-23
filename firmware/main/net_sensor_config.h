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

// 比较器电平约定：光束被遮挡时为低，PVDF 比较器触发时为高。
constexpr int kBeamBlockedLevel = 0;
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
