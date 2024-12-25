import cv2
import mediapipe as mp
import numpy as np
from flask_socketio import SocketIO
import threading
import time
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations

class GestureService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.is_running = False
        self.thread = None
        self.last_gesture = None
        self.gesture_cooldown = 1.0  # Cooldown in seconds
        self.last_gesture_time = 0

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._gesture_recognition_loop)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()

    def _gesture_recognition_loop(self):
        cap = cv2.VideoCapture(0)
        
        while self.is_running:
            success, frame = cap.read()
            if not success:
                continue

            gesture = self._process_frame(frame)
            if gesture and self._check_cooldown():
                self.socketio.emit('gesture_event', {'gesture': gesture})
                self.last_gesture = gesture
                self.last_gesture_time = time.time()

        cap.release()

    def _process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                return self._analyze_gesture(hand_landmarks)
        return None

    def _analyze_gesture(self, landmarks):
        # Get key points
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        wrist = landmarks.landmark[0]

        # Thumbs up/down detection
        if abs(thumb_tip.x - index_tip.x) > 0.1:
            if thumb_tip.y < index_tip.y:
                print("a3laaaaaaa")
                return "thumbs_up"
            elif thumb_tip.y > index_tip.y:
                print("taaaaaaa7t")
                return "thumbs_down"

        # Swipe detection
        if abs(index_tip.x - wrist.x) > 0.3:
            if index_tip.x > wrist.x:
                return "swipe_right"
            else:
                return "swipe_left"

        return None

    def _check_cooldown(self):
        """Prevent rapid-fire gesture detection"""
        return time.time() - self.last_gesture_time > self.gesture_cooldown