from deepface import DeepFace  # type: ignore
import cv2  # type: ignore

# Open the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open webcam. Please check your camera connection.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Mirror the frame
    frame = cv2.flip(frame, 1)

    # Detect faces in the frame using OpenCV's pre-trained Haar Cascade classifier
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        # Draw rectangle around the face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Crop the face region from the frame
        face = frame[y:y+h, x:x+w]

        # Analyze the emotion of the face using DeepFace (no need to load a custom model)
        result = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)

        # Get the dominant emotion
        dominant_emotion = result[0]['dominant_emotion']

        # Display the emotion text on the frame
        cv2.putText(frame, dominant_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    # Display the frame with rectangles and emotions
    cv2.imshow("Emotion Detection", frame)

    # Exit loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()