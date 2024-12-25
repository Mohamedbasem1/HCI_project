from db import db

injuries_collection = db.injuries

# Example injury document structure
# {
#     "_id": "unique_injury_id",
#     "name": "Leg Injury",
#     "description": "Description of the injury",
#     "exercises": ["exercise_id_1", "exercise_id_2"]
# }