#include "piezo_waveform.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <utility>

namespace smartgear {

namespace {
constexpr std::size_t kReadyFrameCapacity = 4;
}

PiezoFeatureSummary extract_piezo_features(const PiezoWaveformFrame& frame,
                                           const std::uint32_t sample_rate_hz) {
    PiezoFeatureSummary features;
    features.complete = frame.complete && frame.sample_timestamps_valid;
    if (sample_rate_hz == 0) {
        return features;
    }

    std::size_t max_active_samples = 0;
    for (std::size_t channel = 0; channel < frame.samples.size(); ++channel) {
        const auto& samples = frame.samples[channel];
        if (samples.empty()) {
            continue;
        }
        const std::size_t pre_samples = std::min(
            samples.size(), frame.pre_trigger_samples != 0
                                ? frame.pre_trigger_samples
                                : static_cast<std::size_t>(sample_rate_hz) * 20U /
                                      1'000U);
        const std::size_t recorded_pre = frame.pre_samples_available[channel];
        if (frame.complete && recorded_pre < pre_samples) {
            // A just-booted device may have a complete post-trigger window
            // before its rolling history has filled. Keep the frame for
            // diagnostics, but do not turn zero-filled history into valid
            // baseline evidence.
            features.complete = false;
        }
        const std::size_t available_pre = std::min(pre_samples, recorded_pre);
        const std::size_t baseline_begin = pre_samples - available_pre;
        const float baseline = std::accumulate(
                                  samples.begin() + baseline_begin,
                                  samples.begin() + pre_samples,
                                  0.0F) /
                              static_cast<float>(available_pre == 0 ? 1 : available_pre);

        float peak = 0.0F;
        float energy = 0.0F;
        const std::size_t recorded_post =
            frame.complete && frame.post_samples[channel] == 0
                ? samples.size() - pre_samples
                : frame.post_samples[channel];
        const std::size_t post_samples = std::min(
            recorded_post, samples.size() - pre_samples);
        for (auto sample = samples.begin() + pre_samples;
             sample != samples.begin() + pre_samples + post_samples; ++sample) {
            const float deviation = static_cast<float>(*sample) - baseline;
            const float magnitude = std::fabs(deviation);
            peak = std::max(peak, magnitude);
            energy += deviation * deviation;
        }
        features.peak[channel] = peak;
        features.energy[channel] = energy;

        const float active_threshold = peak * 0.1F;
        std::size_t active_samples = 0;
        std::size_t current_active_samples = 0;
        if (active_threshold > 0.0F) {
            for (std::size_t index = pre_samples;
                 index < pre_samples + post_samples; ++index) {
                if (std::fabs(static_cast<float>(samples[index]) - baseline) >=
                    active_threshold) {
                    ++current_active_samples;
                    active_samples = std::max(active_samples, current_active_samples);
                } else {
                    current_active_samples = 0;
                }
            }
        }
        max_active_samples = std::max(max_active_samples, active_samples);
    }
    features.duration_us = static_cast<std::uint64_t>(max_active_samples) *
                           1'000'000ULL / sample_rate_hz;
    return features;
}

PiezoWaveformCapture::PiezoWaveformCapture(PiezoWaveformConfig config)
    : config_(config) {
    const std::size_t pre_samples = config_.pre_trigger_samples();
    for (std::size_t channel = 0; channel < history_.size(); ++channel) {
        auto& channel_history = history_[channel];
        channel_history.assign(pre_samples, 0);
        history_timestamps_[channel].assign(pre_samples, 0);
    }
}

void PiezoWaveformCapture::feed_sample(const std::uint8_t channel,
                                       const std::int16_t sample,
                                       const std::uint64_t timestamp_us) {
    if (channel >= history_.size() || history_[channel].empty()) {
        return;
    }

    if (!active_) {
        record_history_sample(channel, sample, timestamp_us);
        return;
    }

    if (frame_) {
        if (frame_has_sample_timestamp_[channel] &&
            timestamp_us < frame_last_sample_timestamp_[channel]) {
            // A DMA adapter is expected to dispatch each channel in
            // timestamp order. Preserve the sample for diagnostics, but do
            // not let a reordered stream become valid waveform evidence.
            frame_->sample_timestamps_valid = false;
        }
        frame_last_sample_timestamp_[channel] = timestamp_us;
        frame_has_sample_timestamp_[channel] = true;
    }

    // ADC DMA may deliver samples that were already buffered before the
    // comparator edge. They belong to the pre-trigger history, but may arrive
    // after start_capture() has already snapshotted the rolling buffer. Keep
    // only samples inside the configured pre-trigger time window and backfill
    // the current frame's newest pre-trigger slots; an older DMA backlog is
    // stale input and must not masquerade as evidence from this event.
    if (!frame_ || timestamp_us < frame_->trigger_us) {
        if (frame_ && timestamp_us < frame_->trigger_us) {
            const std::uint64_t age_us = frame_->trigger_us - timestamp_us;
            const std::uint64_t pre_trigger_window_us =
                static_cast<std::uint64_t>(config_.pre_trigger_ms) * 1'000ULL;
            if (age_us <= pre_trigger_window_us) {
                append_late_pre_trigger_sample(channel, sample);
                record_history_sample(channel, sample, timestamp_us);
            } else {
                // An ADC DMA batch may contain an older backlog sample. It
                // is not part of this frame and must not poison the rolling
                // history used by the next frame.
            }
        } else {
            record_history_sample(channel, sample, timestamp_us);
        }
        return;
    }

    const std::uint64_t post_trigger_window_us =
        static_cast<std::uint64_t>(config_.post_trigger_ms) * 1'000ULL;
    if (timestamp_us - frame_->trigger_us > post_trigger_window_us) {
        // Samples arriving after the configured post-trigger window may be
        // useful to the rolling history, but cannot fill this frame.
        record_history_sample(channel, sample, timestamp_us);
        return;
    }

    if (post_written_[channel] >= config_.post_trigger_samples()) {
        record_history_sample(channel, sample, timestamp_us);
        return;
    }
    frame_->samples[channel][config_.pre_trigger_samples() + post_written_[channel]] =
        sample;
    ++post_written_[channel];
    record_history_sample(channel, sample, timestamp_us);
    if (all_post_samples_written()) {
        enqueue_current_frame(true);
    }
}

bool PiezoWaveformCapture::start_capture(const std::uint64_t trigger_us,
                                         const std::string& reference) {
    if (active_ || reference.empty() || config_.pre_trigger_samples() == 0 ||
        config_.post_trigger_samples() == 0) {
        return false;
    }

    frame_ = PiezoWaveformFrame{};
    frame_->reference = reference;
    frame_->trigger_us = trigger_us;
    frame_->pre_trigger_samples = config_.pre_trigger_samples();
    const std::size_t total_samples =
        config_.pre_trigger_samples() + config_.post_trigger_samples();
    for (auto& channel_samples : frame_->samples) {
        channel_samples.assign(total_samples, 0);
    }
    post_written_ = {0, 0};
    frame_last_sample_timestamp_ = {0, 0};
    frame_has_sample_timestamp_ = {false, false};
    snapshot_pre_trigger();
    active_ = true;
    return true;
}

void PiezoWaveformCapture::snapshot_pre_trigger() {
    for (std::size_t channel = 0; channel < history_.size(); ++channel) {
        const auto& channel_history = history_[channel];
        const auto& channel_timestamps = history_timestamps_[channel];
        const std::size_t pre_samples = config_.pre_trigger_samples();
        if (pre_samples == 0 || channel_history.empty()) {
            frame_->pre_samples_available[channel] = 0;
            continue;
        }

        const std::size_t oldest =
            (history_cursor_[channel] + channel_history.size() -
             history_count_[channel]) % channel_history.size();
        std::size_t available = 0;
        for (std::size_t offset = 0; offset < history_count_[channel]; ++offset) {
            const std::size_t chronological_index =
                (oldest + offset) % channel_history.size();
            const std::uint64_t timestamp_us =
                channel_timestamps[chronological_index];
            if (timestamp_us >= frame_->trigger_us ||
                frame_->trigger_us - timestamp_us >
                    static_cast<std::uint64_t>(config_.pre_trigger_ms) * 1'000ULL) {
                continue;
            }
            frame_->samples[channel][available++] =
                channel_history[chronological_index];
        }

        frame_->pre_samples_available[channel] =
            std::min(available, pre_samples);
        const std::size_t missing =
            pre_samples - frame_->pre_samples_available[channel];
        for (std::size_t index = frame_->pre_samples_available[channel]; index > 0;
             --index) {
            frame_->samples[channel][missing + index - 1] =
                frame_->samples[channel][index - 1];
        }
        for (std::size_t index = 0; index < missing; ++index) {
            frame_->samples[channel][index] = 0;
        }
    }
}

bool PiezoWaveformCapture::all_post_samples_written() const {
    const std::size_t target = config_.post_trigger_samples();
    return post_written_[0] >= target && post_written_[1] >= target;
}

std::optional<PiezoWaveformFrame> PiezoWaveformCapture::take_ready() {
    if (ready_frames_.empty()) {
        return std::nullopt;
    }
    auto result = std::move(ready_frames_.front());
    ready_frames_.pop_front();
    return result;
}

bool PiezoWaveformCapture::expire(const std::uint64_t timestamp_us) {
    if (!active_ || !frame_ || timestamp_us < frame_->trigger_us) {
        return false;
    }
    const std::uint64_t post_window_us =
        static_cast<std::uint64_t>(config_.post_trigger_ms) * 1'000ULL;
    if (timestamp_us - frame_->trigger_us < post_window_us) {
        return false;
    }
    enqueue_current_frame(false);
    return true;
}

std::string PiezoWaveformCapture::active_reference() const {
    return frame_ ? frame_->reference : std::string{};
}

void PiezoWaveformCapture::abort() {
    active_ = false;
    frame_.reset();
    post_written_ = {0, 0};
    frame_last_sample_timestamp_ = {0, 0};
    frame_has_sample_timestamp_ = {false, false};
    clear_history();
}

void PiezoWaveformCapture::clear_history() {
    history_cursor_ = {0, 0};
    history_count_ = {0, 0};
    history_last_sample_timestamp_ = {0, 0};
    history_has_timestamp_ = {false, false};
    for (std::size_t channel = 0; channel < history_.size(); ++channel) {
        std::fill(history_[channel].begin(), history_[channel].end(), 0);
        std::fill(history_timestamps_[channel].begin(),
                  history_timestamps_[channel].end(), 0);
    }
}

void PiezoWaveformCapture::enqueue_current_frame(const bool complete) {
    if (!frame_) {
        return;
    }
    const bool history_is_safe = frame_->sample_timestamps_valid;
    frame_->post_samples = post_written_;
    frame_->complete = complete && frame_->sample_timestamps_valid;
    active_ = false;
    if (ready_frames_.size() == kReadyFrameCapacity) {
        ready_frames_.pop_front();
        ++dropped_ready_count_;
    }
    ready_frames_.push_back(std::move(*frame_));
    frame_.reset();
    if (!history_is_safe) {
        // Do not let an out-of-order DMA frame become the pre-trigger history
        // of a later event. The next frame must rebuild history from ordered
        // samples and will remain incomplete until it has enough evidence.
        clear_history();
    }
}

void PiezoWaveformCapture::record_history(const std::uint8_t channel,
                                          const std::int16_t sample,
                                          const std::uint64_t timestamp_us) {
    auto& channel_history = history_[channel];
    const std::size_t cursor = history_cursor_[channel];
    channel_history[cursor] = sample;
    history_timestamps_[channel][cursor] = timestamp_us;
    history_cursor_[channel] =
        (history_cursor_[channel] + 1) % channel_history.size();
    history_count_[channel] = std::min(
        history_count_[channel] + static_cast<std::size_t>(1),
        channel_history.size());
}

void PiezoWaveformCapture::record_history_sample(
    const std::uint8_t channel,
    const std::int16_t sample,
    const std::uint64_t timestamp_us) {
    if (history_has_timestamp_[channel] &&
        timestamp_us < history_last_sample_timestamp_[channel]) {
        // A late DMA sample can arrive after the current frame has already
        // closed. Dropping it here prevents stale data from becoming the
        // pre-trigger baseline of the next event.
        return;
    }
    record_history(channel, sample, timestamp_us);
    history_last_sample_timestamp_[channel] = timestamp_us;
    history_has_timestamp_[channel] = true;
}

void PiezoWaveformCapture::append_late_pre_trigger_sample(
    const std::uint8_t channel,
    const std::int16_t sample) {
    if (!frame_ || channel >= frame_->samples.size()) {
        return;
    }
    const std::size_t pre_samples = config_.pre_trigger_samples();
    if (pre_samples == 0 || frame_->samples[channel].size() < pre_samples) {
        return;
    }

    const std::size_t available = std::min(
        frame_->pre_samples_available[channel], pre_samples);
    const std::size_t known_begin = pre_samples - available;
    if (available > 0) {
        // The known samples occupy the right-hand tail of the pre-trigger
        // region. A later DMA-backlog sample shifts that tail left by one;
        // zero-filled unknown history remains on the left.
        std::move(frame_->samples[channel].begin() + known_begin + 1,
                  frame_->samples[channel].begin() + pre_samples,
                  frame_->samples[channel].begin() + known_begin);
    }
    frame_->samples[channel][pre_samples - 1] = sample;
    frame_->pre_samples_available[channel] =
        std::min(pre_samples, available + static_cast<std::size_t>(1));
}

}  // namespace smartgear
