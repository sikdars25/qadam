import React, { useState } from 'react';
import Sidebar from './Sidebar';
import SampleQuestions from './SampleQuestions';
import UploadPapers from './UploadPapers';
import ChapterQuestions from './ChapterQuestions';
import QuestionBank from './QuestionBank';
import SingleQuestionUpload from './SingleQuestionUpload';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const [activeMenu, setActiveMenu] = useState('sample-questions');
  const [showSingleQuestionUpload, setShowSingleQuestionUpload] = useState(false);

  const renderContent = () => {
    switch (activeMenu) {
      case 'sample-questions':
        return <SampleQuestions />;
      case 'upload-papers':
        return <UploadPapers user={user} />;
      case 'chapter-questions':
        return <ChapterQuestions />;
      case 'question-bank':
        return <QuestionBank />;
      default:
        return <SampleQuestions />;
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
