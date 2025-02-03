def compute_fov(self, z, w, h):  # type: ignore
        print("Computing fov ...")

        # Compute the field of view based on K
        fov_x = np.rad2deg(2 * np.arctan(w / (2 * self.cam.get_K("left")[0, 0])))
        fov_y = np.rad2deg(2 * np.arctan(h / (2 * self.cam.get_K("left")[1, 1])))
        print(f"Theoretical Horizontal FOV: {fov_x:.2f} degrees")
        print(f"Theoretical Vertical FOV: {fov_y:.2f} degrees")

        # Compute the field of view based on data
        fov_x = np.rad2deg(2 * np.arctan((BOARD_WIDTH / 2) / z))
        fov_y = np.rad2deg(2 * np.arctan((BOARD_HEIGHT / 2) / z))
        print(f"Measured Horizontal FOV: {fov_x:.2f} degrees")
        print(f"Measured Vertical FOV: {fov_y:.2f} degrees")


if __name__ == "__main__":
    cam = SDKWrapper(get_config_file_path("CONFIG_IMX296"), fps=30, compute_depth=False, rectify=True)
    # cam = TeleopWrapper(get_config_file_path("CONFIG_IMX296"), fps=30)
    fov_calc = FOVCalculator(cam)