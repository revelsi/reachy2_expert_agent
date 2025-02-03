T_world_cam = fv_utils.make_pose([0.03, -0.15, 0.1], [0, 0, 0])
# T_world_cam = fv_utils.make_pose([0.0537, -0.1281, 0.1413], [0, 0, 0]) # Old mounting piece
T_world_cam[:3, :3] = np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]])
T_world_cam = fv_utils.rotateInSelf(T_world_cam, [-45, 0, 0])
fv.pushFrame(T_world_cam, "camera")

fv.createMesh(
    "gripper",
    "example_meshes/gripper_simplified.obj",
    fv_utils.make_pose([0, 0, 0], [0, 0, 0]),
    scale=10.0,
    wireFrame=True,
)


def grasp(T_world_mug: npt.NDArray[np.float32]) -> None:
    # Proceed to grasp
    pregrasp_pose = T_world_mug.copy()
    pregrasp_pose[:3, :3] = start_pose[:3, :3]
    pregrasp_pose[:3, 3] += np.array([-0.1, 0, 0.05])
    fv.pushFrame(pregrasp_pose, "pregrasp", color=(0, 255, 0))

    joint_pregrasp_pose = reachy.r_arm.inverse_kinematics(pregrasp_pose)
    goto({joint: pos for joint, pos in zip(reachy.r_arm.joints.values(), joint_pregrasp_pose)}, duration=1.0)

    grasp_pose = pregrasp_pose.copy()
    grasp_pose[:3, 3] += np.array([0.15, 0, 0])

    joint_grasp_pose = reachy.r_arm.inverse_kinematics(grasp_pose)
    goto({joint: pos for joint, pos in zip(reachy.r_arm.joints.values(), joint_grasp_pose)}, duration=1.0)
    close_gripper()

    lift_pose = grasp_pose.copy()
    lift_pose[:3, 3] += np.array([0, 0, 0.1])
    joint_lift_pose = reachy.r_arm.inverse_kinematics(lift_pose)
    goto({joint: pos for joint, pos in zip(reachy.r_arm.joints.values(), joint_lift_pose)}, duration=1.0)