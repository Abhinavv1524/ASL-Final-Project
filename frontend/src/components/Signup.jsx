import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Auth.css";

const Signup = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!name || !email || !password) {
      alert("Please fill all fields");
      return;
    }

    try {
      console.log("📤 Sending signup data:", { name, email, password });

      const response = await fetch(
        "https://asl-final-project.onrender.com/signup",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password }),
        }
      );

      const data = await response.json();
      console.log("📥 Response:", data);

      if (response.ok) {
        alert("Signup Successful!");
        localStorage.setItem("token", data.access_token);
        localStorage.setItem(
          "user",
          JSON.stringify({ username: data.username })
        );
        navigate("/");
      } else {
        alert(data.detail || "Signup failed!");
      }
    } catch (error) {
      console.error("❌ Error:", error);
      alert("Something went wrong!");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h2>Create Account ✨</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Create a password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Sign Up</button>
        </form>

        <p className="switch-text">
          Already have an account? <a href="/login">Login</a>
        </p>
      </div>
    </div>
  );
};

export default Signup;
