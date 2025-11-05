import cv2
import os
import numpy as np
import mediapipe as mp
from time import sleep

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# 🔹 Replace this with your DroidCam IP
DROIDCAM_URL = "http://192.168.29.123:4747/video"

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR), results

def draw_styled_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh   = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh   = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])

# 🔹 Actions and folder setup
actions = np.array(['hello', 'thanks', 'iloveyou', 'yes', 'no'])
DATA_PATH = 'MP_Data'
no_sequences = 30
sequence_length = 30

for action in actions:
    for seq in range(no_sequences):
        os.makedirs(os.path.join(DATA_PATH, action, str(seq)), exist_ok=True)

print("Available actions:", actions)
action = input("Enter the action to record: ").strip().lower()
if action not in actions:
    print("❌ Invalid action!")
    exit()

# 🔹 Connect to DroidCam
print("\n🎥 Connecting to DroidCam feed...")
cap = cv2.VideoCapture(DROIDCAM_URL)

if not cap.isOpened():
    print("❌ Could not connect to DroidCam. Make sure the app is running and IP is correct.")
    exit()
else:
    print("✅ DroidCam connected successfully!")

# 🔹 Mediapipe processing
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    for sequence in range(no_sequences):
        print(f"\nRecording {sequence+1}/{no_sequences} for '{action}'")

        # Countdown before recording
        for i in range(3, 0, -1):
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame error during countdown!")
                break
            frame = cv2.flip(frame, 1)
            cv2.putText(frame, f'Starting in {i}', (120, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3, cv2.LINE_AA)
            cv2.imshow('Collecting Data', frame)
            cv2.waitKey(1000)

        for frame_num in range(sequence_length):
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame error! Recheck DroidCam connection.")
                break

            frame = cv2.flip(frame, 1)  # Mirror selfie view
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)

            keypoints = extract_keypoints(results)
            np.save(os.path.join(DATA_PATH, action, str(sequence), f"{frame_num}.npy"), keypoints)

            cv2.imshow('Collecting Data', image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()
print(f"✅ Data collection completed for '{action}'")
