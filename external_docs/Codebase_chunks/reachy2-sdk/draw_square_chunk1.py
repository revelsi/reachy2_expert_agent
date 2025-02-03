"""Example of how to draw a square with Reachy's right arm."""

import logging
import time

import numpy as np
import numpy.typing as npt

from reachy2_sdk import ReachySDK


def build_pose_matrix(x: float, y: float, z: float) -> npt.NDArray[np.float64]:
    """Build a 4x4 pose matrix for a given position in 3D space, with the effector at a fixed orientation.

    Args:
        x: The x-coordinate of the position.
        y: The y-coordinate of the position.
        z: The z-coordinate of the position.

    Returns:
        A 4x4 NumPy array representing the pose matrix.
    """
    # The effector is always at the same orientation in the world frame
    return np.array(
        [
            [0, 0, -1, x],
            [0, 1, 0, y],
            [1, 0, 0, z],
            [0, 0, 0, 1],
        ]
    )


def draw_square(reachy: ReachySDK) -> None:
    """Draw a square path with Reachy's right arm in 3D space.

    This function commands Reachy's right arm to move in a square pattern
    using four predefined positions (A, B, C, and D) in the world frame.
    The square is drawn by moving the arm sequentially through these positions:
    - A: (0.4, -0.5, -0.2)
    - B: (0.4, -0.5, 0)
    - C: (0.4, -0.3, 0)
    - D: (0.4, -0.3, -0.2)

    see https://pollen-robotics.github.io/reachy2-docs/developing-with-reachy-2/basics/4-use-arm-kinematics/
    for Reachy's coordinate system