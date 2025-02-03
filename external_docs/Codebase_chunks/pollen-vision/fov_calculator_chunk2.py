return T_cam_frame, marker_corners, marker_ids


class FOVCalculator:
    def __init__(self, cam: CameraWrapper):
        self.cam = cam
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_1000)
        self.run()

    def run(self) -> None:
        z, w, h = None, None, None
        while True:
            data, _, _ = self.cam.get_data()

            im = data["left"]
            if w is None:
                h, w = im.shape[:2]

            T_cam_board, corners, ids = get_charuco_board_pose_in_cam(
                im, self.cam.get_K("left"), self.cam.get_D("left")
            )  # type: ignore
            if corners is not None and ids is not None:
                im = aruco.drawDetectedMarkers(im, corners, ids)
                z = T_cam_board[:3, 3][2]

            im = cv2.putText(
                im,
                "Move the charuco board so that if fills the entire field of view. Press Enter when done.",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("im", im)
            key = cv2.waitKey(1)
            if key == 13:  # Enter
                break
        self.compute_fov(z, w, h)  # type: ignore

    def compute_fov(self, z, w, h):  # type: ignore
        print("Computing fov ...")