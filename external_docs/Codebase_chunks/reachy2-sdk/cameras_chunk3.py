if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    argParser = argparse.ArgumentParser(description="SDK camera example")
    argParser.add_argument(
        "mode",
        type=str,
        choices=["teleop", "depth"],
    )
    args = argParser.parse_args()

    reachy = ReachySDK(host="localhost")

    if not reachy.is_connected:
        exit("Reachy is not connected.")

    if reachy.cameras is None:
        exit("There is no connected camera.")

    if args.mode == "teleop":
        display_teleop_cam()
    elif args.mode == "depth":
        display_depth_cam()