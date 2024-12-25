class GestureSmoother:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.gesture_history = []
    
    def smooth_gesture(self, gesture):
        """Smooth gestures over time to reduce jitter"""
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > self.window_size:
            self.gesture_history.pop(0)
        
        if self.gesture_history:
            return max(set(self.gesture_history), key=self.gesture_history.count)
        return gesture