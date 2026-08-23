#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace smartgear::config {

constexpr std::size_t kBeamCount = 10;
constexpr std::size_t kPiezoCount = 2;

// 首轮占位引脚映射。最终值必须和 PCB、SmartPaddle 既有约束及启动脚复核后冻结。
constexpr std::array<int, kBeamCount> kBeamGpioPins = {
    4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
constexpr std::array<int, kPiezoCount> kPiezoComparatorGpioPins = {14, 15};
constexpr std::array<int, kPiezoCount> kPiezoAdcGpioPins = {1, 2};
constexpr int kFeedbackLedRedGpio = 16;
constexpr int kFeedbackLedGreenGpio = 17;
constexpr int kFeedbackLedBlueGpio = 18;
constexpr int kFeedbackBuzzerGpio = 19;

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
