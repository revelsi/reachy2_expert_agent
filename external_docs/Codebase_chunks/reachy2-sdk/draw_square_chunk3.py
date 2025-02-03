current_pos = reachy.r_arm.forward_kinematics()
    print("Pose D: ", current_pos)

    # Going from D to A
    target_pose = build_pose_matrix(0.4, -0.5, -0.2)
    ik = reachy.r_arm.inverse_kinematics(target_pose)
    reachy.r_arm.goto(ik, duration=2.0, degrees=True, wait=True)

    current_pos = reachy.r_arm.forward_kinematics()
    print("Pose A: ", current_pos)


def goto_to_point_A(reachy: ReachySDK) -> None:
    """Move Reachy's right arm to Point A in 3D space.

    This function commands Reachy's right arm to move to a specified target position
    (Point A) in the world frame, which is located at (0.4, -0.5, -0.2).

    Args:
        reachy: An instance of the ReachySDK used to control the robot.
    """
    # position of point A in space
    target_pose = build_pose_matrix(0.4, -0.5, -0.2)
    # get the position in the joint space
    joints_positions = reachy.r_arm.inverse_kinematics(target_pose)
    # move Reachy's right arm to this point
    reachy.r_arm.goto(joints_positions, duration=2, wait=True)


if __name__ == "__main__":
    print("Reachy SDK example: draw square")

    logging.basicConfig(level=logging.INFO)
    reachy = ReachySDK(host="localhost")

    if not reachy.is_connected:
        exit("Reachy is not connected.")

    print("Turning on Reachy")
    reachy.turn_on()

    time.sleep(0.2)

    print("Set to Elbow 90 pose ...")
    goto_ids = reachy.goto_posture("elbow_90", wait=True)
    # wait_for_pose_to_finish(goto_ids)