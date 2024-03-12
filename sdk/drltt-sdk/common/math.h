#pragma once

#include <algorithm>

const float EPSILON = 1e-6;

/**
 * @brief Clip an object. Comparison operator need to be implemented for this
 * object
 *
 * @tparam T Object type.
 * @param n Object to be clipped.
 * @param lower Lower bound.
 * @param upper Upper bound.
 * @return T Clipped object.
 */
template <typename T>
T clip(const T& n, const T& lower, const T& upper) {
  return std::max(lower, std::min(n, upper));
}
