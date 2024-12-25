# src/frame_extractor.py

import cv2
import os


def extract_frames(video_path, output_folder="frames/", interval=5):
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_id = 0
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % interval == 0:
            frames.append(frame)

        frame_id += 1

    cap.release()
    return frames
