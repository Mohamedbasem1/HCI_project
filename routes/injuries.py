from flask import Blueprint, request, jsonify
from models.injury import injuries_collection
from models.exercise import exercises_collection
from bson import ObjectId

injuries_bp = Blueprint('injuries', __name__)

@injuries_bp.route('/api/injuries', methods=['GET'])
def get_injuries():
    try:
        injuries = list(injuries_collection.find({}, {'_id': 1, 'name': 1, 'exercises': 1}))
        for injury in injuries:
            injury['_id'] = str(injury['_id'])  # Convert ObjectId to string
            for exercise in injury.get('exercises', []):
                if isinstance(exercise, dict) and '_id' in exercise:
                    exercise['_id'] = str(exercise['_id'])  # Convert ObjectId to string in exercises
        print("Injuries fetched from DB:", injuries)  # Add this line to log the injuries
        return jsonify(injuries)
    except Exception as e:
        print("Error fetching injuries:", e)  # Add this line to log the error
        return jsonify({"error": str(e)}), 500

@injuries_bp.route('/api/injuries/test', methods=['GET'])
def test_get_injuries():
    try:
        injuries = list(injuries_collection.find({}, {'_id': 1, 'name': 1, 'exercises': 1}))
        for injury in injuries:
            injury['_id'] = str(injury['_id'])  # Convert ObjectId to string
            for exercise in injury.get('exercises', []):
                if isinstance(exercise, dict) and '_id' in exercise:
                    exercise['_id'] = str(exercise['_id'])  # Convert ObjectId to string in exercises
        print(injuries)  # Print the injuries to the console
        return jsonify(injuries)
    except Exception as e:
        print("Error fetching injuries:", e)  # Add this line to log the error
        return jsonify({"error": str(e)}), 500

@injuries_bp.route('/api/injuries', methods=['POST'])
def add_injury():
    try:
        data = request.json
        injuries_collection.insert_one(data)
        return jsonify({"message": "Injury added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@injuries_bp.route('/api/injuries/<injury_id>/exercises', methods=['POST'])
def add_exercise_to_injury(injury_id):
    try:
        exercise_id = request.json.get('exercise_id')
        result = injuries_collection.update_one(
            {'_id': ObjectId(injury_id)},
            {'$addToSet': {'exercises': exercise_id}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Injury not found"}), 404
        return jsonify({"message": "Exercise added to injury successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500