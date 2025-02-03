def open_gripper() -> None:
    goto({reachy.r_arm.r_gripper: -50}, duration=1.0)


def close_gripper() -> None:
    goto({reachy.r_arm.r_gripper: 0}, duration=1.0)


start_pose = fv_utils.make_pose([0.17, -0.16, -0.3], [0, -90, 0])
joint_start_pose = reachy.r_arm.inverse_kinematics(start_pose)


def goto_start_pose() -> None:
    goto({joint: pos for joint, pos in zip(reachy.r_arm.joints.values(), joint_start_pose)}, duration=2.0)
    open_gripper()


goto_start_pose()


def uv_to_xyz(z: float, u: float, v: float, K: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    cx = K[0, 2]
    cy = K[1, 2]
    fx = K[0, 0]
    fy = K[1, 1]

    # Calcul des coordonnées dans le monde
    x = (u - cx) * z / fx
    y = (v - cy) * z / fy

    return np.array([x, y, z])


def get_centroid(mask: npt.NDArray[np.uint8]) -> Tuple[int, int]:
    mask = mask.astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        raise Exception("No contours found")
    c = max(contours, key=cv2.contourArea)
    M = cv2.moments(c)
    if M["m00"] == 0:
        raise Exception("No contours found")
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return cX, cY