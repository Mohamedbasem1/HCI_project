import cv2
import mediapipe as mp
import pyautogui
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Capture video
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Smoothing variables
prev_x, prev_y = 0, 0
smooth_factor = 0.4
click_threshold = 0.04  # Threshold for thumb and index finger proximity

# Functions for gesture detection
def fingers_touching(thumb_tip, index_tip):
    distance = math.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
    return distance < click_threshold

def is_peace_sign(hand_landmarks):
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]

    is_index_extended = index_tip.y < index_mcp.y
    is_middle_extended = middle_tip.y < middle_mcp.y
    is_ring_folded = ring_tip.y > ring_mcp.y
    is_pinky_folded = pinky_tip.y > pinky_mcp.y
    is_thumb_folded = thumb_tip.x < thumb_ip.x

    return is_index_extended and is_middle_extended and is_ring_folded and is_pinky_folded and is_thumb_folded

def is_thumbs_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    thumb_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]

    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]

    is_thumb_extended = (thumb_tip.y < thumb_ip.y < thumb_mcp.y < thumb_cmc.y)
    are_other_fingers_not_extended = (
            index_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y and
            middle_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y and
            ring_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y and
            pinky_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y
    )

    return is_thumb_extended and are_other_fingers_not_extended

while True:
    # Read the frame
    success, frame = cap.read()
    if not success:
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert normalized coordinates to screen coordinates
            x_screen = int(index_tip.x * screen_width)
            y_screen = int(index_tip.y * screen_height)

            # Smooth cursor movement
            x_screen = int(prev_x + (x_screen - prev_x) * smooth_factor)
            y_screen = int(prev_y + (y_screen - prev_y) * smooth_factor)
            pyautogui.moveTo(x_screen, y_screen)
            prev_x, prev_y = x_screen, y_screen

            # Check if thumb and index fingertips are close enough to click
            if fingers_touching(thumb_tip, index_tip):
                pyautogui.click()
                print("Click triggered by finger touch")

            # Gesture detection
            if is_peace_sign(hand_landmarks):
                print("Peace sign detected!")
            elif is_thumbs_up(hand_landmarks):
                print("Thumbs up detected!")

    # Display the video feed (comment this line to make the camera silent)
    # cv2.imshow("Hand Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
