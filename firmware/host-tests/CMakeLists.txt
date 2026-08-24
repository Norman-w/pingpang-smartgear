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
    ../main/piezo_capture.cpp
    ../main/piezo_waveform.cpp
    ../main/net_event_aggregator.cpp
)
target_include_directories(net_event_trace PRIVATE ../main)
target_compile_options(net_event_trace PRIVATE -Wall -Wextra -Wpedantic -Werror)

if(SMARTGEAR_SANITIZERS)
    set(SMARTGEAR_SANITIZER_FLAGS -fsanitize=address,undefined -fno-omit-frame-pointer)
    foreach(target net_event_tests net_event_trace)
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
