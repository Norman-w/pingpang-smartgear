cmake_minimum_required(VERSION 3.16)
project(pingpang_smartgear_host_tests LANGUAGES CXX)

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
    ../main/feedback.cpp
)
target_include_directories(net_event_tests PRIVATE ../main)
target_compile_options(net_event_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)

enable_testing()
add_test(NAME net_event_unit_tests COMMAND net_event_tests)
