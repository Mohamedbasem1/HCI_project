import cv2
import face_recognition
from pymongo import MongoClient
import os

# MongoDB connection
try:
    client = MongoClient('mongodb+srv://mostafaahesham12:TtqslmSrekYVVjzy@hci.xfv9n.mongodb.net/recovery_hub?retryWrites=true&w=majority&appName=Hci')
    db = client['recovery_hub']
    patients_collection = db['patients']
    print("Successfully connected to the database")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    exit(1)

# Create arrays of known face encodings and their names
known_face_encodings = []
known_face_names = []

# Load known faces and their names from the database
for patient in patients_collection.find():
    name = patient['name']
    if 'image_path' in patient:
        image_path = patient['image_path']
        
        # Load the image file
        if os.path.exists(image_path):
            image = cv2.imread(image_path)  # Load the image using OpenCV
            
            # Convert the image from BGR to RGB (OpenCV loads images in BGR by default)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Get the face encoding
            face_encoding = face_recognition.face_encodings(image_rgb)[0]
            
            # Append the face encoding and name to the arrays
            known_face_encodings.append(face_encoding)
            known_face_names.append(name)
    else:
        print(f"Image not found for patient: {name}")

video_capture = cv2.VideoCapture(1)
recognized_name = "Unknown"  # Initialize recognized name

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # Convert the frame from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find all face locations in the current frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Check if the face matches any known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            recognized_name = name  # Update recognized name

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop if a face is recognized
    if recognized_name != "Unknown":
        break

    # Break the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV windows
video_capture.release()
cv2.destroyAllWindows()

# Print the recognized name
print(f"Recognized name: {recognized_name}")

# Ensure the script exits properly
exit(0)
