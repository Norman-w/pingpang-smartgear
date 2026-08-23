#include "net_event_transport.h"

#if defined(__GNUC__)
#define SMARTGEAR_WEAK __attribute__((weak))
#else
#define SMARTGEAR_WEAK
#endif

extern "C" SMARTGEAR_WEAK bool smartgear_board_transport_connected() {
    return false;
}

extern "C" SMARTGEAR_WEAK bool smartgear_board_transport_send_json(
    const char* /*json*/) {
    return false;
}

#undef SMARTGEAR_WEAK
