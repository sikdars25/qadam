import React, { useState, useEffect } from 'react';
import axiosInstance from '../config/axios';
import SampleQuestions from './SampleQuestions';
import ChapterQuestions from './ChapterQuestions';
import UploadPapers from './UploadPapers';
import './AdminDashboard.css';

function AdminDashboard({ user, onLogout }) {
  const [activeSection, setActiveSection] = useState('users');
  const [analyticsTab, setAnalyticsTab] = useState('questions'); // 'questions' or 'tokens'
  const [users, setUsers] = useState([]);
  const [usageAnalytics, setUsageAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('http://localhost:5000/api/admin/users');
      setUsers(response.data.users);
      setError('');
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsageAnalytics = async () => {
    try {
      const response = await axiosInstance.get('http://localhost:5000/api/admin/usage-analytics');
      setUsageAnalytics(response.data);
    } catch (err) {
      console.error('Failed to load usage analytics:', err);
    }
  };

  useEffect(() => {
    fetchUsers();
    fetchUsageAnalytics();
  }, []);

  const toggleUserStatus = async (userId, currentStatus) => {
    try {
      const response = await axiosInstance.post(
        `http://localhost:5000/api/admin/users/${userId}/toggle-active`
      );
      
      if (response.data.success) {
        setSuccess(response.data.message);
        fetchUsers(); // Refresh list
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update user status');
      setTimeout(() => setError(''), 3000);
    }
  };

  const deleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await axiosInstance.delete(
        `http://localhost:5000/api/admin/users/${userId}`,
        {
          withCredentials: true
        }
      );
      
      if (response.data.success) {
        setSuccess(response.data.message);
        fetchUsers(); // Refresh list
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete user');
      setTimeout(() => setError(''), 3000);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const menuItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard', description: 'Overview & Stats' },
    { id: 'users', icon: '👥', label: 'User Management', description: 'Manage Users' },
    { id: 'analytics', icon: '📈', label: 'Usage Analytics', description: 'Tokens & Activity' },
    { id: 'question-paper', icon: '📚', label: 'Question Paper', description: 'Answer All Questions' },
    { id: 'textbook', icon: '📖', label: 'Text Book', description: 'Answer Chapterwise' },
    { id: 'upload-hub', icon: '📤', label: 'Upload Hub', description: 'Upload Papers & Textbooks' },
  ];

  return (
    <div className="admin-dashboard">
      {/* Left Sidebar */}
      <div className="admin-sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-icon">🎓</span>
            <div className="logo-text">
              <h2>Qadam Admin</h2>
              <p>Control Panel</p>
            </div>
          </div>
        </div>

        <div className="sidebar-menu">
          {menuItems.map(item => (
            <button
              key={item.id}
              className={`menu-item ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => setActiveSection(item.id)}
            >
              <span className="menu-icon">{item.icon}</span>
              <div className="menu-content">
                <span className="menu-label">{item.label}</span>
                <span className="menu-description">{item.description}</span>
              </div>
            </button>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="admin-user-card">
            <div className="user-avatar">👨‍💼</div>
            <div className="user-details">
              <span className="user-name">{user.full_name}</span>
              <span className="user-role">Administrator</span>
            </div>
          </div>
          <button onClick={onLogout} className="sidebar-logout-btn">
            <span>🚪</span> Logout
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="admin-main">
        {/* Top Header */}
        <div className="admin-header">
          <div className="header-title">
            <h1>{menuItems.find(m => m.id === activeSection)?.label || 'Dashboard'}</h1>
            <p>{menuItems.find(m => m.id === activeSection)?.description || ''}</p>
          </div>
        </div>

        {/* Content Area */}
        <div className="admin-content">
        {/* Messages */}
        {error && <div className="admin-error">{error}</div>}
        {success && <div className="admin-success">{success}</div>}

        {/* Dashboard Section */}
        {activeSection === 'dashboard' && (
          <div className="dashboard-section">
            <div className="admin-stats">
          <div className="stat-card">
            <div className="stat-icon">👥</div>
            <div className="stat-info">
              <h3>{users.length}</h3>
              <p>Total Users</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-info">
              <h3>{users.filter(u => u.is_active).length}</h3>
              <p>Active Users</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⏸️</div>
            <div className="stat-info">
              <h3>{users.filter(u => !u.is_active).length}</h3>
              <p>Inactive Users</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">👨‍💼</div>
            <div className="stat-info">
              <h3>{users.filter(u => u.is_admin).length}</h3>
              <p>Admins</p>
            </div>
            </div>
          </div>
          <div className="welcome-card">
            <h2>Welcome, {user.full_name}! 👋</h2>
            <p>Use the sidebar menu to navigate through different sections of the admin panel.</p>
          </div>
        </div>
        )}

        {/* User Management Section */}
        {activeSection === 'users' && (
        <div className="users-table-container">
          <h2>All Users</h2>
          
          {loading ? (
            <div className="admin-loading">Loading users...</div>
          ) : (
            <table className="users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Status</th>
                  <th>Role</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id} className={!u.is_active ? 'inactive-user' : ''}>
                    <td>{u.id}</td>
                    <td>
                      <strong>{u.username}</strong>
                    </td>
                    <td>{u.full_name}</td>
                    <td>{u.email || 'N/A'}</td>
                    <td>{u.phone || 'N/A'}</td>
                    <td>
                      <span className={`status-badge ${u.is_active ? 'active' : 'inactive'}`}>
                        {u.is_active ? '✅ Active' : '⏸️ Inactive'}
                      </span>
                    </td>
                    <td>
                      {u.is_admin ? (
                        <span className="role-badge admin">👨‍💼 Admin</span>
                      ) : (
                        <span className="role-badge user">👤 User</span>
                      )}
                    </td>
                    <td className="date-cell">{formatDate(u.created_at)}</td>
                    <td>
                      <div className="action-buttons">
                        {!u.is_admin && (
                          <>
                            <button
                              onClick={() => toggleUserStatus(u.id, u.is_active)}
                              className={`action-btn ${u.is_active ? 'deactivate' : 'activate'}`}
                              title={u.is_active ? 'Deactivate' : 'Activate'}
                            >
                              {u.is_active ? '⏸️' : '▶️'}
                            </button>
                            <button
                              onClick={() => deleteUser(u.id, u.username)}
                              className="action-btn delete"
                              title="Delete User"
                            >
                              🗑️
                            </button>
                          </>
                        )}
                        {u.is_admin && (
                          <span className="protected-badge">🔒 Protected</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        )}

        {/* Question Paper Section */}
        {activeSection === 'question-paper' && (
          <div className="admin-feature-section">
            <SampleQuestions />
          </div>
        )}

        {/* Text Book Section */}
        {activeSection === 'textbook' && (
          <div className="admin-feature-section">
            <ChapterQuestions />
          </div>
        )}

        {/* Upload Hub Section */}
        {activeSection === 'upload-hub' && (
          <div className="admin-feature-section">
            <UploadPapers user={user} />
          </div>
        )}

        {/* Usage Analytics Section */}
        {activeSection === 'analytics' && (
          <div className="analytics-section">
            {!usageAnalytics ? (
              <div className="admin-loading">Loading analytics...</div>
            ) : (
              <>
                {/* Tabs */}
                <div className="analytics-tabs">
                  <button
                    className={`analytics-tab ${analyticsTab === 'questions' ? 'active' : ''}`}
                    onClick={() => setAnalyticsTab('questions')}
                  >
                    📊 Questions Solved
                  </button>
                  <button
                    className={`analytics-tab ${analyticsTab === 'tokens' ? 'active' : ''}`}
                    onClick={() => setAnalyticsTab('tokens')}
                  >
                    🤖 LLM Token Usage
                  </button>
                </div>

                {/* Questions Tab */}
                {analyticsTab === 'questions' && (
                <>
                {/* Overall Stats */}
                <div className="analytics-stats">
                  <div className="stat-card">
                    <div className="stat-icon">👥</div>
                    <div className="stat-info">
                      <h3>{usageAnalytics.overall_stats.active_users}</h3>
                      <p>Active Users</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">❓</div>
                    <div className="stat-info">
                      <h3>{usageAnalytics.overall_stats.total_questions_solved}</h3>
                      <p>Questions Solved</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">📚</div>
                    <div className="stat-info">
                      <h3>{usageAnalytics.overall_stats.total_subjects}</h3>
                      <p>Subjects Covered</p>
                    </div>
                  </div>
                </div>

                {/* Questions Solved by User */}
                <div className="analytics-table-container">
                  <h2>📊 Questions Solved by User</h2>
                  <table className="analytics-table">
                    <thead>
                      <tr>
                        <th>User</th>
                        <th>Total Questions</th>
                        <th>Single Question</th>
                        <th>Text Book</th>
                        <th>Question Paper</th>
                        <th>Subjects</th>
                        <th>First Activity</th>
                        <th>Last Activity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {usageAnalytics.user_analytics.map(user => (
                        <tr key={user.user_id}>
                          <td>
                            <strong>{user.full_name}</strong>
                            <br />
                            <span className="username-small">@{user.username}</span>
                          </td>
                          <td><strong className="highlight-number">{user.questions_solved}</strong></td>
                          <td>{user.solve_one_count}</td>
                          <td>{user.chapterwise_count}</td>
                          <td>{user.all_questions_count}</td>
                          <td>{user.subjects_covered}</td>
                          <td className="date-cell">{formatDate(user.first_question_date)}</td>
                          <td className="date-cell">{formatDate(user.last_question_date)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                </>
                )}

                {/* Tokens Tab */}
                {analyticsTab === 'tokens' && (
                <>
                {/* Token Usage Stats */}
                <div className="analytics-stats">
                  <div className="stat-card">
                    <div className="stat-icon">🤖</div>
                    <div className="stat-info">
                      <h3>{usageAnalytics.token_analytics.reduce((sum, u) => sum + u.total_tokens, 0).toLocaleString()}</h3>
                      <p>Total Tokens Used</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">📞</div>
                    <div className="stat-info">
                      <h3>{usageAnalytics.token_analytics.reduce((sum, u) => sum + u.api_calls, 0)}</h3>
                      <p>Total API Calls</p>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon">👥</div>
                    <div className="stat-info">
                      <h3>{usageAnalytics.token_analytics.length}</h3>
                      <p>Active Users</p>
                    </div>
                  </div>
                </div>

                {/* Token Usage Table */}
                {usageAnalytics.token_analytics.length > 0 ? (
                  <div className="analytics-table-container">
                    <h2>🤖 LLM Token Usage by User</h2>
                    <table className="analytics-table">
                      <thead>
                        <tr>
                          <th>User</th>
                          <th>Full Name</th>
                          <th>Total Tokens</th>
                          <th>API Calls</th>
                          <th>Model</th>
                          <th>Avg Tokens/Call</th>
                        </tr>
                      </thead>
                      <tbody>
                        {usageAnalytics.token_analytics.map(user => (
                          <tr key={user.user_id}>
                            <td>
                              <strong>{user.username}</strong>
                            </td>
                            <td>{user.full_name || 'N/A'}</td>
                            <td><strong className="highlight-number">{user.total_tokens.toLocaleString()}</strong></td>
                            <td>{user.api_calls}</td>
                            <td><span className="model-badge">{user.model_name}</span></td>
                            <td>{Math.round(user.total_tokens / user.api_calls)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="no-data-message">
                    <div className="no-data-icon">🤖</div>
                    <h3>No Token Usage Data</h3>
                    <p>Token usage tracking will appear here once users start solving questions with AI.</p>
                  </div>
                )}
                </>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
    </div>
  );
}

export default AdminDashboard;
