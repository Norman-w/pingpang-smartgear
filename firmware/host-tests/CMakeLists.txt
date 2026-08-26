cmake_minimum_required(VERSION 3.16)
project(pingpang_smartgear_host_tests LANGUAGES CXX)

option(SMARTGEAR_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(net_event_tests
    test_net_event.cpp
    ../main/net_event.cpp
    ../main/beam_capture.cpp
    ../main/beam_channel_map.cpp
    ../main/piezo_capture.cpp
    ../main/piezo_waveform.cpp
    ../main/piezo_waveform_archive.cpp
    ../main/net_event_aggregator.cpp
    ../main/sensor_self_test.cpp
    ../main/sensor_health_gate.cpp
    ../main/feedback.cpp
    ../main/piezo_waveform_hook.cpp
    ../main/net_event_transport.cpp
    ../main/sensor_board_hooks.cpp
)
target_include_directories(net_event_tests PRIVATE ../main)
target_compile_options(net_event_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)

add_executable(net_event_trace
    trace_replay.cpp
    ../main/net_event.cpp
    ../main/beam_capture.cpp
    ../main/beam_channel_map.cpp
    ../main/piezo_capture.cpp
    ../main/piezo_waveform.cpp
    ../main/net_event_aggregator.cpp
)
target_include_directories(net_event_trace PRIVATE ../main)
target_compile_options(net_event_trace PRIVATE -Wall -Wextra -Wpedantic -Werror)

add_executable(m6_carrier_protocol_tests
    test_m6_carrier_protocol.cpp
    ../main/m6_carrier_protocol.cpp
    ../main/m6_carrier_adapter.cpp
    ../main/beam_capture.cpp
    ../carrier/m6_carrier_capture_core.cpp
    ../carrier/m6_carrier_spi_slave_transport.cpp
)
target_include_directories(m6_carrier_protocol_tests PRIVATE ../main ../carrier)
target_compile_options(m6_carrier_protocol_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)

add_executable(m6_carrier_stm32g031_port_tests
    test_m6_carrier_stm32g031_port.cpp
    ../main/m6_carrier_protocol.cpp
    ../carrier/m6_carrier_capture_core.cpp
    ../carrier/m6_carrier_spi_slave_transport.cpp
    ../carrier/stm32g031-reference/m6_carrier_stm32g031_port.cpp
)
target_include_directories(m6_carrier_stm32g031_port_tests PRIVATE
    ../main
    ../carrier
    ../carrier/stm32g031-reference
)
target_compile_options(m6_carrier_stm32g031_port_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)

if(SMARTGEAR_SANITIZERS)
    set(SMARTGEAR_SANITIZER_FLAGS -fsanitize=address,undefined -fno-omit-frame-pointer)
    foreach(target net_event_tests net_event_trace m6_carrier_protocol_tests m6_carrier_stm32g031_port_tests)
        target_compile_options(${target} PRIVATE ${SMARTGEAR_SANITIZER_FLAGS})
        target_link_options(${target} PRIVATE ${SMARTGEAR_SANITIZER_FLAGS})
    endforeach()
endif()

enable_testing()
add_test(NAME net_event_unit_tests COMMAND net_event_tests)
add_test(
    NAME net_event_trace_replay
    COMMAND net_event_trace ${CMAKE_CURRENT_SOURCE_DIR}/fixtures/net_trace_v0.1.csv
)
add_test(NAME m6_carrier_protocol COMMAND m6_carrier_protocol_tests)
add_test(
    NAME m6_carrier_stm32g031_port
    COMMAND m6_carrier_stm32g031_port_tests
)
