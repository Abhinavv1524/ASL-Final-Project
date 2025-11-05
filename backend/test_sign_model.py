import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
from collections import deque
import time

# ===============================
# Load the best trained model
# ===============================
model = load_model("best_finetuned_modelpart2.keras")

# 🔤 Update this list exactly as per your training actions
actions = np.array([
    'hello', 'thanks', 'iloveyou', 'yes', 'no'
])

# ===============================
# Mediapipe setup
# ===============================
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

sequence_buffer = deque(maxlen=30)
last_prediction_time = 0
prediction_interval = 3  # seconds between predictions
last_action = None

holistic = mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ===============================
# Extract Keypoints Function
# ===============================
def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    face = np.array([[res.x, res.y, res.z] for res in
                     results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
    lh = np.array([[res.x, res.y, res.z] for res in
                   results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in
                   results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)
    return np.concatenate([pose, face, lh, rh])  # shape: (1662,)

# ===============================
# Start Camera
# ===============================
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture("http://10.16.96.241:4747/video")  # your phone’s IP from DroidCam

print("✅ Webcam opened. Performing live gesture detection...")

threshold = 0.7  # Confidence threshold

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame.")
        break

    # Flip horizontally (mirror view)
    frame = cv2.flip(frame, 1)

    # Convert and process with MediaPipe
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(image_rgb)


    # Draw landmarks
    mp_drawing.draw_landmarks(frame, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
    mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    # Extract keypoints
    keypoints = extract_keypoints(results)
    sequence_buffer.append(keypoints)

    # Predict every few seconds
    current_time = time.time()
    if len(sequence_buffer) == 30 and current_time - last_prediction_time > prediction_interval:
        sequence = np.expand_dims(sequence_buffer, axis=0)
        yhat = model.predict(sequence, verbose=0)
        pred_class = actions[np.argmax(yhat)]
        confidence = float(np.max(yhat))

        if confidence > threshold:
            last_action = f"{pred_class} ({confidence*100:.1f}%)"
            print(f"✅ Detected: {pred_class} | Confidence: {confidence:.2f}")
        else:
            last_action = "No confident gesture"
            print(f"⚠️ Low confidence: {confidence:.2f}")

        last_prediction_time = current_time

    # Display last prediction
    if last_action:
        cv2.putText(frame, last_action, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('🤖 Sign Language Detection', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
holistic.close()
print("👋 Detection stopped.")
