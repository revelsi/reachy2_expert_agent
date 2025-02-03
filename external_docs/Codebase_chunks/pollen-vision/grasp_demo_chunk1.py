# TODO Outdated

import argparse
import time
from typing import Tuple

import cv2
import FramesViewer.utils as fv_utils
import numpy as np
import numpy.typing as npt
from FramesViewer.viewer import Viewer
from pollen_vision.camera_wrappers.depthai import SDKWrapper
from pollen_vision.camera_wrappers.depthai.utils import (
    get_config_file_path,
    get_config_files_names,
)
from pollen_vision.vision_models.object_detection import OwlVitWrapper
from pollen_vision.vision_models.object_segmentation import MobileSamWrapper
from reachy_sdk import ReachySDK
from reachy_sdk.trajectory import goto

valid_configs = get_config_files_names()
argParser = argparse.ArgumentParser(description="Basic grasping demo")
argParser.add_argument(
    "--config",
    type=str,
    required=True,
    choices=valid_configs,
    help=f"Configutation file name : {valid_configs}",
)
args = argParser.parse_args()

w = SDKWrapper(get_config_file_path(args.config), compute_depth=True)
MSW = MobileSamWrapper()
OW = OwlVitWrapper()

fv = Viewer()
fv.start()
K = w.cam_config.get_K_left()

reachy = ReachySDK("10.0.0.93")
# reachy = ReachySDK("localhost")
reachy.turn_on("r_arm")


def open_gripper() -> None:
    goto({reachy.r_arm.r_gripper: -50}, duration=1.0)


def close_gripper() -> None:
    goto({reachy.r_arm.r_gripper: 0}, duration=1.0)


start_pose = fv_utils.make_pose([0.17, -0.16, -0.3], [0, -90, 0])
joint_start_pose = reachy.r_arm.inverse_kinematics(start_pose)