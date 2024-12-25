import mediapipe as mp

mp_hands = mp.solutions.hands

def count_fingers(hand_landmarks):
    fingers = [False] * 5
    tips = [mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.INDEX_FINGER_TIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_TIP,
            mp_hands.HandLandmark.PINKY_TIP]
    dips = [mp_hands.HandLandmark.THUMB_IP, mp_hands.HandLandmark.INDEX_FINGER_DIP,
            mp_hands.HandLandmark.MIDDLE_FINGER_DIP, mp_hands.HandLandmark.RING_FINGER_DIP,
            mp_hands.HandLandmark.PINKY_DIP]

    for i in range(5):
        if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[dips[i]].y:
            fingers[i] = True

    return sum(fingers)