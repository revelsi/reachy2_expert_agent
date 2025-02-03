if use_segmentation:
    print("Instantiating mobile sam ...")
    sam = MobileSamWrapper()

A = Annotator()


annotated_video_path = args.video.split(".")[0] + "_annotated.mp4"
rec_left = Recorder(annotated_video_path)

classes = args.classes
detection_threshold = args.threshold

print(f"Starting video annotation for classes: {classes} with detection threshold {detection_threshold}...")

for i in tqdm.tqdm(range(nb_frames_left)):
    ret, left_frame = cap_left.read()
    if not ret:
        break

    predictions = owl_vit.infer(
        im=left_frame,
        candidate_labels=classes,
        detection_threshold=detection_threshold,
    )
    bboxes = get_bboxes(predictions)

    if use_segmentation:
        masks = sam.infer(left_frame, bboxes)
    else:
        masks = []

    left_frame = A.annotate(im=left_frame, detection_predictions=predictions, masks=masks)

    asyncio.run(rec_left.new_im(left_frame.astype(np.uint8)))


print("Saving video ...")
rec_left.stop()
print("Video saved")