import math

def calculate_angle(hip, knee, ankle):
    # Calculate the angle between three points
    angle = math.degrees(math.atan2(ankle.y - knee.y, ankle.x - knee.x) -
                         math.atan2(hip.y - knee.y, hip.x - knee.x))
    return angle