#!/usr/bin/env python3
"""
PEMs_Example.py -- Python translation of PEMs_Example.m

Run from a terminal with:
    python3 PEMs_Example.py
"""

import pems
from pems import (
    get_object_detection_probability,
    get_position_estimation_error,
    get_heading_estimation_error,
    get_existence_probability,
)


def main():
    pems.set_seed()   # equivalent of rng('shuffle'); use pems.set_seed(42) for reproducible runs

    # Select LiDAR type and perception stage
    lidar_type = "OS2-128"          # Available inputs: OS2-128, OS2-64, OS1-64
    perception_stage = "detection"  # Available inputs: detection or validation

    # Set distance and angle of the target object relative to the ego-vehicle's
    # right-hand coordinate system (shown below)
    distance = 100   # meters
    angle = 0        # degrees

    # ---------------------------------------
    #    y ^                     ----------
    #      |                     | TARGET |
    #   -------                  ----------
    #   | EGO | -->
    #   -------   x
    # ---------------------------------------

    # Get detection probability
    detection_probability = get_object_detection_probability(
        lidar_type, perception_stage, distance, angle)
    object_detected = pems.rand() < detection_probability   # true with probability p
    print(f"Object detected? {int(object_detected)} (1 = yes, 0 = no)")

    # If the object is detected, get position and heading estimation error as
    # well as the existence probability
    if object_detected:
        x_error, y_error = get_position_estimation_error(
            lidar_type, perception_stage, distance, angle)
        heading_error = get_heading_estimation_error(
            lidar_type, perception_stage, distance, angle)
        existence_prob = get_existence_probability(
            lidar_type, perception_stage, distance, angle)
        print(f"X error: {x_error:.2f} m, Y error: {y_error:.2f}, heading error: {heading_error:.1f}°, "
              f"existence probability: {existence_prob:.2f}")


if __name__ == "__main__":
    main()
