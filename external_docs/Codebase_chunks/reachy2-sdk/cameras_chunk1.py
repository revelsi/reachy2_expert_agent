"""Example script to display live frames from the teleoperation and depth cameras."""

import argparse
import logging

import cv2

from reachy2_sdk import ReachySDK
from reachy2_sdk.media.camera import CameraView


def display_teleop_cam() -> None:
    """Display live frames from the teleoperation camera.

    This function retrieves and displays frames from the left and right
    views of the teleoperation camera. The function terminates
    upon a keyboard interrupt.

    Raises:
        SystemExit: If the teleop camera is not available.
    """
    if reachy.cameras.teleop is None:
        exit("There is no teleop camera.")

    print(f"Left camera parameters {reachy.cameras.teleop.get_parameters(CameraView.LEFT)}")
    print(f"Left camera extrinsic parameters {reachy.cameras.teleop.get_extrinsics(CameraView.LEFT)}")
    # print(reachy.cameras.teleop.get_parameters(CameraView.RIGHT))

    try:
        while True:
            frame, ts = reachy.cameras.teleop.get_frame(CameraView.LEFT)
            frame_r, ts_r = reachy.cameras.teleop.get_frame(CameraView.RIGHT)
            print(f"timestamps secs: left {ts} - right {ts_r}")
            cv2.imshow("left", frame)
            cv2.imshow("right", frame_r)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        logging.info("User Interrupt")


def display_depth_cam() -> None:
    """Display live frames from the depth camera.