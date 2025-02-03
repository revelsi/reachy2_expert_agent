lift_pose = grasp_pose.copy()
    lift_pose[:3, 3] += np.array([0, 0, 0.1])
    joint_lift_pose = reachy.r_arm.inverse_kinematics(lift_pose)
    goto({joint: pos for joint, pos in zip(reachy.r_arm.joints.values(), joint_lift_pose)}, duration=1.0)

    goto({joint: pos for joint, pos in zip(reachy.r_arm.joints.values(), joint_grasp_pose)}, duration=1.0)

    open_gripper()

    goto_start_pose()


try:
    while True:
        print("")
        print("")
        print("")
        object_to_grasp = input("what do you want to grasp ? : ")
        print("press esc to cancel")
        while True:
            T_world_hand = reachy.r_arm.forward_kinematics()
            fv.pushFrame(T_world_hand, "hand")
            fv.updateMesh("gripper", T_world_hand)

            data, _, _ = w.get_data()
            im = data["left"]
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            depth = data["depth"]