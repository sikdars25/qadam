import React, { useState } from 'react';
import axiosInstance from '../config/axios';
import './Login.css';
import Register from './Register';
import API_URL from '../config/api';
import { setToken, setUser } from '../utils/auth';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axiosInstance.post(`${API_URL}/api/login`, {
        username,
        password
      }, {
        withCredentials: true  // Enable cookies for session management
      });

      if (response.data.message === 'Login successful' || response.data.success) {
        // Store JWT token if provided
        if (response.data.token) {
          setToken(response.data.token);
          console.log('🔑 JWT token stored');
        }
        
        // Store user data
        if (response.data.user) {
          setUser(response.data.user);
        }
        
        onLogin(response.data.user);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (showRegister) {
    return <Register onBack={() => setShowRegister(false)} onRegisterSuccess={() => setShowRegister(false)} />;
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">🎓</div>
          <h1>
            <span className="brand-name">Qadam</span>
            <span className="brand-subtitle">Step up your prep</span>
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="register-link">
          <p>
            Don't have an account?{' '}
            <button
              type="button"
              className="register-btn"
              onClick={() => setShowRegister(true)}
            >
              Register Now
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
