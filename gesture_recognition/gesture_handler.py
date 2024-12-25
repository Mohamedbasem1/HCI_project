import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom operations

import cv2
import mediapipe as mp
from flask_socketio import SocketIO
import numpy as np
from .gesture_smoother import GestureSmoother
from .gesture_analyzer import GestureAnalyzer

class GestureHandler:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.gesture_smoother = GestureSmoother()
        self.gesture_analyzer = GestureAnalyzer()
        self.is_running = False

    def start(self):
        """Start gesture recognition"""
        self.is_running = True
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("Error: Could not open video capture")
            return
        
        print("Gesture recognition started")
        
        while self.is_running and cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Error: Could not read frame")
                continue

            processed_frame = self.process_frame(frame)
            cv2.imshow('Hand Gestures', processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Gesture recognition stopped")

    def stop(self):
        """Stop gesture recognition"""
        self.is_running = False

    def process_frame(self, frame):
        """Process a single frame for hand gestures"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Analyze gesture
                gesture = self.gesture_analyzer.analyze(hand_landmarks)
                
                # Smooth gesture
                smoothed_gesture = self.gesture_smoother.smooth_gesture(gesture)
                
                # Emit gesture event
                if smoothed_gesture != "unknown":
                    self.socketio.emit('gesture_event', {'gesture': smoothed_gesture})
                
                # Draw landmarks
                self.mp_draw.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    self.mp_hands.HAND_CONNECTIONS
                )

        return frame