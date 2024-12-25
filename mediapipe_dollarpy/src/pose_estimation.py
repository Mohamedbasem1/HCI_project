import cv2
import mediapipe as mp
from src.angle_calculation import calculate_angle

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def get_angles(frames):
    angles = []
    with mp_pose.Pose(static_image_mode=True) as pose:
        for frame in frames:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
                knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
                ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
                angle = calculate_angle(hip, knee, ankle)
                angles.append(angle)

                # Draw the full pose landmarks on the frame
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return angles