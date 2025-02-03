"""This script is used to annotate a video with the OwlViT and SAM models.

The script takes a video as input and can output a new video with the detected objects and their segmentation masks.
Use the `--with-segmentation` flag to perform segmentation. By default, the script will only perform object detection.


Args:
    -v: the path to the video to annotate
    --with-segmentation: add this flag to perform segmentation
    -t: the detection threshold for the object detection model (default: 0.2)
    --classes: a list of classes to detect. Separate the classes with a space. Example: --classes 'robot' 'mug'

Example:
    python annotate_video.py -v path/to/video.mp4 --with-segmentation -t 0.2 --classes 'robot' 'mug'"

Output:
    The annotated video will be saved in the same directory as the input video with the suffix "_annotated".
"""

import argparse
import asyncio

import cv2
import numpy as np
import tqdm
from pollen_vision.utils import Annotator, get_bboxes
from pollen_vision.vision_models.object_detection import OwlVitWrapper
from pollen_vision.vision_models.object_segmentation import MobileSamWrapper
from recorder import Recorder