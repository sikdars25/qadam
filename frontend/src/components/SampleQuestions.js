import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SampleQuestions.css';
import EnhancedPDFViewer from './EnhancedPDFViewer';

const SampleQuestions = () => {
  const [uploadedPapers, setUploadedPapers] = useState([]);
  const [filteredPapers, setFilteredPapers] = useState([]);
  const [textbooks, setTextbooks] = useState([]);
  const [filteredTextbooks, setFilteredTextbooks] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [selectedTextbook, setSelectedTextbook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState('');
  const [modalTitle, setModalTitle] = useState('');
  const [loadingContent, setLoadingContent] = useState(false);
  const [showEnhancedViewer, setShowEnhancedViewer] = useState(false);
  const [selectedPaperId, setSelectedPaperId] = useState(null);

  useEffect(() => {
    fetchUploadedPapers();
    fetchTextbooks();
  }, []);

  const fetchUploadedPapers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('http://localhost:5000/api/uploaded-papers');
      const papers = response.data;
      setUploadedPapers(papers);
      setFilteredPapers(papers);
      
      // Extract unique subjects from uploaded papers
      const uniqueSubjects = [...new Set(papers.map(paper => paper.subject))];
      setSubjects(uniqueSubjects);
    } catch (err) {
      setError('Failed to load uploaded papers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTextbooks = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/textbooks');
      const books = response.data;
      setTextbooks(books);
      setFilteredTextbooks(books);
    } catch (err) {
      console.error('Error fetching textbooks:', err);
    }
  };

  const handleSubjectChange = (subject) => {
    setSelectedSubject(subject);
    if (subject === 'all') {
      setFilteredPapers(uploadedPapers);
      setFilteredTextbooks(textbooks);
    } else {
      setFilteredPapers(uploadedPapers.filter(paper => paper.subject === subject));
      setFilteredTextbooks(textbooks.filter(book => book.subject === subject));
    }
  };

  const handleRowClick = async (paper, isTextbook = false) => {
    if (isTextbook) {
      // Select textbook for analysis
      setSelectedTextbook(paper);
      return;
    }

    // Check if a textbook is selected for AI analysis
    if (selectedTextbook) {
      // Open enhanced viewer with AI features
      setSelectedPaperId(paper.id);
      setShowEnhancedViewer(true);
    } else {
      // Open regular modal viewer
      setModalOpen(true);
      setModalTitle(paper.title);
      setLoadingContent(true);
      setModalContent('');

      try {
        const apiUrl = `http://localhost:5000/api/paper-file/${paper.id}`;
        
        const response = await axios.get(apiUrl);
        if (response.data.success) {
          const fileType = response.data.file_type;
          const fileUrl = `http://localhost:5000/api/download-paper/${paper.id}`;
          
          if (fileType === 'pdf') {
            setModalContent(`<iframe src="${fileUrl}" style="width: 100%; height: 600px; border: none; border-radius: 8px;"></iframe>`);
          } else if (fileType === 'txt') {
            const textResponse = await fetch(fileUrl);
            const textContent = await textResponse.text();
            setModalContent(`<pre style="white-space: pre-wrap; font-family: Arial; padding: 20px; background: #f8f9fa; border-radius: 8px; line-height: 1.6;">${textContent}</pre>`);
          } else {
            setModalContent(`<div style="padding: 40px; text-align: center;">
              <h3>File Preview Not Available</h3>
              <p>This file type (${fileType.toUpperCase()}) cannot be previewed in the browser.</p>
              <a href="${fileUrl}" download style="display: inline-block; margin-top: 20px; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Download File</a>
            </div>`);
          }
        } else {
          setModalContent('<div style="padding: 20px; color: red;">Failed to load file.</div>');
        }
      } catch (err) {
        setModalContent('<div style="padding: 20px; color: red;">Error loading file.</div>');
      } finally {
        setLoadingContent(false);
      }
    }
  };

  const handleTextbookClick = (textbook) => {
    if (selectedTextbook && selectedTextbook.id === textbook.id) {
      // Deselect textbook
      setSelectedTextbook(null);
    } else {
      // Select textbook
      setSelectedTextbook(textbook);
    }
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalContent('');
    setModalTitle('');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="sample-questions">
      {showEnhancedViewer ? (
        <EnhancedPDFViewer
          paperId={selectedPaperId}
          textbookId={selectedTextbook?.id}
          onClose={() => setShowEnhancedViewer(false)}
        />
      ) : (
        <>
          <div className="questions-header">
            <h2>📚 Answer a full paper</h2>
            <p>
              {selectedTextbook 
                ? `🤖 AI Mode Active: Selected "${selectedTextbook.title}" - Click any question paper for AI analysis`
                : 'Select a textbook first, then click a question paper for AI-powered analysis'}
            </p>
          </div>

      <div className="filter-section">
        <label>Filter by Subject:</label>
        <div className="subject-filters">
          <button
            className={`filter-btn ${selectedSubject === 'all' ? 'active' : ''}`}
            onClick={() => handleSubjectChange('all')}
          >
            All Subjects
          </button>
          {subjects.map((subject) => (
            <button
              key={subject}
              className={`filter-btn ${selectedSubject === subject ? 'active' : ''}`}
              onClick={() => handleSubjectChange(subject)}
            >
              {subject}
            </button>
          ))}
        </div>
      </div>

          {/* Textbooks Section */}
          {filteredTextbooks.length > 0 && (
            <div className="textbooks-section">
              <h3 className="section-heading">
                📖 Available Textbooks 
                {selectedTextbook && <span className="ai-badge">✨ AI Analysis Mode</span>}
              </h3>
              <div className="textbooks-grid">
                {filteredTextbooks.map((textbook) => (
                  <div 
                    key={textbook.id} 
                    className={`textbook-card ${selectedTextbook?.id === textbook.id ? 'selected' : ''}`}
                    onClick={() => handleTextbookClick(textbook)}
                  >
                    <div className="textbook-icon">📚</div>
                    <div className="textbook-info">
                      <h4>{textbook.title}</h4>
                      <p className="textbook-subject">{textbook.subject}</p>
                      {textbook.author && <p className="textbook-author">By: {textbook.author}</p>}
                      <p className="textbook-meta">Uploaded by: {textbook.uploaded_by_name || 'Unknown'}</p>
                    </div>
                    {selectedTextbook?.id === textbook.id && (
                      <div className="selected-badge">✓ Selected</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

      {/* Question Papers Section */}
      <div className="papers-section">
        <h3 className="section-heading">📝 Question Papers</h3>
        {loading ? (
          <div className="loading">Loading papers...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : filteredPapers.length === 0 ? (
          <div className="no-questions">
            {selectedSubject === 'all' 
              ? 'No papers uploaded yet. Upload papers from the "Upload Papers" menu.' 
              : `No papers found for ${selectedSubject}.`}
          </div>
        ) : (
          <div className="table-container">
            <table className="papers-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Title</th>
                  <th>Subject</th>
                  <th>Uploaded By</th>
                  <th>Upload Date</th>
                  <th>File Name</th>
                </tr>
              </thead>
              <tbody>
                {filteredPapers.map((paper, index) => (
                  <tr 
                    key={paper.id} 
                    onClick={() => handleRowClick(paper, false)}
                    className="clickable-row"
                  >
                    <td>{index + 1}</td>
                    <td className="title-cell">{paper.title}</td>
                  <td>
                    <span className="subject-badge">{paper.subject}</span>
                  </td>
                  <td>{paper.uploaded_by_name || 'Unknown'}</td>
                  <td>{formatDate(paper.uploaded_at)}</td>
                  <td className="file-cell">{paper.file_path.split('/').pop()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )}
      </div>

          {/* Modal for displaying paper content */}
          {modalOpen && (
            <div className="modal-overlay" onClick={closeModal}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>{modalTitle}</h3>
                  <button className="close-button" onClick={closeModal}>✕</button>
                </div>
                <div className="modal-body">
                  {loadingContent ? (
                    <div className="loading-content">Loading content...</div>
                  ) : (
                    <div dangerouslySetInnerHTML={{ __html: modalContent }} />
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SampleQuestions;
