#pragma once

// The external SmartPaddle/target connection layer is expected to override
// these weak C hooks. Keeping the boundary C-shaped avoids copying
// BLE/WebSocket/MQTT/SSE code into this business component while still making
// the ESP32 runtime able to publish and recover NetEvent messages once the
// target connection layer is linked.
extern "C" {

bool smartgear_board_transport_connected();
bool smartgear_board_transport_send_json(const char* json);

}
