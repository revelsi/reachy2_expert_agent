import cv2
import numpy as np
from cv2 import aruco
from pollen_vision.camera_wrappers import CameraWrapper, SDKWrapper
from pollen_vision.camera_wrappers.depthai.utils import get_config_file_path

ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
MARKER_LENGTH = 0.01558
SQUARE_LENGTH = 0.02075
BOARD_SIZE = (11, 8)
BOARD_WIDTH = BOARD_SIZE[0] * SQUARE_LENGTH
BOARD_HEIGHT = BOARD_SIZE[1] * SQUARE_LENGTH
board = cv2.aruco.CharucoBoard(BOARD_SIZE, SQUARE_LENGTH, MARKER_LENGTH, ARUCO_DICT)
board.setLegacyPattern(True)
charuco_detector = cv2.aruco.CharucoDetector(board)


def get_charuco_board_pose_in_cam(image, K, D):  # type: ignore
    charuco_corners, charuco_ids, marker_corners, marker_ids = charuco_detector.detectBoard(image)
    if charuco_corners is None:
        return None, None, None

    obj_points, img_points = board.matchImagePoints(charuco_corners, charuco_ids)

    if len(obj_points) < 4:
        return None, None, None

    flag, rvec, tvec = cv2.solvePnP(obj_points, img_points, K, D)

    T_cam_frame = np.eye(4)
    T_cam_frame[:3, :3], _ = cv2.Rodrigues(rvec.flatten())
    T_cam_frame[:3, 3] = tvec.flatten()
    # T_cam_frame = fv_utils.translateInSelf(T_cam_frame, [w / 2, h / 2, 0])

    return T_cam_frame, marker_corners, marker_ids


class FOVCalculator:
    def __init__(self, cam: CameraWrapper):
        self.cam = cam
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
        self.run()