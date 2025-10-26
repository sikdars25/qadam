import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './UploadPapers.css';
import ParsedQuestionsView from './ParsedQuestionsView';

const UploadPapers = ({ user }) => {
  // Question Papers State
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [file, setFile] = useState(null);
  const [uploadedPapers, setUploadedPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Textbooks State
  const [textbookTitle, setTextbookTitle] = useState('');
  const [textbookSubject, setTextbookSubject] = useState('');
  const [textbookAuthor, setTextbookAuthor] = useState('');
  const [textbookFile, setTextbookFile] = useState(null);
  const [uploadedTextbooks, setUploadedTextbooks] = useState([]);
  const [textbookLoading, setTextbookLoading] = useState(false);
  const [textbookMessage, setTextbookMessage] = useState({ type: '', text: '' });

  // Question Parsing State
  const [parsingPaper, setParsingPaper] = useState(null);
  const [parsedQuestions, setParsedQuestions] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [showParsedQuestions, setShowParsedQuestions] = useState(false);
  const [parsingLoading, setParsingLoading] = useState(false);
  const [parsingMessage, setParsingMessage] = useState({ type: '', text: '' });

  // Tab State
  const [activeTab, setActiveTab] = useState('textbooks');

  useEffect(() => {
    fetchUploadedPapers();
    fetchUploadedTextbooks();
    fetchParsedQuestions();
  }, []);

  const fetchUploadedPapers = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/uploaded-papers');
      setUploadedPapers(response.data);
    } catch (err) {
      console.error('Error fetching papers:', err);
    }
  };

  const fetchUploadedTextbooks = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/textbooks');
      setUploadedTextbooks(response.data);
    } catch (err) {
      console.error('Error fetching textbooks:', err);
    }
  };

  const fetchParsedQuestions = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/parsed-questions');
      setParsedQuestions(response.data);
    } catch (err) {
      console.error('Error fetching parsed questions:', err);
    }
  };

  const handleParseQuestions = async (paperId) => {
    setParsingLoading(true);
    setParsingMessage({ type: '', text: '' });
    setParsingPaper(paperId);

    try {
      const response = await axios.post(`http://localhost:5000/api/parse-questions/${paperId}`);
      
      if (response.data.success) {
        setParsingMessage({ 
          type: 'success', 
          text: `Successfully parsed ${response.data.total_questions} questions!` 
        });
        fetchParsedQuestions();
        setTimeout(() => setShowParsedQuestions(true), 1000);
      }
    } catch (err) {
      setParsingMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Parsing failed. Please try again.' 
      });
    } finally {
      setParsingLoading(false);
      setParsingPaper(null);
    }
  };

  const handleCleanDuplicates = async () => {
    if (!window.confirm('Remove all duplicate questions from database?')) {
      return;
    }

    setParsingLoading(true);
    setParsingMessage({ type: '', text: '' });

    try {
      const response = await axios.post('http://localhost:5000/api/clean-duplicates');
      
      if (response.data.success) {
        setParsingMessage({ 
          type: 'success', 
          text: response.data.message 
        });
        fetchParsedQuestions();
      }
    } catch (err) {
      setParsingMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Cleanup failed.' 
      });
    } finally {
      setParsingLoading(false);
    }
  };

  const handleDeletePaper = async (paperId, paperTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${paperTitle}"?\n\nThis will also delete all parsed questions associated with this paper.`)) {
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await axios.delete(`http://localhost:5000/api/delete-paper/${paperId}`);
      
      if (response.data.success) {
        setMessage({ 
          type: 'success', 
          text: 'Paper deleted successfully!' 
        });
        fetchUploadedPapers();
        fetchParsedQuestions();
      }
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Delete failed. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTextbook = async (textbookId, textbookTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${textbookTitle}"?`)) {
      return;
    }

    setTextbookLoading(true);
    setTextbookMessage({ type: '', text: '' });

    try {
      const response = await axios.delete(`http://localhost:5000/api/delete-textbook/${textbookId}`);
      
      if (response.data.success) {
        setTextbookMessage({ 
          type: 'success', 
          text: 'Textbook deleted successfully!' 
        });
        fetchUploadedTextbooks();
      }
    } catch (err) {
      setTextbookMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Delete failed. Please try again.' 
      });
    } finally {
      setTextbookLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      
      // Auto-populate title with filename (without extension)
      const fileName = selectedFile.name;
      const fileNameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
      
      // Only set title if it's empty
      if (!title) {
        setTitle(fileNameWithoutExt);
      }
    }
  };

  const handleTextbookFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setTextbookFile(selectedFile);
      
      // Auto-populate title with filename (without extension)
      const fileName = selectedFile.name;
      const fileNameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
      
      // Only set title if it's empty
      if (!textbookTitle) {
        setTextbookTitle(fileNameWithoutExt);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title || !subject || !file) {
      setMessage({ type: 'error', text: 'Please fill all fields and select a file' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('subject', subject);
    formData.append('user_id', user.id);

    try {
      const response = await axios.post('http://localhost:5000/api/upload-paper', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setMessage({ type: 'success', text: 'Paper uploaded successfully!' });
        setTitle('');
        setSubject('');
        setFile(null);
        document.getElementById('file-input').value = '';
        fetchUploadedPapers();
      }
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Upload failed. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTextbookSubmit = async (e) => {
    e.preventDefault();
    
    if (!textbookTitle || !textbookSubject || !textbookFile) {
      setTextbookMessage({ type: 'error', text: 'Please fill all required fields and select a file' });
      return;
    }

    setTextbookLoading(true);
    setTextbookMessage({ type: '', text: '' });

    const formData = new FormData();
    formData.append('file', textbookFile);
    formData.append('title', textbookTitle);
    formData.append('subject', textbookSubject);
    formData.append('author', textbookAuthor);
    formData.append('user_id', user.id);

    try {
      const response = await axios.post('http://localhost:5000/api/upload-textbook', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setTextbookMessage({ type: 'success', text: 'Textbook uploaded successfully!' });
        setTextbookTitle('');
        setTextbookSubject('');
        setTextbookAuthor('');
        setTextbookFile(null);
        document.getElementById('textbook-file-input').value = '';
        fetchUploadedTextbooks();
      }
    } catch (err) {
      setTextbookMessage({ 
        type: 'error', 
        text: err.response?.data?.error || 'Upload failed. Please try again.' 
      });
    } finally {
      setTextbookLoading(false);
    }
  };

  // eslint-disable-next-line no-unused-vars
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
    <div className="upload-papers">
      <div className="upload-header">
        <h2>📤 Upload Resources</h2>
        <p>Share textbooks, study materials, and past papers</p>
      </div>

      {/* Tabs */}
      <div className="upload-tabs">
        <button 
          className={`tab-btn ${activeTab === 'textbooks' ? 'active' : ''}`}
          onClick={() => setActiveTab('textbooks')}
        >
          📚 Textbooks
        </button>
        <button 
          className={`tab-btn ${activeTab === 'papers' ? 'active' : ''}`}
          onClick={() => setActiveTab('papers')}
        >
          📝 Question Papers
        </button>
        <button 
          className={`tab-btn ${activeTab === 'all-questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('all-questions')}
        >
          📋 All Questions
        </button>
      </div>

      {/* Textbook Upload Section */}
      {activeTab === 'textbooks' && (
      <div className="upload-section compact">
        <h3 className="section-title">📚 Upload Textbooks</h3>
        <div className="compact-form-container">
          <form onSubmit={handleTextbookSubmit} className="compact-form">
            <input
              type="text"
              value={textbookTitle}
              onChange={(e) => setTextbookTitle(e.target.value)}
              placeholder="Title (auto-filled)"
              required
            />
            <select
              value={textbookSubject}
              onChange={(e) => setTextbookSubject(e.target.value)}
              required
            >
              <option value="">Subject</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Chemistry">Chemistry</option>
              <option value="Biology">Biology</option>
              <option value="English">English</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Social Science">Social Science</option>
            </select>
            <input
              type="text"
              value={textbookAuthor}
              onChange={(e) => setTextbookAuthor(e.target.value)}
              placeholder="Author (optional)"
            />
            <input
              type="file"
              id="textbook-file-input"
              onChange={handleTextbookFileChange}
              accept=".pdf,.doc,.docx,.txt"
              required
            />
            <button type="submit" className="compact-upload-btn" disabled={textbookLoading}>
              {textbookLoading ? '⏳' : '📚 Upload'}
            </button>
          </form>
          {textbookMessage.text && (
            <div className={`compact-message ${textbookMessage.type}`}>
              {textbookMessage.text}
            </div>
          )}
        </div>

        {uploadedTextbooks.length > 0 && (
          <div className="table-container">
            <table className="documents-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Subject</th>
                  <th>Vectorized</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {uploadedTextbooks.map((textbook) => {
                  const isVectorized = textbook.is_indexed === 1 || textbook.is_indexed === true;
                  return (
                    <tr key={textbook.id}>
                      <td className="title-cell">📚 {textbook.title}</td>
                      <td><span className="subject-badge">{textbook.subject}</span></td>
                      <td>
                        <span className={`parsed-badge ${isVectorized ? 'parsed-yes' : 'parsed-no'}`}>
                          {isVectorized ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="table-delete-btn"
                          onClick={() => handleDeleteTextbook(textbook.id, textbook.title)}
                          disabled={textbookLoading}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
      )}

      {/* Question Papers Upload Section */}
      {activeTab === 'papers' && (
      <div className="upload-section compact">
        <div className="section-header-compact">
          <h3 className="section-title">📝 Upload Question Papers</h3>
          <div className="header-actions-compact">
            <button 
              className="compact-action-btn"
              onClick={handleCleanDuplicates}
              disabled={parsingLoading}
            >
              🧹 Clean
            </button>
          </div>
        </div>

        <div className="compact-form-container">
          <form onSubmit={handleSubmit} className="compact-form">
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Paper Title (auto-filled)"
              required
            />
            <select
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
            >
              <option value="">Subject</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Chemistry">Chemistry</option>
              <option value="Biology">Biology</option>
              <option value="English">English</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Social Science">Social Science</option>
            </select>
            <input
              type="file"
              id="file-input"
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.txt"
              required
            />
            <button type="submit" className="compact-upload-btn" disabled={loading}>
              {loading ? '⏳' : '📤 Upload'}
            </button>
          </form>
          {message.text && (
            <div className={`compact-message ${message.type}`}>
              {message.text}
            </div>
          )}
        </div>

        {uploadedPapers.length > 0 && (
          <div className="table-container">
            <table className="documents-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Subject</th>
                  <th>Parsed</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {uploadedPapers.map((paper) => {
                  const isParsed = parsedQuestions.some(q => q.paper_id === paper.id);
                  return (
                    <tr key={paper.id}>
                      <td className="title-cell">📄 {paper.title}</td>
                      <td><span className="subject-badge">{paper.subject}</span></td>
                      <td>
                        <span className={`parsed-badge ${isParsed ? 'parsed-yes' : 'parsed-no'}`}>
                          {isParsed ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="table-action-btn parse"
                          onClick={() => handleParseQuestions(paper.id)}
                          disabled={parsingPaper === paper.id}
                          title="Parse Questions"
                        >
                          {parsingPaper === paper.id ? '⏳' : '🔍'}
                        </button>
                        <button 
                          className="table-delete-btn"
                          onClick={() => handleDeletePaper(paper.id, paper.title)}
                          disabled={loading}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {parsingMessage.text && (
              <div className={`compact-message ${parsingMessage.type}`}>
                {parsingMessage.text}
              </div>
            )}
          </div>
        )}
      </div>
      )}

      {/* All Questions Tab */}
      {activeTab === 'all-questions' && (
        <div className="all-questions-section">
          <ParsedQuestionsView 
            onClose={null}
            embedded={true}
          />
        </div>
      )}
    </div>
  );
};

export default UploadPapers;
