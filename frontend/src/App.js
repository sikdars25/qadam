import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import AdminDashboard from './components/AdminDashboard';
import Activate from './components/Activate';
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  // Check for stored user on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Error parsing stored user:', e);
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={user ? (user.is_admin ? <Navigate to="/admin" /> : <Navigate to="/" />) : <Login onLogin={handleLogin} />} 
          />
          <Route 
            path="/" 
            element={user && !user.is_admin ? <Dashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/admin" 
            element={user && user.is_admin ? <AdminDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/activate" 
            element={<Activate />} 
          />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
