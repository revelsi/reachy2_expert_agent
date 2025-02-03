see https://pollen-robotics.github.io/reachy2-docs/developing-with-reachy-2/basics/4-use-arm-kinematics/
    for Reachy's coordinate system

    Each movement uses inverse kinematics to calculate the required joint
    positions to achieve the target pose and then sends the commands to
    Reachy's arm to execute the movements.

    Args:
        reachy: An instance of the ReachySDK used to control the robot.
    """
    # Going from A to B
    target_pose = build_pose_matrix(0.4, -0.5, 0)
    ik = reachy.r_arm.inverse_kinematics(target_pose)
    reachy.r_arm.goto(ik, duration=2.0, degrees=True)

    current_pos = reachy.r_arm.forward_kinematics()
    print("Pose B: ", current_pos)

    # Going from B to C
    target_pose = build_pose_matrix(0.4, -0.3, 0)
    ik = reachy.r_arm.inverse_kinematics(target_pose)
    reachy.r_arm.goto(ik, duration=2.0, degrees=True)

    current_pos = reachy.r_arm.forward_kinematics()
    print("Pose C: ", current_pos)

    # Going from C to D
    target_pose = build_pose_matrix(0.4, -0.3, -0.2)
    ik = reachy.r_arm.inverse_kinematics(target_pose)
    reachy.r_arm.goto(ik, duration=2.0, degrees=True)

    current_pos = reachy.r_arm.forward_kinematics()
    print("Pose D: ", current_pos)

    # Going from D to A
    target_pose = build_pose_matrix(0.4, -0.5, -0.2)
    ik = reachy.r_arm.inverse_kinematics(target_pose)
    reachy.r_arm.goto(ik, duration=2.0, degrees=True, wait=True)