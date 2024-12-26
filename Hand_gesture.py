import cv2
import mediapipe as mp
from dollarpy import Recognizer, Template, Point
import csv
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Load gesture templates from a CSV fileq
def load_templates_from_csv(csv_file_path):
    loaded_templates = []
    current_gesture = None
    current_points = []

    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        for row in reader:
            gesture_name, point_index, x, y = row[0], int(row[1]), float(row[2]), float(row[3])
            point = Point(x, y)

            if current_gesture != gesture_name:
                if current_gesture is not None:
                    loaded_templates.append(Template(current_gesture, current_points))
                current_gesture = gesture_name
                current_points = [point]
            else:
                current_points.append(point)

        # Add the last gesture template
        if current_gesture is not None:
            loaded_templates.append(Template(current_gesture, current_points))

    print("Templates loaded from CSV:", len(loaded_templates))
    return loaded_templates

# Path to the CSV file with gesture templates
csv_file_path = 'gesture.csv'
loaded_templates = load_templates_from_csv(csv_file_path)
recognizer = Recognizer(loaded_templates)

# Recognize gestures from the video in real-time
def recognize_in_real_time():
    cap = cv2.VideoCapture(0)  # Use webcam
    all_points = []

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            recognized_gesture = "No Gesture"
            score = None

            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                points = [Point(hand_landmarks.landmark[i].x, hand_landmarks.landmark[i].y) for i in range(21)]
                all_points = points

                # Perform recognition on the current frame
                if all_points:
                    start_time = time.time()
                    result = recognizer.recognize(all_points)
                    end_time = time.time()

                    if result and isinstance(result[0], Template):
                        recognized_gesture = result[0].name
                        score = f"Score: {result[0].score:.2f}"
                    elif result:
                        recognized_gesture = result

            # Draw landmarks on the frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Display recognized gesture on the frame
            cv2.putText(frame, f"Gesture: {recognized_gesture}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            if score:
                cv2.putText(frame, score, (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Display the video feed
            cv2.imshow("Real-Time Gesture Recognition", frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):  # Press 'q' to quit
                break

    cap.release()
    cv2.destroyAllWindows()

# Run the real-time gesture recognition
recognize_in_real_time()
