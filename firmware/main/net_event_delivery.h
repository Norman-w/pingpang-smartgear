#pragma once

#include <cstddef>
#include <string>

#include "net_event.h"
#include "net_sensor_config.h"
#include "ring_buffer.h"

namespace smartgear {

// SmartPaddle WebSocket、BLE/MQTT/SSE 适配层只需实现这个发送函数。
// 返回 true 表示本条已经被传输层接收；false 会保留在 RAM 缓存中。
using NetEventSendFunction = bool (*)(const char* json, void* context);

class NetEventDelivery {
  public:
    void set_transport(bool connected,
                       NetEventSendFunction send,
                       void* context = nullptr) {
        connected_ = connected;
        send_ = send;
        context_ = context;
        if (connected_) {
            flush();
        }
    }

    bool publish(const NetEvent& event) {
        if (connected_ && send_ != nullptr) {
            const std::string json = net_event_to_json(event);
            if (send_(json.c_str(), context_)) {
                return true;
            }
        }
        cache_.push(event);
        return false;
    }

    std::size_t flush() {
        if (!connected_ || send_ == nullptr) {
            return 0;
        }
        std::size_t sent = 0;
        NetEvent event;
        while (cache_.peek(event)) {
            const std::string json = net_event_to_json(event);
            if (!send_(json.c_str(), context_)) {
                break;
            }
            cache_.discard();
            ++sent;
        }
        return sent;
    }

    std::size_t cached_count() const { return cache_.size(); }
    std::size_t dropped_count() const { return cache_.dropped_count(); }

  private:
    bool connected_ = false;
    NetEventSendFunction send_ = nullptr;
    void* context_ = nullptr;
    RingBuffer<NetEvent, config::kEventCacheCapacity> cache_;
};

}  // namespace smartgear
