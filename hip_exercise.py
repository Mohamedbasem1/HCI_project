from ultralytics import YOLO
import cv2
import time

# Initialize the webcam
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("Error: Cannot access the webcam")
    exit()

model = YOLO(r"bestmodel.pt")  # Replace 'bestmodel.pt' with the path to your model file
print("Model loaded successfully!")

success_count = 0
class_id_1 = 0  # Replace with the actual class ID for the first class
class_id_2 = 1  # Replace with the actual class ID for the second class
waiting_for_disappearance = False  # Flag to wait for disappearance of classes
detection_start_time = None  # Start time for detecting both classes

required_detection_time = 0.4  # Time in seconds
start_time = time.time()  # Record the start time
duration = 60  # Duration in seconds (1 minute)

# Run the video capture loop
while True:
    elapsed_time = time.time() - start_time  # Calculate elapsed time
    if elapsed_time > duration:
        print("1 minute elapsed. Exiting...")
        break

    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture frame")
        break

    # Use the YOLO model to make predictions
    results = model(frame)

    # Annotate the frame with predictions
    annotated_frame = results[0].plot()
    detected_classes = set()  # Store detected class IDs in the current frame

    if len(results[0].boxes) > 0:
        for box in results[0].boxes:
            class_id = int(box.cls)
            label = results[0].names[class_id]
            detected_classes.add(class_id)

    # Check if both classes are detected
    if class_id_1 in detected_classes and class_id_2 in detected_classes:
        if detection_start_time is None:
            # Start the timer when both classes are detected
            detection_start_time = time.time()
        elif time.time() - detection_start_time >= required_detection_time:
            # If both classes are detected for the required duration
            waiting_for_disappearance = True  # Start waiting for disappearance
    else:
        if detection_start_time is not None and time.time() - detection_start_time < required_detection_time:
            cv2.putText(annotated_frame, "You are too fast!", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        detection_start_time = None

    # Check for disappearance and increment success count
    if waiting_for_disappearance:
        if class_id_1 not in detected_classes and class_id_2 not in detected_classes:
            success_count += 1  # Increment success counter
            waiting_for_disappearance = False  # Reset flag
            detection_start_time = None  # Reset timer

    # Display the frame with annotations and success count
    cv2.putText(annotated_frame, f"Success Count: {success_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow("YOLO Object Detection", annotated_frame)

    # Break the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
