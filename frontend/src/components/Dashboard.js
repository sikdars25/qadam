import React, { useState } from 'react';
import Sidebar from './Sidebar';
import QuestionBank from './QuestionBank';
import SingleQuestionUpload from './SingleQuestionUpload';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const [activeMenu, setActiveMenu] = useState('question-bank');
  const [showSingleQuestionUpload, setShowSingleQuestionUpload] = useState(false);

  const renderContent = () => {
    switch (activeMenu) {
      case 'question-bank':
        return <QuestionBank />;
      default:
        return <QuestionBank />;
    }
  };

  const handleQuestionParsed = (question) => {
    console.log('Question parsed:', question);
    // You can add logic here to save or display the parsed question
  };

  return (
    <div className="dashboard">
      <Sidebar 
        activeMenu={activeMenu} 
        setActiveMenu={setActiveMenu}
        user={user}
        onLogout={onLogout}
        onUploadSingleQuestion={() => setShowSingleQuestionUpload(true)}
      />
      <div className="dashboard-content">
        <div className="content-area">
          {renderContent()}
        </div>
      </div>

      {showSingleQuestionUpload && (
        <SingleQuestionUpload
          onClose={() => setShowSingleQuestionUpload(false)}
          onQuestionParsed={handleQuestionParsed}
        />
      )}
    </div>
  );
};

export default Dashboard;
