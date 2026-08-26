#if defined(SMARTGEAR_SMARTPADDLE_WS)

#include <cstring>

#include "esp_err.h"
#include "ws_data_server.h"

// Build this translation unit with SMARTGEAR_SMARTPADDLE_WS and the
// SmartPaddle firmware/main include path when both projects are linked into
// one ESP-IDF target. The default Pingpang build leaves the weak hooks in
// net_event_transport.cpp in place, so it does not silently claim a network
// connection that was never linked.
extern "C" bool smartgear_board_transport_connected() {
    return ws_data_has_client();
}

extern "C" bool smartgear_board_transport_send_json(const char* json) {
    return json != nullptr &&
           ws_data_send_text(json, std::strlen(json)) == ESP_OK;
}

#endif
