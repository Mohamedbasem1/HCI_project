import cv2
import numpy as np
import time
import pyautogui
import mediapipe as mp
from deepface import DeepFace  # type: ignore

cap = cv2.VideoCapture(1)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

light_pattern = []
finger_positions = []

# Initialize the laser_detected flag
laser_detected = False
laser_positions = []  # Track laser positions over time

while(1):
    flag , background = cap.read()

    hsv_frame = cv2.cvtColor(background, cv2.COLOR_BGR2HSV)

    red_lower = np.array([170, 200, 175])
    red_upper = np.array([180, 255, 255])
    red_mask = cv2.inRange(hsv_frame, red_lower, red_upper)

    red_color = cv2.bitwise_and(background, background, mask=red_mask)

    detected_edges, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Check if laser is detected
    if detected_edges:
        laser_detected = True
        # Process laser detection
        largest_contour = max(detected_edges, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        current_time = time.time()
        light_pattern.append((x, y, current_time))

        new_light_pattern = []
        for px, py, t in light_pattern:
            if current_time - t <= 5:  # 5 sec and delete the pattern 
                new_light_pattern.append((px, py, t))
        light_pattern = new_light_pattern

        for i in range(1, len(light_pattern)):
            cv2.line(background, (light_pattern[i-1][0], light_pattern[i-1][1]), (light_pattern[i][0], light_pattern[i][1]), (255, 0, 0), 2)

        cv2.rectangle(background, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        cv2.putText(background, f"({x}, {y})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)  

        # Move the mouse cursor to the position of the red color
        screen_width, screen_height = pyautogui.size()
        frame_height, frame_width, _ = background.shape
        mouse_x = screen_width - int((x + w / 2) * screen_width / frame_width)
        mouse_y = int((y + h / 2) * screen_height / frame_height)
        pyautogui.moveTo(mouse_x, mouse_y)

        # Track the laser position over time
        laser_positions.append((x, y, current_time))

        # Remove old positions
        new_laser_positions = []
        for px, py, t in laser_positions:
            if current_time - t <= 5:  # 5 seconds threshold
                new_laser_positions.append((px, py, t))
        laser_positions = new_laser_positions

        if len(laser_positions) > 0:
            initial_x, initial_y, initial_time = laser_positions[0]
            if all(np.sqrt((px - initial_x) ** 2 + (py - initial_y) ** 2) < 20 for px, py, t in laser_positions):  # Adjust the threshold as needed
                if current_time - initial_time >= 3:  # 3 seconds threshold for left click
                    print("Left click triggered by laser")
                    pyautogui.click()  # Trigger left click
                    laser_positions.clear()  # Clear positions after left-click

    else:
        laser_detected = False
        light_pattern.clear()
        laser_positions.clear()

    # Convert the frame to RGB
    rgb_frame = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # Only execute the finger function if no laser is detected
    if not laser_detected and result.multi_hand_landmarks:
        # Process only the first detected hand
        hand_landmarks = result.multi_hand_landmarks[0]
        # Get the tip of the index finger
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        frame_height, frame_width, _ = background.shape
        x = int(index_finger_tip.x * frame_width)
        y = int(index_finger_tip.y * frame_height)
        
        # Invert the x-coordinate for left-right inversion
        screen_width, screen_height = pyautogui.size()
        mouse_x = screen_width - int(index_finger_tip.x * screen_width)
        mouse_y = int(index_finger_tip.y * screen_height)
        pyautogui.moveTo(mouse_x, mouse_y)
        
        # Track the finger position over time
        current_time = time.time()
        finger_positions.append((x, y, current_time))
        
        # Remove old positions
        new_finger_positions = []
        for px, py, t in finger_positions:
            if current_time - t <= 5:  # 5 seconds threshold
                new_finger_positions.append((px, py, t))
        finger_positions = new_finger_positions
        
        if len(finger_positions) > 0:
            initial_x, initial_y, initial_time = finger_positions[0]
            if all(np.sqrt((px - initial_x) ** 2 + (py - initial_y) ** 2) < 20 for px, py, t in finger_positions):  # Adjust the threshold as needed
                if current_time - initial_time >= 3:  # 3 seconds threshold for left click
                    print("Left click triggered")
                    pyautogui.click()  # Trigger left click
                    finger_positions.clear()  # Clear positions after left-click

        mp_draw.draw_landmarks(background, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Emotion detection and display
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) > 0:  # Ensure that there is at least one face detected
        for (x, y, w, h) in faces:
            # Draw rectangle around the face
            cv2.rectangle(background, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Crop the face region from the frame
            face = background[y:y+h, x:x+w]

            # Analyze the emotion of the face using DeepFace (no need to load a custom model)
            result = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)

            # Get the dominant emotion
            dominant_emotion = result[0]['dominant_emotion']

            # Display the emotion text on the frame
            cv2.putText(background, dominant_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    cv2.imshow("Original Image", background)
    cv2.imshow("Red Color", red_color)

    k = cv2.waitKey(5)

    if k == ord('q'):
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
