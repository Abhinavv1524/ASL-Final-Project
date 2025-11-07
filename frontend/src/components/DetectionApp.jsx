import React, { useRef, useState, useCallback, useEffect } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import "../styles/DetectionApp.css"; // ✅ New CSS file

function DetectionApp() {
  const webcamRef = useRef(null);
  const [gesture, setGesture] = useState("");
  const [confidence, setConfidence] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [intervalId, setIntervalId] = useState(null);
  const [language, setLanguage] = useState("en-IN");
  const [translated, setTranslated] = useState("");

  const captureFrame = useCallback(async () => {
    if (!webcamRef.current) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    const blob = await fetch(imageSrc).then((res) => res.blob());
    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");

    try {
      const res = await axios.post(
        "https://asl-final-project.onrender.com/predict/",
        formData
      );

      const detectedGesture = res.data.prediction;
      setGesture(detectedGesture);
      setConfidence((res.data.confidence * 100).toFixed(2));
    } catch (err) {
      console.error("Prediction error:", err);
    }
  }, []);

  const startDetection = () => {
    if (detecting) return;
    setDetecting(true);
    const id = setInterval(captureFrame, 5000);
    setIntervalId(id);
  };

  const stopDetection = () => {
    clearInterval(intervalId);
    setDetecting(false);
  };

  const speakGesture = () => {
    if (!gesture) return;
    const utterance = new SpeechSynthesisUtterance(translated || gesture);
    utterance.lang = language;
    window.speechSynthesis.speak(utterance);
  };

  const translateGesture = useCallback(async () => {
    if (!gesture) {
      setTranslated("");
      return;
    }

    const langCode = language.split("-")[0];

    if (langCode === "en") {
      setTranslated(gesture);
      return;
    }

    try {
      const response = await fetch(
        `https://api.mymemory.translated.net/get?q=${encodeURIComponent(
          gesture
        )}&langpair=en|${langCode}`
      );
      const data = await response.json();
      setTranslated(data.responseData.translatedText);
    } catch (err) {
      setTranslated(gesture);
    }
  }, [gesture, language]);

  useEffect(() => {
    translateGesture();
  }, [gesture, language, translateGesture]);

  return (
    <div className="detect-container">
      {/* ✅ Left: Webcam */}
      <div className="left-box">
        <Webcam
          ref={webcamRef}
          audio={false}
          mirrored={true}
          screenshotFormat="image/jpeg"
          className="webcam-feed"
        />

        {!detecting ? (
          <button className="btn-detect" onClick={startDetection}>
            Start Detection
          </button>
        ) : (
          <button className="btn-stop" onClick={stopDetection}>
            Stop Detection
          </button>
        )}
      </div>

      {/* ✅ Right: Results & Controls */}
      <div className="right-box">
        <h3 className="title">Detected Gesture:</h3>
        <p className="gesture">{gesture || "None"}</p>

        {translated && translated !== gesture && (
          <p className="translated-text">Translated: {translated}</p>
        )}

        {confidence && (
          <p className="confidence-text">Confidence: {confidence}%</p>
        )}

        <label className="label">🌍 Choose Language:</label>
        <select
          className="language-select"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="en-IN">English (India)</option>
          <option value="hi-IN">Hindi (भारत)</option>
          <option value="es-ES">Spanish (España)</option>
          <option value="fr-FR">French (France)</option>
          <option value="de-DE">German (Deutschland)</option>
        </select>

        <button className="btn-speak" onClick={speakGesture}>
          🔊 Speak
        </button>
      </div>
    </div>
  );
}

export default DetectionApp;
