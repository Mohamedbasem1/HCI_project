import cv2
import mediapipe as mp
from src.pose_estimation import get_angles
from src.save_data import save_data, load_data
from src.exercise_evaluator import evaluate_exercise
from src.frame_extractor import extract_frames

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def is_peace_sign(hand_landmarks):
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]  # Corrected attribute
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]

    # Check if index and middle fingers are extended
    is_index_extended = index_tip.y < index_mcp.y
    is_middle_extended = middle_tip.y < middle_mcp.y

    # Check if ring and pinky fingers are not extended
    is_ring_folded = ring_tip.y > ring_mcp.y
    is_pinky_folded = pinky_tip.y > pinky_mcp.y

    # Check if thumb is not extended
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

    # Check if thumb is extended
    is_thumb_extended = (thumb_tip.y < thumb_ip.y < thumb_mcp.y < thumb_cmc.y)

    # Check if other fingers are not extended
    are_other_fingers_not_extended = (
            index_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y and
            middle_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y and
            ring_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y and
            pinky_mcp.y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y
    )

    return is_thumb_extended and are_other_fingers_not_extended


def capture_webcam_video():
    cap = cv2.VideoCapture(0)
    frames = []
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if is_thumbs_up(hand_landmarks):
                        cap.release()
                        cv2.destroyAllWindows()
                        return frames
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.imshow('Webcam', frame)
            frames.append(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()
    return frames


def main():
    # Step 1: Extract and Calculate Angles for Reference Video
    reference_video_path = 'videos/ref1.mp4'
    reference_frames = extract_frames(reference_video_path)
    reference_angles = get_angles(reference_frames)
    save_data(reference_angles, 'data/reference_angles.npy')

    # Step 2: Load Data
    reference_angles = load_data('data/reference_angles.npy')

    # Step 3: Capture and Process Webcam Video in Real-time
    user_frames = capture_webcam_video()
    user_angles = get_angles(user_frames)
    save_data(user_angles, 'data/user_angles.npy')

    # Step 4: Load Data and Evaluate
    user_angles = load_data('data/user_angles.npy')
    score = evaluate_exercise(reference_angles, user_angles)

    # Step 5: Display Match Score
    if user_frames:
        last_frame = user_frames[-1]
        cv2.putText(last_frame, f'Match score: {score:.2f}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Webcam', last_frame)
        cv2.waitKey(0)  # Pause the video
        cv2.destroyAllWindows()

    print(f'User exercise match score: {score}')


if __name__ == '__main__':
    main()
