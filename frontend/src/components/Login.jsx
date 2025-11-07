import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";
import axios from "axios";
import "../styles/Auth.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please fill all fields");
      return;
    }

    try {
      const response = await fetch(
        "https://asl-final-project.onrender.com/login",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert("Login Successful!");
        localStorage.setItem("token", data.access_token);
        localStorage.setItem(
          "user",
          JSON.stringify({ username: data.username })
        );
        navigate("/");
      } else {
        alert(data.detail || "Invalid credentials");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong!");
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const decoded = jwtDecode(credentialResponse.credential);
      console.log("✅ Decoded Google Data:", decoded);

      const { email, name } = decoded;
      if (!email) {
        alert("Google login failed: No email found.");
        return;
      }

      console.log("📤 Sending to backend:", { email, name });

      const res = await axios.post(
        "https://asl-final-project.onrender.com/auth/google",
        {
          email,
          name,
        }
      );

      console.log("📥 Backend response:", res.data);

      const data = res.data;
      alert("Google Login Successful!");
      localStorage.setItem("token", "google");
      localStorage.setItem("user", JSON.stringify({ username: data.user }));
      navigate("/");
    } catch (err) {
      console.error("❌ Google Login Error:", err);
      alert("Google login failed!");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Welcome Back 👋</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">Login</button>
        </form>

        <p className="switch-text">
          Don’t have an account? <a href="/signup">Sign Up</a>
        </p>

        {/* ✅ Google Login Section */}
        <div style={{ marginTop: "25px" }}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => {
              alert("Google login failed 😢");
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default Login;
