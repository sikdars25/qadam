import React, { useState } from 'react';
import Sidebar from './Sidebar';
import QuestionBank from './QuestionBank';
import DashboardQuestionSolver from './DashboardQuestionSolver';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const [activeMenu, setActiveMenu] = useState('solve-question');

  const renderContent = () => {
    switch (activeMenu) {
      case 'solve-question':
        return <DashboardQuestionSolver />;
      case 'question-bank':
        return <QuestionBank />;
      default:
        return <DashboardQuestionSolver />;
    }
  };

  return (
    <div className="dashboard">
      <Sidebar 
        activeMenu={activeMenu} 
        setActiveMenu={setActiveMenu}
        user={user}
        onLogout={onLogout}
      />
      <div className="dashboard-content">
        <div className="content-area">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
