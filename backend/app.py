from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import mediapipe as mp
import tempfile
import io
from collections import deque
from PIL import Image
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt
from datetime import datetime, timedelta


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = "super_secret_key_123"  # You can change this
ALGORITHM = "HS256"


@app.post("/signup")
def signup(user: dict, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user["password"][:72])

    new_user = User(
        username=user["name"],
        email=user["email"],
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup successful"}


@app.post("/login")
def login(user: dict, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user["email"]).first()
    if not db_user or not pwd_context.verify(user["password"], db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = "dummy_token_123"

    return {
        "message": "Login successful",
        "access_token": access_token,
        "username": db_user.username,
    }


model = load_model("best_finetuned_modelpart2.keras")
actions = np.array(['hello', 'thanks', 'iloveyou', 'yes', 'no'])
mp_holistic = mp.solutions.holistic
sequence_buffer = deque(maxlen=30)
SINGLE_FRAME_MODE = True


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model.process(image)
    return results

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    face = np.array([[res.x, res.y, res.z] for res in
                     results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
    lh = np.array([[res.x, res.y, res.z] for res in
                   results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in
                   results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21 * 3)
    
    return np.concatenate([pose, face, lh, rh])

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    frame = cv2.imread(tmp_path)
    if frame is None:
        return {"error": "Could not read image."}

    with mp_holistic.Holistic(min_detection_confidence=0.5,
                              min_tracking_confidence=0.5) as holistic:
        results = mediapipe_detection(frame, holistic)
        keypoints = extract_keypoints(results)
        sequence = np.expand_dims([keypoints] * 30, axis=0)

        yhat = model.predict(sequence, verbose=0)
        predicted_class = actions[np.argmax(yhat)]
        confidence = float(np.max(yhat))

    return {"prediction": predicted_class, "confidence": confidence}

mp_drawing = mp.solutions.drawing_utils
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

@app.post("/visualize/")
async def visualize_keypoints(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")
    img_array = np.array(image)
    results = holistic.process(img_array)
    annotated_image = img_array.copy()

    mp_drawing.draw_landmarks(
        annotated_image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
        mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
        mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
    )
    mp_drawing.draw_landmarks(
        annotated_image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS
    )
    mp_drawing.draw_landmarks(
        annotated_image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS
    )
    mp_drawing.draw_landmarks(
        annotated_image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS
    )

    pil_img = Image.fromarray(annotated_image)
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")
