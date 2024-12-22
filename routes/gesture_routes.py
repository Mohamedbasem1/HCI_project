from flask import Blueprint, jsonify
from flask_socketio import SocketIO
from gesture_recognition.gesture_handler import GestureHandler

gesture_bp = Blueprint('gesture', __name__)
gesture_handler = None

def init_gesture_handler(socketio: SocketIO):
    global gesture_handler
    gesture_handler = GestureHandler(socketio)

@gesture_bp.route('/start', methods=['POST'])
def start_gesture_recognition():
    try:
        if gesture_handler:
            gesture_handler.start()
            return jsonify({"status": "success", "message": "Gesture recognition started"}), 200
        return jsonify({"error": "Gesture handler not initialized"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@gesture_bp.route('/stop', methods=['POST'])
def stop_gesture_recognition():
    try:
        if gesture_handler:
            gesture_handler.stop()
            return jsonify({"status": "success", "message": "Gesture recognition stopped"}), 200
        return jsonify({"error": "Gesture handler not initialized"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500