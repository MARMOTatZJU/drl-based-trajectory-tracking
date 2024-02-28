
#include <algorithm>
#include <cmath>


// TODO: import from: https://github.com/ros/angles

/**
 * Normalize a scalar angle to [0, 2*pi).
 * Source: http://docs.ros.org/en/indigo/api/angles/html/angles_8h_source.html, L68
 * @param angle Input angle.
 * @return Normalized angle.
*/
static inline double normalize_angle_positive(double angle) {
  return fmod(fmod(angle, 2.0 * M_PI) + 2.0 * M_PI, 2.0 * M_PI);
}

/**
 * Normalize a scalar angle to [-pi, pi).
 * Source: http://docs.ros.org/en/indigo/api/angles/html/angles_8h_source.html, L81
 * @param angle Input angle.
 * @return Normalized angle.
*/
static inline double normalize_angle(double angle) {
  double a = normalize_angle_positive(angle);
  if (a >= M_PI)
    a -= 2.0 * M_PI;
  return a;
}
