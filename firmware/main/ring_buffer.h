#pragma once

#include <array>
#include <cstddef>
#include <utility>

namespace smartgear {

template <typename T, std::size_t Capacity>
class RingBuffer {
    static_assert(Capacity > 0, "RingBuffer capacity must be positive");

  public:
    bool push(T value) {
        bool overwritten = false;
        if (size_ == Capacity) {
            head_ = (head_ + 1) % Capacity;
            --size_;
            ++dropped_count_;
            overwritten = true;
        }
        storage_[tail_] = std::move(value);
        tail_ = (tail_ + 1) % Capacity;
        ++size_;
        return !overwritten;
    }

    bool pop(T& value) {
        if (size_ == 0) {
            return false;
        }
        value = std::move(storage_[head_]);
        head_ = (head_ + 1) % Capacity;
        --size_;
        return true;
    }

    bool peek(T& value) const {
        if (size_ == 0) {
            return false;
        }
        value = storage_[head_];
        return true;
    }

    bool discard() {
        if (size_ == 0) {
            return false;
        }
        head_ = (head_ + 1) % Capacity;
        --size_;
        return true;
    }

    void clear() {
        head_ = 0;
        tail_ = 0;
        size_ = 0;
    }

    std::size_t size() const { return size_; }
    std::size_t dropped_count() const { return dropped_count_; }
    bool empty() const { return size_ == 0; }

  private:
    std::array<T, Capacity> storage_{};
    std::size_t head_ = 0;
    std::size_t tail_ = 0;
    std::size_t size_ = 0;
    std::size_t dropped_count_ = 0;
};

}  // namespace smartgear
