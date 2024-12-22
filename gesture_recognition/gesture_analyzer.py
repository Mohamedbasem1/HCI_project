class GestureAnalyzer:
    def __init__(self):
        # Define gesture thresholds and configurations
        self.gestures = {
            "thumbs_up": self._check_thumbs_up,
            "thumbs_down": self._check_thumbs_down,
            "swipe_right": self._check_swipe_right,
            "swipe_left": self._check_swipe_left,
            # Add more gestures as needed
        }

    def analyze(self, landmarks):
        """Analyze hand landmarks and return detected gesture"""
        for gesture_name, check_func in self.gestures.items():
            if check_func(landmarks):
                return gesture_name
        return "unknown"

    def _check_thumbs_up(self, landmarks):
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        return thumb_tip.y < index_tip.y

    def _check_thumbs_down(self, landmarks):
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        return thumb_tip.y > index_tip.y

    def _check_swipe_right(self, landmarks):
        wrist = landmarks.landmark[0]
        index_tip = landmarks.landmark[8]
        return index_tip.x - wrist.x > 0.3

    def _check_swipe_left(self, landmarks):
        wrist = landmarks.landmark[0]
        index_tip = landmarks.landmark[8]
        return wrist.x - index_tip.x > 0.3