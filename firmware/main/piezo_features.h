#pragma once

#include <array>
#include <cstdint>

namespace smartgear {

struct PiezoFeatureSummary {
    std::array<float, 2> peak = {0.0F, 0.0F};
    std::array<float, 2> energy = {0.0F, 0.0F};
    std::uint64_t duration_us = 0;
};

}  // namespace smartgear
