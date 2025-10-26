import React, { useState } from 'react';
import axios from 'axios';
import './Register.css';

const Register = ({ onBack, onRegisterSuccess }) => {
  const [formData, setFormData] = useState({
    fullName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [activationSent, setActivationSent] = useState(false);
  const [activationLink, setActivationLink] = useState('');
  // eslint-disable-next-line no-unused-vars
  const [emailSent, setEmailSent] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/register', {
        fullName: formData.fullName,
        username: formData.username,
        email: formData.email,
        phone: null,
        password: formData.password
      });

      if (response.data.success) {
        setActivationSent(true);
        
        if (response.data.activation_link) {
          // Email not configured - show activation link
          setActivationLink(response.data.activation_link);
          setEmailSent(false);
          setSuccess('Registration successful! Click the activation link below to activate your account.');
        } else if (response.data.email_sent) {
          // Email sent successfully
          setEmailSent(true);
          setSuccess('Registration successful! Please check your email to activate your account.');
        } else {
          setSuccess(response.data.message);
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card register-card">
        <div className="login-header">
          <div className="login-icon">🎓</div>
          <h1>
            <span className="brand-name">qadam</span>
            <span className="brand-subtitle">Academic Portal</span>
          </h1>
          <p className="register-subtitle">Create Your Account</p>
        </div>

        <form onSubmit={handleRegister} className="login-form">
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              placeholder="Enter your full name"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
              disabled={activationSent}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              disabled={activationSent}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password (min 6 characters)"
              minLength="6"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Re-enter your password"
              minLength="6"
              required
            />
          </div>

          {success && <div className="success-message">{success}</div>}
          {error && <div className="error-message">{error}</div>}
          
          {activationLink && (
            <div className="activation-link-box">
              <h3>🔗 Activation Link</h3>
              <p className="activation-info">
                Email is not configured. Click the link below to activate your account:
              </p>
              <a 
                href={activationLink} 
                className="activation-link-button"
                target="_blank"
                rel="noopener noreferrer"
              >
                Activate Account Now
              </a>
              <p className="activation-copy">
                Or copy this link: <br/>
                <code>{activationLink}</code>
              </p>
            </div>
          )}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Processing...' : 'Register'}
          </button>
        </form>

        <div className="register-link">
          <p>
            Already have an account?{' '}
            <button
              type="button"
              className="register-btn"
              onClick={onBack}
            >
              Login
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
