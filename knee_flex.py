import cv2
import mediapipe as mp
import math
import time

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    angle = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) -
                         math.atan2(a[1] - b[1], a[0] - b[0]))
    return abs(angle) if abs(angle) <= 180 else 360 - abs(angle)

# Thresholds for correct flexion and extension
FLEXION_THRESHOLD = 90  # Knee flexion angle (less than this is a correct flexion)
EXTENSION_THRESHOLD = 170  # Knee extension angle (close to this is a correct extension)

# Start video capture
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# Counters for correct gestures
left_knee_count = 0
right_knee_count = 0
left_was_flexed = False  # Track state of left knee flexion
right_was_flexed = False  # Track state of right knee flexion

start_time = time.time()

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read from camera.")
            break

        # Convert frame to RGB for MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # Get frame dimensions
        h, w, _ = frame.shape

        # Check for detected landmarks
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Extract keypoints for left and right knees, hips, and ankles
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h]

            right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x * w,
                         landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y * h]
            right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * w,
                          landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * h]
            right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x * w,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y * h]

            # Calculate knee angles
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

            # Display angles on screen
            cv2.putText(frame, f"Left Knee: {int(left_knee_angle)}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cv2.putText(frame, f"Right Knee: {int(right_knee_angle)}", (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Check left knee gesture (flexion and extension cycle)
            if left_knee_angle < FLEXION_THRESHOLD:  # Detect flexion
                if not left_was_flexed:
                    left_knee_count += 1
                    left_was_flexed = True
            elif left_knee_angle > EXTENSION_THRESHOLD:  # Detect extension
                left_was_flexed = False  # Reset state after full extension

            # Check right knee gesture (flexion and extension cycle)
            if right_knee_angle < FLEXION_THRESHOLD:  # Detect flexion
                if not right_was_flexed:
                    right_knee_count += 1
                    right_was_flexed = True
            elif right_knee_angle > EXTENSION_THRESHOLD:  # Detect extension
                right_was_flexed = False  # Reset state after full extension

        else:
            cv2.putText(frame, "Detecting key points...", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Display the success counts
        cv2.putText(frame, f"Left Knee Count: {left_knee_count}", (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.putText(frame, f"Right Knee Count: {right_knee_count}", (10, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Check if 30 seconds have passed
        if time.time() - start_time > 30:
            break

        # Display the frame
        cv2.imshow("Knee Gesture Tracker", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print(f"Left Knee Count: {left_knee_count}")
    print(f"Right Knee Count: {right_knee_count}")