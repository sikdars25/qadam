import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';
import Register from './Register';

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
      const response = await axios.post('http://localhost:5000/api/login', {
        username,
        password
      });

      if (response.data.success) {
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
