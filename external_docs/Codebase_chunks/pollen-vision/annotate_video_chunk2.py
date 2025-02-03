import cv2
import numpy as np
import tqdm
from pollen_vision.utils import Annotator, get_bboxes
from pollen_vision.vision_models.object_detection import OwlVitWrapper
from pollen_vision.vision_models.object_segmentation import MobileSamWrapper
from recorder import Recorder

argParser = argparse.ArgumentParser(description="record sr")
argParser.add_argument(
    "-v",
    "--video",
    type=str,
    required=True,
    help="Video to annotate",
)
argParser.add_argument(
    "--with-segmentation",
    action="store_true",
    help="Whether to perform segmentation or not",
)
argParser.add_argument(
    "-t",
    "--threshold",
    type=float,
    default=0.2,
    help="Detection threshold for the object detection model",
)
argParser.add_argument(
    "--classes",
    nargs="+",
    required=True,
    help="Classes to detect. Separa Example: --classes 'robot' 'mug'",
)
args = argParser.parse_args()

cap_left = cv2.VideoCapture(args.video)
nb_frames_left = int(cap_left.get(cv2.CAP_PROP_FRAME_COUNT))

print("Instantiating owl vit ...")
owl_vit = OwlVitWrapper()

use_segmentation = args.with_segmentation

if use_segmentation:
    print("Instantiating mobile sam ...")
    sam = MobileSamWrapper()

A = Annotator()


annotated_video_path = args.video.split(".")[0] + "_annotated.mp4"
rec_left = Recorder(annotated_video_path)

classes = args.classes
detection_threshold = args.threshold