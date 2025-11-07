# 🧠 ASL Detection — American Sign Language Recognition

> A full-stack project that detects **American Sign Language (ASL)** gestures in real-time using **TensorFlow**, **Mediapipe**, and **FastAPI**, with a modern **React (Vite)** frontend and secure **Google OAuth authentication**.

---

## 🚀 Tech Stack

| Category           | Technology                                             |
| ------------------ | ------------------------------------------------------ |
| **Frontend**       | React (Vite), Axios, @react-oauth/google               |
| **Backend**        | FastAPI, TensorFlow, Mediapipe, SQLAlchemy             |
| **Database**       | SQLite                                                 |
| **Authentication** | Google OAuth 2.0 + Local Auth                          |
| **Model**          | Custom Trained CNN (`best_finetuned_modelpart2.keras`) |
| **Deployment**     | Render (Backend) + Netlify (Frontend)                  |

---

## 📁 Project Structure

```
ASL-Final-Project/
│
├── backend/                      # FastAPI backend
│   ├── app.py                    # Main FastAPI app (Google OAuth + Prediction)
│   ├── best_finetuned_modelpart2.keras
│   ├── collect_data.py           # Data collection for training
│   ├── create_dataset.py         # Dataset preprocessing
│   ├── database.py               # SQLAlchemy database setup
│   ├── models.py                 # ORM models
│   ├── schemas.py                # Pydantic schemas
│   ├── train_model.py            # Model training
│   ├── test_sign_model.py        # Model testing
│   ├── test_camera.py            # Live webcam test
│   ├── requirements.txt          # Python dependencies
│   ├── runtime.txt               # Python runtime version for Render
│   ├── users.db                  # Auto-created SQLite DB
│   ├── .env                      # Backend environment variables
│   └── venv/                     # Virtual environment (ignored)
│
├── frontend/                     # React (Vite) frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DetectionApp.jsx  # Real-time detection UI
│   │   │   ├── Login.jsx         # Email/Password + Google login
│   │   │   ├── Signup.jsx        # Registration page
│   │   │   ├── MainPage.jsx      # Dashboard / Home
│   │   │   └── PrivateRoute.jsx  # Auth-protected routes
│   │   ├── styles/
│   │   │   ├── App.css
│   │   │   ├── index.css
│   │   │   └── Auth.css
│   │   ├── assets/               # Images / Icons
│   │   ├── App.jsx               # Routing setup
│   │   └── main.jsx              # Entry point with GoogleOAuthProvider
│   ├── package.json
│   ├── vite.config.js
│   ├── .env
│   └── .gitignore
│
├── model/                        # Optional model or dataset storage
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 🧩 1. Clone the Repository

```bash
git clone https://github.com/Abhinavv1524/ASL-Final-Project.git
cd ASL-Final-Project
```

### 🧠 2. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
# Activate the environment
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Create `.env` file

```ini
GOOGLE_CLIENT_ID=809547916780-h8i8dmf3uau16ttajq6nem53ptd052nl.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxx_yoursecret
SECRET_KEY=super_secret_key_123
```

#### Run backend

```bash
uvicorn app:app --reload
```

✅ **Backend URL:** http://127.0.0.1:8000

---

### 💻 3. Frontend Setup (React + Vite)

```bash
cd ../frontend
npm install
```

#### Create `.env` file

```ini
VITE_BACKEND_URL=http://127.0.0.1:8000
VITE_GOOGLE_CLIENT_ID=809547916780-h8i8dmf3uau16ttajq6nem53ptd052nl.apps.googleusercontent.com
```

#### Run frontend

```bash
npm run dev
```

✅ **Frontend URL:** http://localhost:5173

---

## 🔑 Authentication

### Local Auth

- Users can sign up and log in using email & password.
- Passwords are securely hashed using bcrypt.

### Google OAuth

- Users can sign in with Google via Google Identity Services.

**Google Cloud Console setup:**  
Authorized JavaScript origins:

```
http://localhost:5173
https://your-netlify-site.netlify.app
```

Authorized redirect URIs:

```
http://localhost:5173
https://your-netlify-site.netlify.app
```

---

## 🧠 Model Information

- **File:** `backend/best_finetuned_modelpart2.keras`
- **Framework:** TensorFlow / Keras
- **Uses:** Mediapipe Holistic for feature extraction.
- **Trained Gestures:**

```python
['hello', 'thanks', 'iloveyou', 'yes', 'no']
```

---

## 📸 Real-Time Detection Flow

1. The webcam captures frames using React Webcam.
2. Each frame is sent as a JPEG blob to the FastAPI `/predict/` endpoint.
3. FastAPI extracts keypoints via Mediapipe.
4. The TensorFlow model predicts the gesture class.
5. The frontend displays the detected gesture and confidence.

---

## 🧾 API Endpoints

| Method | Endpoint       | Description                         |
| ------ | -------------- | ----------------------------------- |
| POST   | `/signup`      | Register a new user                 |
| POST   | `/login`       | Login with email/password           |
| POST   | `/auth/google` | Google OAuth login                  |
| POST   | `/predict/`    | Predict gesture from uploaded frame |
| POST   | `/visualize/`  | Return Mediapipe-annotated image    |

---

## 🌐 Deployment

### 🔹 Backend on Render

1. Push project to GitHub.
2. Go to Render Dashboard → Create Web Service.
3. Configure:

**Root Directory:** backend  
**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
uvicorn app:app --host 0.0.0.0 --port 10000
```

**Environment Variables:**

```ini
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
SECRET_KEY=super_secret_key
```

✅ **Deployed URL:** https://asl-final-project.onrender.com

---

### 🔹 Frontend on Netlify

1. Go to Netlify → New Site from Git.
2. Set configuration:

**Build command:** `npm run build`  
**Publish directory:** `frontend/dist`

**Environment Variables:**

```ini
VITE_BACKEND_URL=https://asl-final-project.onrender.com
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

✅ **Live Site URL:** https://your-app-name.netlify.app

---

## 🧩 .gitignore Essentials

```bash
# Backend
backend/venv/
backend/__pycache__/
backend/.env
backend/*.db
backend/MP_Data/
backend/uploads/
backend/temp/
backend/tmp/

# Frontend
frontend/node_modules/
frontend/dist/
frontend/.env

# System
.DS_Store
Thumbs.db
```

---

## 👨‍💻 Author

**Abhinav Choudhary**  
🎓 MCA | Lovely Professional University  
📧 abhinavchoudhary1524@gmail.com  
🔗 [GitHub Profile](https://github.com/Abhinavv1524)
