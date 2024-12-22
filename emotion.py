import mne
import numpy as np
import matplotlib.pyplot as plt
import cv2
import dlib
from deepface import DeepFace  # type: ignore

# Initialize Dlib's face detector and create a predictor for eye landmarks
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("c:/Users/medob/Desktop/Knee_exercises/shape_predictor_68_face_landmarks.dat")

# Initialize video capture with error handling
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Function to get the midpoint of the eye
def midpoint(p1, p2):
    return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

# Function to get the center of the eye
def eye_center(landmarks, eye_points):
    x = int((landmarks.part(eye_points[0]).x + landmarks.part(eye_points[3]).x) / 2)
    y = int((landmarks.part(eye_points[1]).y + landmarks.part(eye_points[4]).y) / 2)
    return x, y

# Function to map gaze points to screen coordinates
def map_gaze_to_screen(gaze_x, gaze_y, frame_width, frame_height, screen_width, screen_height):
    screen_x = int(gaze_x * screen_width / frame_width)
    screen_y = int(gaze_y * screen_height / frame_height)
    return screen_x, screen_y

# Create a 2D histogram (heatmap) of gaze points
heatmap, xedges, yedges = np.histogram2d([], [], bins=[100, 100], range=[[0, 1080], [0, 1920]])

# Create a grid of coordinates for plotting
xgrid, ygrid = np.meshgrid(xedges[:-1], yedges[:-1], indexing="ij")

# Plot the heatmap using MNE's `plot` function
fig, ax = plt.subplots(figsize=(8, 6))
pcm = ax.pcolormesh(xgrid, ygrid, heatmap.T, cmap='jet', shading='auto')
fig.colorbar(pcm, ax=ax, label='Gaze Density')
ax.set_xlabel('X Coordinates')
ax.set_ylabel('Y Coordinates')
ax.set_title('Gaze Tracking Heatmap')

# Initialize lists to store gaze points
gaze_x_list = []
gaze_y_list = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    frame_height, frame_width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    # Detect faces for emotion analysis
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    detected_faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for face in faces:
        landmarks = predictor(gray, face)
        
        left_eye_center = eye_center(landmarks, [36, 37, 38, 39, 40, 41])
        right_eye_center = eye_center(landmarks, [42, 43, 44, 45, 46, 47])
        
        gaze_x = (left_eye_center[0] + right_eye_center[0]) / 2
        gaze_y = (left_eye_center[1] + right_eye_center[1]) / 2
        
        screen_x, screen_y = map_gaze_to_screen(gaze_x, gaze_y, frame_width, frame_height, 1920, 1080)
        
        gaze_x_list.append(screen_x)
        gaze_y_list.append(screen_y)
        
        if len(gaze_x_list) > 500:
            gaze_x_list.pop(0)
            gaze_y_list.pop(0)
        
        heatmap, _, _ = np.histogram2d(gaze_y_list, gaze_x_list, bins=[100, 100], range=[[0, 1080], [0, 1920]])
        pcm.set_array(heatmap.T.ravel())
        plt.draw()
        plt.pause(0.01)
        
        # Draw circles at the eye centers
        cv2.circle(frame, left_eye_center, 5, (0, 255, 0), -1)
        cv2.circle(frame, right_eye_center, 5, (0, 255, 0), -1)
        cv2.circle(frame, (int(gaze_x), int(gaze_y)), 5, (255, 0, 0), -1)

    # Emotion detection and display
    for (x, y, w, h) in detected_faces:
        print(x, y, w, h)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        face = frame[y:y+h, x:x+w]
        result = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        cv2.putText(frame, dominant_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    # Display the frame with gaze tracking and emotion detection
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
plt.show()
