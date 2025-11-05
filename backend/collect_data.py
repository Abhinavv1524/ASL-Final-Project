import os
import numpy as np
import mediapipe as mp
import cv2

# 🔹 Replace the IP below with the one shown in your DroidCam app
DROIDCAM_URL = "http://192.168.29.123:4747/video"

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# 🔹 Path to save collected data
DATA_PATH = os.path.join('..', 'MP_Data')

# 🔹 Actions and configuration
actions = np.array(['hello', 'thanks', 'iloveyou', 'yes', 'no'])
no_sequences = 10
sequence_length = 30

# ----------- Utility Functions ------------
def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility]
                     for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    face = np.array([[res.x, res.y, res.z]
                     for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z]
                   for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z]
                   for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])

# ----------- Create directories ------------
for action in actions:
    for sequence in range(no_sequences):
        os.makedirs(os.path.join(DATA_PATH, action, str(sequence)), exist_ok=True)

# ----------- Capture from DroidCam ------------
print(f"🎥 Connecting to DroidCam feed: {DROIDCAM_URL}")
cap = cv2.VideoCapture(DROIDCAM_URL)

if not cap.isOpened():
    print("❌ Failed to connect to DroidCam. Check if the app is running and both devices are on same Wi-Fi.")
    exit()

print("✅ DroidCam connected successfully!")

# ----------- Start Mediapipe Holistic ------------
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    for action in actions:
        for sequence in range(no_sequences):
            print(f'📸 Collecting frames for {action} - sequence {sequence}')
            for frame_num in range(sequence_length):
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ Frame not received. Recheck DroidCam connection.")
                    break

                # 🔹 Flip the frame horizontally (like a mirror)
                frame = cv2.flip(frame, 1)

                # 🔹 Process with Mediapipe
                image, results = mediapipe_detection(frame, holistic)

                # 🔹 Draw landmarks
                mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION)
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
                mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

                # 🔹 Show collection message
                if frame_num == 0:
                    cv2.putText(image, 'STARTING COLLECTION', (120, 200),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4, cv2.LINE_AA)
                    cv2.putText(image, f'Collecting frames for {action} Video {sequence}', (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.imshow('OpenCV Feed', image)
                    cv2.waitKey(2000)  # 2 sec pause before recording
                else:
                    cv2.putText(image, f'Collecting frames for {action} Video {sequence}', (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.imshow('OpenCV Feed', image)

                # 🔹 Save keypoints
                keypoints = extract_keypoints(results)
                npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                np.save(npy_path, keypoints)

                # 🔹 Exit condition
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

cap.release()
cv2.destroyAllWindows()
print("✅ Data collection complete!")
