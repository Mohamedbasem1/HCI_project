from flask import Blueprint, request, jsonify, current_app
from models.patient import patients_collection
from models.injury import injuries_collection
from bson import ObjectId
import random
import os
from werkzeug.utils import secure_filename

patients_bp = Blueprint('patients', __name__)

def generate_random_name():
    names = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Hannah', 'Ivy', 'Jack']
    return random.choice(names)

def generate_unique_tuio_id():
    existing_ids = set(patients_collection.distinct("tuio_id"))
    tuio_id = 50
    while tuio_id in existing_ids:
        tuio_id += 1
    return tuio_id

def generate_patient_details():
    name = generate_random_name()
    tuio_id = generate_unique_tuio_id()
    return jsonify({"name": name, "tuio_id": tuio_id}), 200

@patients_bp.route('/generate_patient_details', methods=['GET'])
def generate_patient_details_route():
    return generate_patient_details()

@patients_bp.route('/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'GET':
        try:
            patients = list(patients_collection.find({}, {'_id': 1, 'name': 1, 'injury': 1, 'exercises': 1, 'tuio_id': 1, 'type': 1}))  # Include type field
            for patient in patients:
                patient['_id'] = str(patient['_id'])  # Convert ObjectId to string
                for exercise in patient.get('exercises', []):
                    if isinstance(exercise, dict) and '_id' in exercise:
                        exercise['_id'] = str(exercise['_id'])  # Convert ObjectId to string in exercises
            return jsonify(patients)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            name = data.get('name', generate_random_name())
            tuio_id = int(data.get('tuio_id', generate_unique_tuio_id()))
            injury = data.get('injury')
            exercises = data.get('exercises').split(',')
            patient_type = data.get('type')  # Get patient type

            if tuio_id < 50 or patients_collection.find_one({"tuio_id": tuio_id}):
                return jsonify({"error": "Invalid or duplicate TUIO ID"}), 400

            # Handle image upload
            if 'image' not in request.files:
                return jsonify({"error": "No image file provided"}), 400
            image = request.files['image']
            if image.filename == '':
                return jsonify({"error": "No selected file"}), 400
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            # Ensure exercises are stored as a list of dictionaries
            exercises_list = [{"name": ex} for ex in exercises]

            patient = {
                "name": name,
                "tuio_id": tuio_id,
                "injury": injury,
                "exercises": exercises_list,
                "image_path": image_path,  # Save image path in the database
                "type": patient_type  # Save patient type in the database
            }
            result = patients_collection.insert_one(patient)
            patient['_id'] = str(result.inserted_id)
            return jsonify(patient), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@patients_bp.route('/patients/<patient_id>', methods=['PUT', 'DELETE'])
def update_or_delete_patient(patient_id):
    if request.method == 'PUT':
        try:
            data = request.json
            result = patients_collection.update_one({'_id': ObjectId(patient_id)}, {'$set': data})
            if result.matched_count == 0:
                return jsonify({"error": "Patient not found"}), 404
            updated_patient = patients_collection.find_one({'_id': ObjectId(patient_id)}, {'_id': 1, 'name': 1, 'injury': 1, 'exercises': 1, 'code': 1, 'tuio_id': 1})
            updated_patient['_id'] = str(updated_patient['_id'])  # Convert ObjectId to string
            return jsonify(updated_patient), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == 'DELETE':
        try:
            result = patients_collection.delete_one({'_id': ObjectId(patient_id)})
            if result.deleted_count == 0:
                return jsonify({"error": "Patient not found"}), 404
            return jsonify({"message": "Patient deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@patients_bp.route('/patients/<patient_id>/exercises', methods=['GET'])
def get_patient_exercises(patient_id):
    try:
        patient = patients_collection.find_one({"_id": ObjectId(patient_id)})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        injury = injuries_collection.find_one({"name": patient['injury']})
        if not injury:
            return jsonify({"error": "Injury not found"}), 404
        # Filter exercises based on the patient's assigned exercises
        assigned_exercises = {ex['name']: ex for ex in patient['exercises']}
        filtered_exercises = []
        for ex in injury['exercises']:
            if ex['name'] in assigned_exercises:
                filtered_exercise = {
                    'name': ex['name'],
                    'description': ex['description'],
                    'video_url': ex['video_url'],
                    'sets': assigned_exercises[ex['name']]['sets'],
                    'reps': assigned_exercises[ex['name']]['reps'],
                    'default_sets': ex['default_sets'],
                    'default_reps': ex['default_reps']
                }
                filtered_exercises.append(filtered_exercise)
        return jsonify(filtered_exercises), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

