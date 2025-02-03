import argparse
import asyncio
import datetime
import os
import time

import numpy as np
from pollen_vision.camera_wrappers.depthai import SDKWrapper
from pollen_vision.camera_wrappers.depthai.utils import get_config_file_path
from recorder import FPS, Recorder

argParser = argparse.ArgumentParser(description="record sr")
argParser.add_argument(
    "-o",
    "--out",
    type=str,
    required=True,
    help="Output directory",
)
argParser.add_argument(
    "-n",
    "--name",
    type=str,
    required=False,
    default=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    help="name of the session",
)
args = argParser.parse_args()

os.makedirs(args.out, exist_ok=True)
session_path = os.path.join(args.out, args.name)
os.makedirs(session_path, exist_ok=True)

w = SDKWrapper(get_config_file_path("CONFIG_SR"), compute_depth=True, fps=FPS)

rec_left = Recorder(os.path.join(session_path, "left_video.mp4"))
rec_right = Recorder(os.path.join(session_path, "right_video.mp4"))
rec_depth = Recorder(os.path.join(session_path, "depth_video.mp4"))

rec_left.start()
rec_right.start()
rec_depth.start()

print("")
print("")
print("========================")
print("Starting to record, press ctrl + c to stop")
try:
    while True:
        start = time.time()
        data, _, ts = w.get_data()

        left_img = data["left"]
        right_img = data["right"]
        depth = data["depth"]
        depth = np.repeat(depth[:, :, np.newaxis], 3, axis=2)