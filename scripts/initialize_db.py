from pymongo import MongoClient

def initialize_db():
    client = MongoClient('mongodb+srv://mostafaahesham12:TtqslmSrekYVVjzy@hci.xfv9n.mongodb.net/recovery_hub?retryWrites=true&w=majority&appName=Hci')  # Replace with your actual connection string
    db = client['recovery_hub']
    injuries_collection = db['injuries']

    # Define the injuries data
    injuries_data = [
    {
        "name": "ACL Injury",
        "exercises": [
            {
                "name": "Band-Assisted Heel Slides",
                "description": "Assist knee mobility by gently pulling the band to slide the heel.",
                "video_url": "videos/heel-slides-with-strap.mp4",  # Local path
                "default_sets": 3,
                "default_reps": 10
            },
            {
                "name": "Static Quad Contractions",
                "description": "Tighten the thigh muscle against band resistance without moving the leg.",
                "video_url": "videos/vmo-static-quadricep.mp4",  # Local path
                "default_sets": 3,
                "default_reps": 15
            }
        ]
    },
    {
        "name": "Hamstring Strain",
        "exercises": [
            {
                "name": "Standing Hamstring Curl (Single Leg)",
                "description": "Perform this exercise by standing and curling one leg at a time with a resistance band looped around the ankle to strengthen the hamstrings effectively.",
                "video_url": "videos/hamstring-exercise-standing-hamstring-curl-single-leg.mp4",  # Local path
                "default_sets": 4,
                "default_reps": 12
            }
        ]
    },
    {
        "name": "Achilles Tendinopathy",
        "exercises": [
            {
                "name": "Resistance Band Plantar Flexions",
                "description": "Press foot down against the band's resistance to strengthen the Achilles tendon and calf muscles.",
                "video_url": "videos/ankle-strengthening-with-resisted-plantar.mp4",  # Local path
                "default_sets": 3,
                "default_reps": 15
            }
        ]
    },
    {
        "name": "General Leg Weakness",
        "exercises": [
            {
                "name": "Resistance Band Leg Presses",
                "description": "Lie back, press legs outward against band resistance, mimicking a leg press machine.",
                "video_url": "videos/leg-press-with-resistance-band-your-exercise.mp4",  # Local path
                "default_sets": 3,
                "default_reps": 10
            },
            {
                "name": "Seated Band Leg Extensions",
                "description": "Extend leg against band resistance to strengthen quadriceps.",
                "video_url": "videos/Exercise Videos- Band Leg Extension -- Seated.mp4",  # Local path
                "default_sets": 3,
                "default_reps": 15
            }
        ]
    }
]



    # Clear existing data and insert new data
    injuries_collection.delete_many({})
    injuries_collection.insert_many(injuries_data)
    print("Database initialized with injuries and exercises.")

if __name__ == "__main__":
    initialize_db()
