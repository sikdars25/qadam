import React from 'react';
import './Sidebar.css';

const Sidebar = ({ activeMenu, setActiveMenu, user, onLogout, onUploadSingleQuestion }) => {
  const menuItems = [
    { id: 'sample-questions', label: 'Question Paper', icon: '📚' },
    { id: 'chapter-questions', label: 'Text Book', icon: '📖' },
    { id: 'question-bank', label: 'Question Bank', icon: '💾' },
    { id: 'upload-papers', label: 'Upload Hub', icon: '📤' }
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>🎓 Academic Portal</h2>
        <p className="sidebar-subtitle">CBSE, ICSE, Reference</p>
      </div>

      <nav className="sidebar-nav">
        <button
          className="sidebar-menu-item single-question-btn"
          onClick={onUploadSingleQuestion}
        >
          <span className="menu-icon">📝</span>
          <span className="menu-label">A Single Question</span>
        </button>

        <div className="sidebar-divider"></div>

        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-menu-item ${activeMenu === item.id ? 'active' : ''}`}
            onClick={() => setActiveMenu(item.id)}
          >
            <span className="menu-icon">{item.icon}</span>
            <span className="menu-label">{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-avatar">
            {user.full_name.charAt(0).toUpperCase()}
          </div>
          <div className="user-details">
            <p className="user-name">{user.full_name}</p>
            <p className="user-role">Student</p>
          </div>
        </div>
        <button className="logout-button" onClick={onLogout}>
          <span>🚪</span> Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
