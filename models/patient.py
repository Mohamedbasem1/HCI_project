from db import db

patients_collection = db.patients

# Example patient document structure
# {
#     "_id": "unique_patient_id",
#     "name": "Patient Name",
#     "injury": "Injury Name",
#     "exercises": [
#         {
#             "exercise_id": "unique_exercise_id",
#             "sets": 3,
#             "reps": 10
#         }
#     ]
# }