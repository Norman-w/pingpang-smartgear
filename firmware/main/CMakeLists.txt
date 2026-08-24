idf_component_register(
    SRCS
        "main.cpp"
        "net_event.cpp"
        "beam_capture.cpp"
        "piezo_capture.cpp"
        "piezo_waveform.cpp"
        "piezo_waveform_archive.cpp"
        "net_event_aggregator.cpp"
        "sensor_self_test.cpp"
        "sensor_health_gate.cpp"
        "feedback.cpp"
        "feedback_gpio.cpp"
        "piezo_adc_continuous.cpp"
        "piezo_waveform_hook.cpp"
        "net_event_transport.cpp"
        "sensor_board_hooks.cpp"
    INCLUDE_DIRS "."
    REQUIRES driver esp_timer freertos esp_adc
)
