left_img = data["left"]
        right_img = data["right"]
        depth = data["depth"]
        depth = np.repeat(depth[:, :, np.newaxis], 3, axis=2)

        asyncio.run(rec_left.new_im(left_img.astype(np.uint8)))
        asyncio.run(rec_right.new_im(right_img.astype(np.uint8)))
        asyncio.run(rec_depth.new_im(depth.astype(np.uint8)))
        end = time.time()

        took = end - start

        time.sleep(max(0, (1 / FPS) - took))  # Compensating for jitteriness

except KeyboardInterrupt:
    print("Saving ...")
    pass

rec_left.stop()
rec_right.stop()
rec_depth.stop()

print("Done!")
print("Done!")