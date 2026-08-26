cmake_minimum_required(VERSION 3.16)

# The default target is an object-only register-binding check. An explicitly
# enabled reference target adds a minimal startup/vector table, linker script
# and freestanding runtime; it remains a board-independent reference image,
# not a substitute for the final RCC, input conditioning and CS review.
project(pingpang_smartgear_stm32g031_register_port LANGUAGES CXX)

set(STM32_CMSIS_DEVICE_G0_INCLUDE_DIR "" CACHE PATH
    "Directory containing the official stm32g031xx.h")
set(STM32_CMSIS_CORE_INCLUDE_DIR "" CACHE PATH
    "Directory containing the matching CMSIS core_cm0plus.h")
set(STM32_CXX_EXTRA_INCLUDE_DIRS "" CACHE STRING
    "Semicolon-separated C++ standard-header paths for freestanding toolchains")

if(NOT STM32_CMSIS_DEVICE_G0_INCLUDE_DIR OR
   NOT STM32_CMSIS_CORE_INCLUDE_DIR)
    message(FATAL_ERROR
        "Set STM32_CMSIS_DEVICE_G0_INCLUDE_DIR and "
        "STM32_CMSIS_CORE_INCLUDE_DIR to build the optional target")
endif()

add_library(m6_carrier_stm32g031_register_port OBJECT
    m6_carrier_stm32g031_register_port.cpp
    m6_carrier_stm32g031_port.cpp
    ../m6_carrier_capture_core.cpp
    ../m6_carrier_spi_slave_transport.cpp
    ../../main/m6_carrier_protocol.cpp
)

target_compile_features(m6_carrier_stm32g031_register_port PRIVATE cxx_std_17)
target_compile_definitions(m6_carrier_stm32g031_register_port PRIVATE STM32G031xx)
target_include_directories(m6_carrier_stm32g031_register_port PRIVATE
    ${STM32_CMSIS_DEVICE_G0_INCLUDE_DIR}
    ${STM32_CMSIS_CORE_INCLUDE_DIR}
    .
    ..
    ../../main
)
if(STM32_CXX_EXTRA_INCLUDE_DIRS)
    target_include_directories(m6_carrier_stm32g031_register_port SYSTEM PRIVATE
        ${STM32_CXX_EXTRA_INCLUDE_DIRS})
endif()
target_compile_options(m6_carrier_stm32g031_register_port PRIVATE
    -mcpu=cortex-m0plus
    -mthumb
    -ffreestanding
    -fno-exceptions
    -fno-rtti
    -fno-use-cxa-atexit
    -ffunction-sections
    -fdata-sections
    -Wall
    -Wextra
    -Wpedantic
    -Werror
)

option(BUILD_FLASHABLE_REFERENCE
       "Build the minimal STM32G031 reference ELF and raw binary" OFF)

if(BUILD_FLASHABLE_REFERENCE)
    find_program(STM32_OBJCOPY arm-none-eabi-objcopy)
    if(NOT STM32_OBJCOPY)
        message(FATAL_ERROR
            "BUILD_FLASHABLE_REFERENCE requires arm-none-eabi-objcopy")
    endif()

    add_executable(m6_carrier_stm32g031_reference
        m6_carrier_stm32g031_main.cpp
        m6_carrier_stm32g031_startup.cpp
        m6_carrier_stm32g031_runtime.cpp
        m6_carrier_stm32g031_register_port.cpp
        m6_carrier_stm32g031_port.cpp
        ../m6_carrier_capture_core.cpp
        ../m6_carrier_spi_slave_transport.cpp
        ../../main/m6_carrier_protocol.cpp
    )
    target_compile_features(m6_carrier_stm32g031_reference PRIVATE cxx_std_17)
    target_compile_definitions(m6_carrier_stm32g031_reference PRIVATE
        STM32G031xx)
    target_include_directories(m6_carrier_stm32g031_reference PRIVATE
        ${STM32_CMSIS_DEVICE_G0_INCLUDE_DIR}
        ${STM32_CMSIS_CORE_INCLUDE_DIR}
        .
        ..
        ../../main
    )
    if(STM32_CXX_EXTRA_INCLUDE_DIRS)
        target_include_directories(m6_carrier_stm32g031_reference SYSTEM PRIVATE
            ${STM32_CXX_EXTRA_INCLUDE_DIRS})
    endif()
    target_compile_options(m6_carrier_stm32g031_reference PRIVATE
        -mcpu=cortex-m0plus
        -mthumb
        -ffreestanding
        -fno-exceptions
        -fno-rtti
        -fno-use-cxa-atexit
        -ffunction-sections
        -fdata-sections
        -Wall
        -Wextra
        -Wpedantic
        -Werror
    )
    target_link_options(m6_carrier_stm32g031_reference PRIVATE
        -mcpu=cortex-m0plus
        -mthumb
        -nostartfiles
        -nostdlib
        -nodefaultlibs
        "-T${CMAKE_CURRENT_SOURCE_DIR}/stm32g031k8u6.ld"
        "-Wl,--gc-sections,-Map,${CMAKE_CURRENT_BINARY_DIR}/m6_carrier_stm32g031_reference.map"
    )
    target_link_libraries(m6_carrier_stm32g031_reference PRIVATE gcc)
    add_custom_command(TARGET m6_carrier_stm32g031_reference POST_BUILD
        COMMAND ${STM32_OBJCOPY} -O binary
            $<TARGET_FILE:m6_carrier_stm32g031_reference>
            ${CMAKE_CURRENT_BINARY_DIR}/m6_carrier_stm32g031_reference.bin
        COMMENT "Generating m6_carrier_stm32g031_reference.bin"
    )
endif()
