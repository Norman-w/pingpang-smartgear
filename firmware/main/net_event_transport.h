#pragma once

// The existing SmartPaddle connection layer overrides these weak C hooks.
// Keeping the boundary C-shaped avoids copying BLE/WebSocket/MQTT/SSE code into
// this business component while still making the ESP32 runtime actually able
// to publish and recover NetEvent messages.
extern "C" {

bool smartgear_board_transport_connected();
bool smartgear_board_transport_send_json(const char* json);

}
