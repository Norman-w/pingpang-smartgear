#pragma once

#include <cstddef>
#include <deque>
#include <string>

#include "piezo_waveform.h"

namespace smartgear {

// 保留最近若干个完整波形，供事件后的调试、回放和 SmartPaddle 适配层读取。
// 这是有界 RAM 归档，不承诺断电保存。
class PiezoWaveformArchive {
  public:
    explicit PiezoWaveformArchive(std::size_t capacity = 4)
        : capacity_(capacity) {}

    void store(PiezoWaveformFrame frame);
    const PiezoWaveformFrame* find(const std::string& reference) const;

    bool contains(const std::string& reference) const {
        return find(reference) != nullptr;
    }
    std::size_t size() const { return frames_.size(); }
    std::size_t dropped_count() const { return dropped_count_; }

  private:
    std::size_t capacity_;
    std::deque<PiezoWaveformFrame> frames_;
    std::size_t dropped_count_ = 0;
};

}  // namespace smartgear
