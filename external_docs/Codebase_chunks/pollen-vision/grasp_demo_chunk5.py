data, _, _ = w.get_data()
            im = data["left"]
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            depth = data["depth"]

            predictions = OW.infer(im, object_to_grasp)
            if len(predictions) != 0:
                bboxes = OW.get_bboxes(predictions)
                labels = OW.get_labels(predictions)
                mask = MSW.infer(im, bboxes)[0]
                depth[mask == 0] = 0
                average_depth = depth[depth != 0].mean()
                try:
                    u, v = get_centroid(mask)
                except Exception as e:
                    print(e)
                    break
                xyz = uv_to_xyz(average_depth * 0.1, u, v, K)
                xyz *= 0.01

                T_cam_mug = fv_utils.make_pose(xyz, [0, 0, 0])
                T_world_mug = T_world_cam @ T_cam_mug
                T_world_mug[:3, :3] = np.eye(3)
                fv.pushFrame(T_world_mug, "mug")

                print(object_to_grasp, "detected !")