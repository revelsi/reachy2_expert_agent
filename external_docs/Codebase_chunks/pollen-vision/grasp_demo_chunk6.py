T_cam_mug = fv_utils.make_pose(xyz, [0, 0, 0])
                T_world_mug = T_world_cam @ T_cam_mug
                T_world_mug[:3, :3] = np.eye(3)
                fv.pushFrame(T_world_mug, "mug")

                print(object_to_grasp, "detected !")

                im = MSW.annotate(im, [mask], bboxes, labels, labels_colors=OW.labels_colors)
                im = cv2.circle(im, (u, v), 5, (0, 255, 0), -1)
                cv2.imshow("masked_depth", depth * 255)
                cv2.imshow("im", np.array(cv2.cvtColor(im, cv2.COLOR_RGB2BGR)))
                print("press enter to grasp, any other key to cancel")
                key = cv2.waitKey(0)
                if key == 13:
                    grasp(T_world_mug)
                    break
                else:
                    break

            cv2.imshow("im", np.array(cv2.cvtColor(im, cv2.COLOR_RGB2BGR)))
            key = cv2.waitKey(1)
            if key == 27:
                break

except KeyboardInterrupt:
    print("")
    print("")
    print("")
    print("TURNING OFF")
    reachy.turn_off_smoothly("r_arm")
    time.sleep(3)
    print("DONE")
    exit()