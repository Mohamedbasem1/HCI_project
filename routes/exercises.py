from flask import Blueprint, request, jsonify
from models.exercise import exercises_collection

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route('/api/exercises', methods=['GET'])
def get_exercises():
    exercises = list(exercises_collection.find({}, {'_id': 0}))
    return jsonify(exercises)

@exercises_bp.route('/api/exercises', methods=['POST'])
def add_exercise():
    try:
        data = request.json
        exercises_collection.insert_one(data)
        return jsonify({"message": "Exercise added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500