except KeyboardInterrupt:
        logging.info("User Interrupt")


def display_depth_cam() -> None:
    """Display live frames from the depth camera.

    This function retrieves and displays RGB and depth frames from the depth camera.
    It normalizes the depth map for visualization and shows the RGB frame and normalized depth
    frame side by side. The function exits upon a keyboard interrupt.

    Raises:
        SystemExit: If the depth camera is not available.
    """
    if reachy.cameras.depth is None:
        exit("There is no depth camera.")

    print(f"Depth camera parameters {reachy.cameras.depth.get_parameters()}")
    print(f"Depth camera extrinsic parameters {reachy.cameras.depth.get_extrinsics()}")

    try:
        while True:
            rgb, ts = reachy.cameras.depth.get_frame()
            depth, ts_r = reachy.cameras.depth.get_depth_frame()
            depth_map_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)  # type: ignore [attr-defined]
            cv2.imshow("frame", rgb)
            cv2.imshow("depthn", depth_map_normalized)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        logging.info("User Interrupt")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    argParser = argparse.ArgumentParser(description="SDK camera example")
    argParser.add_argument(
        "mode",
        type=str,
        choices=["teleop", "depth"],
    )
    args = argParser.parse_args()