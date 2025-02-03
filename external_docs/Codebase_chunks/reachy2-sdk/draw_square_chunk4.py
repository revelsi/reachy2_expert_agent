if not reachy.is_connected:
        exit("Reachy is not connected.")

    print("Turning on Reachy")
    reachy.turn_on()

    time.sleep(0.2)

    print("Set to Elbow 90 pose ...")
    goto_ids = reachy.goto_posture("elbow_90", wait=True)
    # wait_for_pose_to_finish(goto_ids)

    print("Move to point A")
    goto_to_point_A(reachy)

    print("Draw a square with the right arm ...")
    draw_square(reachy)

    print("Set to Zero pose ...")
    goto_ids = reachy.goto_posture("default", wait=True)
    # wait_for_pose_to_finish(goto_ids)

    time.sleep(0.2)

    exit("Exiting example")