#include "piezo_waveform_archive.h"

#include <utility>

namespace smartgear {

void PiezoWaveformArchive::store(PiezoWaveformFrame frame) {
    for (auto& existing : frames_) {
        if (existing.reference == frame.reference) {
            existing = std::move(frame);
            return;
        }
    }

    if (capacity_ == 0) {
        ++dropped_count_;
        return;
    }
    if (frames_.size() >= capacity_) {
        frames_.pop_front();
        ++dropped_count_;
    }
    frames_.push_back(std::move(frame));
}

const PiezoWaveformFrame* PiezoWaveformArchive::find(
    const std::string& reference) const {
    for (const auto& frame : frames_) {
        if (frame.reference == reference) {
            return &frame;
        }
    }
    return nullptr;
}

}  // namespace smartgear
