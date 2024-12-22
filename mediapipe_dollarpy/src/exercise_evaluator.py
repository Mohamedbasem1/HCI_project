import dollarpy

def normalize_angles(angles):
    min_angle, max_angle = min(angles), max(angles)
    return [(angle - min_angle) / (max_angle - min_angle) for angle in angles]

def evaluate_exercise(reference_angles, user_angles):
    # Normalize angles
    reference_angles = normalize_angles(reference_angles)
    user_angles = normalize_angles(user_angles)

    # Convert angles to points
    reference_points = [dollarpy.Point(i, angle) for i, angle in enumerate(reference_angles)]
    user_points = [dollarpy.Point(i, angle) for i, angle in enumerate(user_angles)]

    # Create gesture templates
    reference_gesture = dollarpy.Template("reference", reference_points)
    user_gesture = dollarpy.Template("user", user_points)

    # Initialize recognizer and recognize the user gesture
    recognizer = dollarpy.Recognizer([reference_gesture])
    template_name, match_score = recognizer.recognize(user_gesture)

    print(f"Match score: {match_score}")
    return match_score
