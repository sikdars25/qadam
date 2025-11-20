import React, { useState } from 'react';
import axiosInstance from '../config/axios';
import './DashboardQuestionSolver.css';
import API_URL from '../config/api';
import { renderTextWithMath, processSolutionForMath } from '../utils/MathProcessor';

const DashboardQuestionSolver = () => {
  const [inputMethod, setInputMethod] = useState('paste'); // 'paste', 'text'
  const [questionText, setQuestionText] = useState('');
  const [pastedImage, setPastedImage] = useState(null);
  const [subject, setSubject] = useState('');
  const [solutionType, setSolutionType] = useState('step-by-step');
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

        if (ocrResponse.data.success) {
          setQuestionText(ocrResponse.data.text);
          setLoadingMessage('Generating solution...');

          const solveResponse = await axiosInstance.post(`${API_URL}/solve-question`, {
            question_text: ocrResponse.data.text,
            subject: subject,
            solution_type: solutionType
          });

          if (solveResponse.data.success) {
            const processedSolution = processSolutionText(solveResponse.data.solution);
            setSolution({
              text: processedSolution,
              question: ocrResponse.data.text
            });
          }
        }
      } else {
        setLoadingMessage('Generating solution...');

        const solveResponse = await axiosInstance.post(`${API_URL}/solve-question`, {
          question_text: questionText,
          subject: subject,
          solution_type: solutionType
        });

        if (solveResponse.data.success) {
          const processedSolution = processSolutionText(solveResponse.data.solution);
          setSolution({
            text: processedSolution,
            question: questionText
          });
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

  return (
    <div className="dashboard-question-solver">
      <div className="solver-grid">
        {/* Left Panel: Question Input */}
        <div className="question-panel">
          <h3 className="panel-title">📝 Submit Question</h3>
          
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

          {/* Controls Row */}
          <div className="controls-row">
            <div className="control-group">
              <label>Subject</label>
              <select value={subject} onChange={(e) => setSubject(e.target.value)}>
                <option value="">Select...</option>
                <option value="Mathematics">Mathematics</option>
                <option value="Physics">Physics</option>
                <option value="Chemistry">Chemistry</option>
                <option value="Biology">Biology</option>
                <option value="English">English</option>
                <option value="History">History</option>
                <option value="Geography">Geography</option>
              </select>
            </div>

            <div className="control-group">
              <label>Solution Type</label>
              <select value={solutionType} onChange={(e) => setSolutionType(e.target.value)}>
                <option value="step-by-step">📝 Step-by-Step</option>
                <option value="high-level">🎯 High-Level</option>
                <option value="with-diagram">📊 With Diagram</option>
              </select>
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading || !subject || (inputMethod === 'paste' && !pastedImage) || (inputMethod === 'text' && !questionText.trim())}
              className="solve-btn"
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
          <div className="input-area-large">
            {inputMethod === 'paste' ? (
              <div
                className="paste-area-large"
                onPaste={handlePaste}
                tabIndex="0"
              >
                {pastedImage ? (
                  <div className="image-preview-large">
                    <img src={pastedImage.preview} alt="Pasted" />
                    <button onClick={handleClearPastedImage} className="clear-btn">
                      ✕ Clear
                    </button>
                  </div>
                ) : (
                  <div className="paste-placeholder-large">
                    <div className="paste-icon">📋</div>
                    <p>Press <kbd>Ctrl+V</kbd> to paste an image</p>
                    <p className="hint">Or copy an image and paste it here</p>
                  </div>
                )}
              </div>
            ) : (
              <textarea
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value)}
                placeholder="Type or paste your question here..."
                className="question-textarea-large"
              />
            )}
          </div>

          {error && <div className="error-msg">⚠️ {error}</div>}
        </div>

        {/* Right Panel: Solution Display */}
        <div className="solution-panel">
          <h3 className="panel-title">💡 Solution</h3>
          
          {loading ? (
            <div className="loading-display">
              <div className="loading-spinner-large"></div>
              <p>{loadingMessage}</p>
            </div>
          ) : solution ? (
            <div className="solution-display">
              <div className="question-box">
                <h4>Question:</h4>
                <div className="question-text">{renderTextWithMath(solution.question)}</div>
              </div>
              
              <div className="solution-content">
                <div className="solution-text">
                  {renderTextWithMath(solution.text)}
                </div>
              </div>

              <div className="solution-actions">
                <button onClick={handleNewQuestion} className="action-btn primary">
                  ✨ New Question
                </button>
                <button className="action-btn secondary">
                  💾 Save to Bank
                </button>
              </div>
            </div>
          ) : (
            <div className="empty-display">
              <div className="empty-icon">🤔</div>
              <p>Submit a question to see the solution here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardQuestionSolver;
