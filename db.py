from pymongo import MongoClient

client = MongoClient('mongodb+srv://mostafaahesham12:TtqslmSrekYVVjzy@hci.xfv9n.mongodb.net/recovery_hub?retryWrites=true&w=majority&appName=Hci')
db = client['recovery_hub']

def test_db_connection():
    try:
        print("Attempting to connect to the database...")
        # Attempt to list the collections in the database
        collections = db.list_collection_names()
        print("Connected to the database. Collections:", collections)
    except Exception as e:
        print("Failed to connect to the database:", e)