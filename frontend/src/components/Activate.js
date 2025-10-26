import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

const Activate = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading'); // 'loading', 'success', 'error'
  const [message, setMessage] = useState('');
  const [username, setUsername] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage('Invalid activation link');
      return;
    }

    // Activate account
    const activateAccount = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/activate/${token}`);
        
        if (response.data.success) {
          setStatus('success');
          setMessage(response.data.message);
          setUsername(response.data.username);
          
          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/');
          }, 3000);
        } else {
          setStatus('error');
          setMessage(response.data.message || 'Activation failed');
        }
      } catch (err) {
        setStatus('error');
        setMessage(err.response?.data?.error || 'Activation failed. Please try again.');
      }
    };

    activateAccount();
  }, [searchParams, navigate]);

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">🎓</div>
          <h1>
            <span className="brand-name">qadam</span>
            <span className="brand-subtitle">Academic Portal</span>
          </h1>
        </div>

        <div className="activation-content">
          {status === 'loading' && (
            <div className="activation-loading">
              <div className="spinner"></div>
              <p>Activating your account...</p>
            </div>
          )}

          {status === 'success' && (
            <div className="activation-success">
              <div className="success-icon">✓</div>
              <h2>Account Activated!</h2>
              <p>{message}</p>
              {username && <p className="username-info">Username: <strong>{username}</strong></p>}
              <p className="redirect-info">Redirecting to login page...</p>
            </div>
          )}

          {status === 'error' && (
            <div className="activation-error">
              <div className="error-icon">✗</div>
              <h2>Activation Failed</h2>
              <p>{message}</p>
              <button 
                className="login-button"
                onClick={() => navigate('/')}
                style={{ marginTop: '20px' }}
              >
                Go to Login
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Activate;
