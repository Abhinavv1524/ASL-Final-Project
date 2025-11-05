from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import mediapipe as mp
from tensorflow.keras.models import load_model
from io import BytesIO
from PIL import Image

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
model = load_model("../model/model.h5")
actions = ["hello", "thanks", "iloveyou", "yes", "no"]  # adjust labels if needed

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

def extract_keypoints(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)
    if result.multi_hand_landmarks:
        landmarks = []
        for lm in result.multi_hand_landmarks[0].landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        return np.array(landmarks)
    return np.zeros(21 * 3)

@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert("RGB")
    frame = np.array(image)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    keypoints = extract_keypoints(frame)
    keypoints = keypoints.reshape(1, 1, -1)  # LSTM expects [batch, timesteps, features]

    prediction = model.predict(keypoints)
    predicted_label = actions[np.argmax(prediction)]
    confidence = float(np.max(prediction))

    return {"gesture": predicted_label, "confidence": confidence}
