import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId
from config import Config
import sys
import os
import random
import string
# import bluetooth
import asyncio
import aiohttp
import subprocess
import sys  # Add this import
import requests  # Add this import

sys.path.append(os.path.join(os.path.dirname(__file__), 'routes'))  # Add this line

from routes.patients import patients_bp  # Import the blueprint
from routes.injuries import injuries_bp
from routes.exercises import exercises_bp
from gesture_recognition.gesture_routes import init_gesture_handler, gesture_bp  # Add this import

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Add UPLOAD_FOLDER configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# MongoDB connection
client = MongoClient('mongodb+srv://mostafaahesham12:TtqslmSrekYVVjzy@hci.xfv9n.mongodb.net/recovery_hub?retryWrites=true&w=majority&appName=Hci')
db = client['recovery_hub']
patients_collection = db['patients']
doctors_collection = db['doctors']  # Add doctors collection
injuries_collection = db['injuries']
exercises_collection = db['exercises']

def test_db_connection():
    try:
        print("Attempting to connect to the database...")
        collections = db.list_collection_names()
        print("Connected to the database. Collections:", collections)
    except Exception as e:
        print("Failed to connect to the database:", e)

def generate_random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

def generate_unique_tuio_id():
    existing_ids = set(patients_collection.distinct("tuio_id"))
    tuio_id = 50
    while tuio_id in existing_ids:
        tuio_id += 1
    return tuio_id

# Initialize gesture handler
init_gesture_handler(socketio)

# Register Blueprints
app.register_blueprint(patients_bp, url_prefix='/api')  # Register with URL prefix
app.register_blueprint(injuries_bp)
app.register_blueprint(exercises_bp)
app.register_blueprint(gesture_bp, url_prefix='/gesture')  # Register gesture blueprint

# Serve video files
@app.route('/videos/<path:filename>')
def serve_video(filename):
    video_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
    return send_from_directory(video_directory, filename)

# Handle rotation events
@app.route('/tuio_rotation', methods=['POST'])
def handle_rotation():
    data = request.json
    rotation_direction = data.get('rotationDirection')
    print(f"Received rotation event: {rotation_direction}")
    socketio.emit('rotate_event', {'direction': rotation_direction})
    return jsonify({"status": "success"}), 200

# Handle click events
@app.route('/tuio_click', methods=['POST'])
def handle_click():
    print("Received click event")
    socketio.emit('click_event')
    return jsonify({"status": "success"}), 200

@app.route('/api/patients/login', methods=['POST'])
def patient_login():
    data = request.json
    tuio_id = int(data.get('tuio_id'))  # Ensure TUIO ID is treated as an integer
    patient = patients_collection.find_one({"tuio_id": tuio_id})
    if patient:
        patient['_id'] = str(patient['_id'])  # Convert ObjectId to string
        # Start gesture recognition
        response = requests.post('http://localhost:5000/gesture/start')
        print(f"Gesture recognition start response: {response.json()}")  # Add debugging statement
        return jsonify({"success": True, "patient": patient}), 200
    else:
        return jsonify({"success": False, "message": "Invalid TUIO ID"}), 401

@app.route('/api/doctors/login', methods=['POST'])
def doctor_login():
    data = request.json
    tuio_id = data.get('tuio_id')
    doctor = doctors_collection.find_one({"tuio_id": tuio_id})
    if doctor:
        doctor['_id'] = str(doctor['_id'])  # Convert ObjectId to string
        # Start gesture recognition
        response = requests.post('http://localhost:5000/gesture/start')
        print(f"Gesture recognition start response: {response.json()}")  # Add debugging statement
        return jsonify({"success": True, "doctor": doctor}), 200
    else:
        return jsonify({"success": False, "message": "Invalid TUIO ID"}), 401

@app.route('/api/patients/<patient_id>/exercises', methods=['GET'])
def get_patient_exercises(patient_id):
    try:
        patient = patients_collection.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        injury = injuries_collection.find_one({"name": patient['injury']})
        if not injury:
            return jsonify({"error": "Injury not found"}), 404
        exercises = injury.get('exercises', [])
        return jsonify(exercises), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_exercise_video', methods=['POST'])
def upload_exercise_video():
    # Call the new function before uploading the video
    try:
        result = subprocess.run(['python', 'knee_flex.py'], capture_output=True, text=True, timeout=60)
        output = result.stdout.strip()
        return jsonify({"message": "Exercise completed successfully", "output": output}), 200
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Exercise timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patient/plan', methods=['GET'])
def get_patient_plan():
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400
    try:
        patient = patients_collection.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        patient['_id'] = str(patient['_id'])  # Convert ObjectId to string
        return jsonify(patient), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tuio_ids', methods=['GET'])
def get_tuio_ids():
    patient_ids = patients_collection.distinct("tuio_id")
    doctor_ids = doctors_collection.distinct("tuio_id")
    return jsonify(patient_ids + doctor_ids), 200

@app.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.json
    name = data.get('name', generate_random_name())
    tuio_id = data.get('tuio_id', generate_unique_tuio_id())
    if tuio_id < 50 or patients_collection.find_one({"tuio_id": tuio_id}):
        return jsonify({"error": "Invalid or duplicate TUIO ID"}), 400
    patient = {
        "name": name,
        "tuio_id": tuio_id,
        "injury": data["injury"],
        "exercises": data["exercises"]
    }
    result = patients_collection.insert_one(patient)
    patient['_id'] = str(result.inserted_id)
    return jsonify(patient), 201

@app.route('/api/generate_patient_details', methods=['GET'])
def generate_patient_details_route():
    return generate_patient_details()


@app.route('/')
def index():
    return "TUIO Server Running"


# Store received TUIO IDs
received_tuio_ids = set()

@app.route('/api/tuio_event', methods=['POST'])
def tuio_event():
    data = request.json
    tuio_id = data.get('tuio_id')
    if tuio_id:
        received_tuio_ids.add(tuio_id)
        print(f'Received TUIO ID: {tuio_id}')
        socketio.emit('tuio_event', {'tuio_id': tuio_id})
    return jsonify({"status": "success"}), 200

@app.route('/api/verify_tuio_id', methods=['POST'])
def verify_tuio_id():
    data = request.json
    tuio_id = data.get('tuio_id')
    if tuio_id in received_tuio_ids:
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False}), 400

@app.route('/api/marker_event', methods=['POST'])
def handle_marker_event():
    data = request.json
    marker_id = int(data.get('marker_id'))
    print(f"Received marker ID: {marker_id}")
    
    # Check if there is a patient with the corresponding TUIO ID
    patient = patients_collection.find_one({"tuio_id": marker_id})
    if patient:
        patient['_id'] = str(patient['_id'])  # Convert ObjectId to string
        print(f"Emitting login_event for patient: {patient}")  # Add this line for debugging
        socketio.emit('login_event', {'patient': patient})
        return jsonify({"status": "success", "patient": patient}), 200
    else:
        return jsonify({"status": "error", "message": "No matching patient found"}), 404

@app.route('/api/bluetooth_device', methods=['POST'])
def handle_bluetooth_device():
    data = request.json
    addr = data.get('address')
    name = data.get('name')
    print(f"Received Bluetooth device: {addr} - {name}")
    
    # Check if the Bluetooth address matches the doctor's address
    if addr == "54:9A:8F:4B:C4:7A":
        print(f"Emitting redirect_event for doctor: {addr}")  # Add this line for debugging
        socketio.emit('redirect_event', {'url': 'http://localhost:3000/doctor'})
        return jsonify({"status": "success", "message": "Redirecting to doctor dashboard"}), 200
    else:
        return jsonify({"status": "error", "message": "No matching doctor found"}), 404

@app.route('/api/start_exercise', methods=['POST'])
def start_exercise(): 
     try:
        # Specify the Python executable from the virtual environment
        python_executable = r'.venv\Scripts\python.exe'
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knee_flex.py')
        environment_vars = os.environ
        print(f"Python executable: {python_executable}")
        print(f"Script path: {script_path}")
        print(f"Environment variables: {environment_vars}")

        # Start the knee_flex.py script and keep it running
        process = subprocess.Popen([python_executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            output = stdout.decode('utf-8')
            print(f"Exercise output: {output}")
            return jsonify({"status": "success", "message": "Exercise started", "output": output}), 200
        else:
            error_message = stderr.decode('utf-8')
            print(f"Error starting exercise: {error_message}")
            return jsonify({"status": "error", "message": "Exercise failed", "output": error_message}), 500
     except Exception as e:
        print(f"Exception starting exercise: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/face_login', methods=['POST'])
def face_login():
    try:
        print("Starting face recognition script...")  # Add this line for debugging
        print(f"Python executable: {sys.executable}")  # Add this line for debugging
        print(f"Python version: {sys.version}")  # Add this line for debugging
        result = subprocess.run([sys.executable, 'face.py'], capture_output=True, text=True, timeout=60)
        print(f"Face recognition script output: {result.stdout}")  # Add this line for debugging
        print(f"Face recognition script error output: {result.stderr}")  # Add this line for debugging
        output_lines = result.stdout.strip().split("\n")
        recognized_name = output_lines[-1].split(": ")[-1] if output_lines else "Unknown"
        print(f"Recognized name: {recognized_name}")  # Add this line for debugging
        if recognized_name == "Unknown":
            return jsonify({"success": False, "message": "Face not recognized"}), 401
        patient = patients_collection.find_one({"name": recognized_name})
        if patient:
            patient['_id'] = str(patient['_id'])  # Convert ObjectId to string
            return jsonify({"success": True, "patient": patient}), 200
        else:
            return jsonify({"success": False, "message": "Face not recognized"}), 401
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Face recognition timed out"}), 500
    except Exception as e:
        print(f"Error during face login: {e}")  # Add this line for debugging
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

async def send_bluetooth_device(addr, name):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/api/bluetooth_device', json={'address': addr, 'name': name}) as response:
            print(f"Sent Bluetooth device: {addr} - {name} to server, response: {response.status}")

async def discover_bluetooth_devices():
    while True:
        print("Discovering nearby Bluetooth devices...")
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        print(f"Found {len(nearby_devices)} devices")

        for addr, name in nearby_devices:
            print(f" {addr} - {name}")
            await send_bluetooth_device(addr, name)

if __name__ == '__main__':
    print("Starting the Flask server...")  # Add this line for debugging
    socketio.run(app, debug=True)