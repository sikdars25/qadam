import React, { useState } from 'react';
import axiosInstance from '../config/axios';
import './QuestionSolver.css';
import API_URL from '../config/api';
import { renderTextWithMath, processSolutionForMath, containsMathExpressions } from '../utils/MathProcessor';
import SideBySideDiagramRenderer from './SideBySideDiagramRenderer';

const QuestionSolver = ({ user, onLogout }) => {
  const [inputMethod, setInputMethod] = useState('paste'); // 'paste', 'text'
  const [questionText, setQuestionText] = useState('');
  const [pastedImage, setPastedImage] = useState(null);
  const [subject, setSubject] = useState('');
  const [solutionType, setSolutionType] = useState('step-by-step'); // 'step-by-step', 'high-level', 'with-diagram'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [solution, setSolution] = useState(null);
  const [loadingMessage, setLoadingMessage] = useState('Solving...');

  const handlePaste = async (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
      if (item.type.indexOf('image') !== -1) {
        const blob = item.getAsFile();
        if (blob) {
          setError('');
          
          const reader = new FileReader();
          reader.onload = (event) => {
            setPastedImage({
              blob: blob,
              preview: event.target.result,
              name: `pasted-image-${Date.now()}.png`,
              size: blob.size
            });
          };
          reader.readAsDataURL(blob);
          
          console.log('Image pasted from clipboard');
          break;
        }
      }
    }
  };

  const handleClearPastedImage = () => {
    setPastedImage(null);
  };

  const processSolutionText = (text) => {
    if (!text) return text;
    let processedText = processSolutionForMath(text);
    
    processedText = processedText.replace(
      /FINAL ANSWER:\s*\\boxed\{([^}]+)\}/gi,
      (match, content) => {
        return `FINAL ANSWER: $$\\boxed{${content}}$$`;
      }
    );
    
    processedText = processedText.replace(
      /FINAL ANSWER:\s*(.+?)(?=\n|$)/gi,
      (match, answer) => {
        if (answer.includes('\\') && !answer.includes('$')) {
          return `FINAL ANSWER: $$${answer}$$`;
        }
        return match;
      }
    );
    
    return processedText;
  };

  const handleSubmit = async () => {
    if (!subject) {
      setError('Please select a subject');
      return;
    }

    if (inputMethod === 'text' && !questionText.trim()) {
      setError('Please enter question text');
      return;
    }

    if (inputMethod === 'paste' && !pastedImage) {
      setError('Please paste an image first');
      return;
    }

    setLoading(true);
    setError('');
    setSolution(null);

    try {
      if (inputMethod === 'paste') {
        setLoadingMessage('Extracting text from image...');
        
        const formData = new FormData();
        formData.append('image', pastedImage.blob, pastedImage.name);
        formData.append('language', 'en,la');

        const ocrResponse = await axiosInstance.post(`${API_URL}/ocr/extract-text`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        if (!ocrResponse.data.success) {
          throw new Error(ocrResponse.data.error || 'Failed to extract text from image');
        }

        const extractedText = ocrResponse.data.text;
        setLoadingMessage('Solving question...');

        const solveResponse = await axiosInstance.post(`${API_URL}/solve-question`, {
          question_text: extractedText,
          subject: subject,
          solution_type: solutionType
        });

        if (solveResponse.data.success) {
          setSolution({
            questionText: extractedText,
            solution: solveResponse.data.solution,
            solver_type: solveResponse.data.solver_type,
            processing_time: solveResponse.data.processing_time_seconds,
            has_diagrams: solveResponse.data.has_diagrams || false,
            diagrams: solveResponse.data.diagrams || null,
            diagram_count: solveResponse.data.diagram_count || 0
          });
        } else {
          throw new Error(solveResponse.data.error || 'Failed to solve question');
        }
      } else if (inputMethod === 'text') {
        setLoadingMessage('Solving question...');

        const solveResponse = await axiosInstance.post(`${API_URL}/solve-question`, {
          question_text: questionText,
          subject: subject,
          solution_type: solutionType
        });

        if (solveResponse.data.success) {
          setSolution({
            questionText: questionText,
            solution: solveResponse.data.solution,
            solver_type: solveResponse.data.solver_type,
            processing_time: solveResponse.data.processing_time_seconds,
            has_diagrams: solveResponse.data.has_diagrams || false,
            diagrams: solveResponse.data.diagrams || null,
            diagram_count: solveResponse.data.diagram_count || 0
          });
        } else {
          throw new Error(solveResponse.data.error || 'Failed to solve question');
        }
      }
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.error || err.message || 'An error occurred');
    } finally {
      setLoading(false);
      setLoadingMessage('Solving...');
    }
  };

  const handleNewQuestion = () => {
    setSolution(null);
    setQuestionText('');
    setPastedImage(null);
    setSubject('');
    setError('');
  };

  const handleLogoutClick = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    onLogout();
  };

  return (
    <div className="question-solver-page">
      {/* Header */}
      <header className="solver-header">
        <div className="header-content">
          <h1 className="header-title">🎓 AI Question Solver</h1>
          <nav className="header-nav">
            <a href="/question-banks" className="nav-link">📚 Question Banks</a>
            <a href="/textbooks" className="nav-link">📖 Textbooks</a>
            <a href="/papers" className="nav-link">📄 Papers</a>
            <div className="user-menu">
              <span className="user-name">{user?.username || user?.email}</span>
              <button onClick={handleLogoutClick} className="logout-btn">
                🚪 Logout
              </button>
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="solver-main">
        <div className="solver-container">
          {/* Left Column: Input Section */}
          <div className="input-section">
            <h2 className="section-title">Submit Your Question</h2>
            
            {/* Tab Selector */}
            <div className="tab-selector">
              <button
                className={`tab-btn ${inputMethod === 'paste' ? 'active' : ''}`}
                onClick={() => setInputMethod('paste')}
              >
                📋 Paste Image
              </button>
              <button
                className={`tab-btn ${inputMethod === 'text' ? 'active' : ''}`}
                onClick={() => setInputMethod('text')}
              >
                ✍️ Text Input
              </button>
            </div>

            {/* Subject and Solution Type Selection */}
            <div className="form-row">
              <div className="form-group form-group-inline">
                <label className="form-label">Subject</label>
                <select
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="form-select"
                >
                  <option value="">Select subject...</option>
                  <option value="Mathematics">Mathematics</option>
                  <option value="Physics">Physics</option>
                  <option value="Chemistry">Chemistry</option>
                  <option value="Biology">Biology</option>
                  <option value="English">English</option>
                  <option value="History">History</option>
                  <option value="Geography">Geography</option>
                </select>
              </div>

              <div className="form-group form-group-inline">
                <label className="form-label">Solution Type</label>
                <select
                  value={solutionType}
                  onChange={(e) => setSolutionType(e.target.value)}
                  className="form-select"
                >
                  <option value="step-by-step">📝 Step-by-Step</option>
                  <option value="high-level">🎯 High-Level</option>
                  <option value="with-diagram">📊 With Diagram</option>
                </select>
              </div>

              <button
                onClick={handleSubmit}
                disabled={loading || !subject || (inputMethod === 'paste' && !pastedImage) || (inputMethod === 'text' && !questionText.trim())}
                className="submit-btn submit-btn-inline"
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    {loadingMessage}
                  </>
                ) : (
                  '✨ Solve'
                )}
              </button>
            </div>

            {/* Input Area */}
            <div className="input-area">
              {inputMethod === 'paste' ? (
                <div
                  className="paste-area"
                  onPaste={handlePaste}
                  tabIndex="0"
                >
                  {pastedImage ? (
                    <div className="image-preview">
                      <img src={pastedImage.preview} alt="Pasted" />
                      <button
                        onClick={handleClearPastedImage}
                        className="clear-image-btn"
                      >
                        ✕ Clear Image
                      </button>
                    </div>
                  ) : (
                    <div className="paste-placeholder">
                      <div className="paste-icon">📋</div>
                      <p>Press <kbd>Ctrl+V</kbd> to paste an image</p>
                      <p className="paste-hint">Or copy an image and paste it here</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-input-area">
                  <textarea
                    value={questionText}
                    onChange={(e) => setQuestionText(e.target.value)}
                    placeholder="Type or paste your question here..."
                    className="question-textarea"
                    rows={10}
                  />
                  <p className="char-count">{questionText.length} characters</p>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}
          </div>

          {/* Right Column: Solution Display */}
          <div className="solution-section">
            <h2 className="section-title">Solution</h2>
            
            {loading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>{loadingMessage}</p>
              </div>
            ) : solution ? (
              <div className="solution-display">
                {/* Question Display */}
                <div className="solution-question-box">
                  <h4>📝 Question:</h4>
                  <div className="question-text-math">
                    {containsMathExpressions(solution?.questionText) 
                      ? renderTextWithMath(solution?.questionText)
                      : solution?.questionText
                    }
                  </div>
                </div>

                {/* Solution Content */}
                <div className="solution-content">
                  {/* Use only the side-by-side renderer - no other text processing */}
                  <SideBySideDiagramRenderer 
                    solutionText={solution.solution}
                  />
                </div>

                {/* Metadata */}
                <div className="solution-metadata">
                  <span className="metadata-item">
                    ⏱️ Solved in {solution.processing_time?.toFixed(2)}s
                  </span>
                  <span className="metadata-item">
                    🤖 {solution.solver_type === 'intelligent' ? 'AI Solver' : 'Basic Solver'}
                  </span>
                  {solution.has_diagrams && (
                    <span className="metadata-item">
                      📊 {solution.diagram_count || solution.diagrams?.length || 0} Diagram(s)
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="solution-actions">
                  <button onClick={handleNewQuestion} className="action-btn primary">
                    ➕ New Question
                  </button>
                  <button className="action-btn secondary">
                    💾 Save Solution
                  </button>
                  <button className="action-btn secondary">
                    🔗 Share
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📝</div>
                <p>Submit a question to see the solution here</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default QuestionSolver;
