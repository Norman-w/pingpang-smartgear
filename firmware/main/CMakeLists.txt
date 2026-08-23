idf_component_register(
    SRCS
        "main.cpp"
        "net_event.cpp"
        "beam_capture.cpp"
        "piezo_capture.cpp"
        "piezo_waveform.cpp"
        "net_event_aggregator.cpp"
        "sensor_self_test.cpp"
        "feedback.cpp"
        "feedback_gpio.cpp"
        "piezo_adc_continuous.cpp"
    INCLUDE_DIRS "."
    REQUIRES driver esp_timer freertos esp_adc
)
