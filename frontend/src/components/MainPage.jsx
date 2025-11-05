import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import DetectionApp from "./DetectionApp";
import "../styles/MainPage.css";

const MainPage = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("User");

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem("user"));
    if (storedUser?.username) setUsername(storedUser.username);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <div className="main-container">
      <header className="header">
        <h2 className="welcome-text">Hi, {username} 👋</h2>
        <button className="logout-btn" onClick={handleLogout}>
          Logout
        </button>
      </header>

      <div className="detection-wrapper">
        <DetectionApp />
      </div>
    </div>
  );
};

export default MainPage;
