import React, { useState } from 'react';
import axios from 'axios';
import './SingleQuestionUpload.css';
import API_URL from '../config/api';

const SingleQuestionUpload = ({ onClose, onQuestionParsed }) => {
  const [inputMethod, setInputMethod] = useState('paste'); // 'paste', 'text' - Paste Image is default
  const [questionText, setQuestionText] = useState('');
  const [pastedImage, setPastedImage] = useState(null);
  const [subject, setSubject] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parsedQuestion, setParsedQuestion] = useState(null);
  const [solution, setSolution] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [solving, setSolving] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Solving...');

  const handlePaste = async (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
      if (item.type.indexOf('image') !== -1) {
        const blob = item.getAsFile();
        if (blob) {
          setPastedImage(blob);
          setError('');
          
          // Create preview URL
          const reader = new FileReader();
          reader.onload = (event) => {
            // Store the data URL for preview
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
      setError('Please paste an image (Ctrl+V or Cmd+V)');
      return;
    }

    setLoading(true);
    setSolving(true);
    setError('');

    try {
      let questionToSolve = questionText;

      // If image input, extract text using OCR first
      if (inputMethod === 'paste' && pastedImage) {
        // Step 1: Extract text from image using OCR
        setLoadingMessage('Extracting text from image...');
        
        const ocrFormData = new FormData();
        ocrFormData.append('file', pastedImage.blob, pastedImage.name);
        ocrFormData.append('input_type', 'file');
        ocrFormData.append('file_type', 'png');

        const ocrResponse = await axios.post(`${API_URL}/api/parse-single-question`, ocrFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        if (ocrResponse.data.success && ocrResponse.data.question) {
          questionToSolve = ocrResponse.data.question.question_text;
          console.log('Extracted text from image:', questionToSolve);
        } else {
          setError('Failed to extract text from image. Please try typing the question instead.');
          setLoading(false);
          setSolving(false);
          return;
        }
      }

      // Step 2: Solve the question using the extracted or typed text
      setLoadingMessage('Solving question...');
      
      const response = await axios.post(`${API_URL}/api/solve-question`, {
        question_text: questionToSolve,
        question_type: 'unknown',
        subject: subject,
        chapter_context: null
      });

      if (response.data.success) {
        const solutionData = {
          questionText: questionToSolve,
          solution: response.data.solution,
          parsedSolution: response.data.parsed_solution
        };
        setSolution(solutionData);
        setParsedQuestion({ question_text: questionToSolve });
        
        // Step 3: Save to Question Bank
        try {
          await axios.post(`${API_URL}/api/save-solved-question`, {
            question_text: questionToSolve,
            solution: response.data.solution,
            subject: subject,
            source: 'solve_one',
            timestamp: new Date().toISOString()
          });
          console.log('Question saved to Question Bank with subject:', subject);
        } catch (saveErr) {
          console.error('Failed to save to Question Bank:', saveErr);
          // Don't show error to user, just log it
        }
        
        if (onQuestionParsed) {
          onQuestionParsed({ question_text: questionToSolve });
        }
      } else {
        setError(response.data.error || 'Failed to solve question');
      }
    } catch (err) {
      console.error('Error solving question:', err);
      setError('Error: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
      setSolving(false);
    }
  };

  const handleReset = () => {
    setQuestionText('');
    setPastedImage(null);
    setSubject('');
    setParsedQuestion(null);
    setSolution(null);
    setError('');
  };

  const handleDownload = () => {
    if (!solution) return;
    
    // Create formatted text content
    const content = `QUESTION:\n${solution.questionText}\n\n${'='.repeat(60)}\n\nSOLUTION:\n\n${solution.solution}\n\n${'='.repeat(60)}\n\nGenerated by Academic Portal`;
    
    // Create blob and download
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `solution_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleWhatsApp = () => {
    if (!solution) return;
    
    // Create formatted message for WhatsApp
    const message = `*QUESTION:*\n${solution.questionText}\n\n*SOLUTION:*\n${solution.solution}\n\n_Generated by Academic Portal_`;
    
    // Encode message for URL
    const encodedMessage = encodeURIComponent(message);
    
    // Open WhatsApp with pre-filled message
    window.open(`https://wa.me/?text=${encodedMessage}`, '_blank');
  };

  return (
    <div className="single-question-modal">
      <div className="single-question-modal-content">
        <div className="single-question-header">
          <h2>✨ Solve One Question</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {!parsedQuestion ? (
          <>
            <div className="input-method-selector">
              <button
                className={`method-btn ${inputMethod === 'paste' ? 'active' : ''}`}
                onClick={() => setInputMethod('paste')}
              >
                📋 Paste Image
              </button>
              <button
                className={`method-btn ${inputMethod === 'text' ? 'active' : ''}`}
                onClick={() => setInputMethod('text')}
              >
                ✍️ Text Input
              </button>
            </div>

            <div className="subject-selector">
              <label htmlFor="subject">Subject: <span className="required">*</span></label>
              <select
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="subject-dropdown"
              >
                <option value="">-- Select Subject --</option>
                <option value="Physics">Physics</option>
                <option value="Chemistry">Chemistry</option>
                <option value="Biology">Biology</option>
                <option value="Mathematics">Mathematics</option>
              </select>
            </div>

            {inputMethod === 'text' && (
              <div className="text-input-section">
                <label>Enter Question Text:</label>
                <textarea
                  value={questionText}
                  onChange={(e) => setQuestionText(e.target.value)}
                  placeholder="Type or paste your question here...&#10;&#10;Example:&#10;1. What is the capital of France?&#10;(A) London&#10;(B) Paris&#10;(C) Berlin&#10;(D) Madrid"
                  rows={12}
                  className="question-textarea"
                />
                <div className="char-count">
                  {questionText.length} characters
                </div>
              </div>
            )}

            {inputMethod === 'paste' && (
              <div className="paste-input-section">
                <div 
                  className="paste-area"
                  onPaste={handlePaste}
                  tabIndex={0}
                >
                  {!pastedImage ? (
                    <>
                      <div className="paste-icon">📋</div>
                      <div className="paste-instruction">
                        Press <kbd>Ctrl+V</kbd> (or <kbd>Cmd+V</kbd> on Mac) to paste an image
                      </div>
                      <div className="paste-hint">
                        Take a screenshot or copy an image, then paste it here
                      </div>
                    </>
                  ) : (
                    <div className="pasted-image-preview">
                      <img 
                        src={pastedImage.preview} 
                        alt="Pasted question" 
                        className="preview-image"
                      />
                      <div className="pasted-image-info">
                        <div className="pasted-image-name">📷 {pastedImage.name}</div>
                        <div className="pasted-image-size">
                          {(pastedImage.size / 1024).toFixed(2)} KB
                        </div>
                      </div>
                      <button 
                        className="clear-pasted-btn"
                        onClick={handleClearPastedImage}
                      >
                        ✕ Clear Image
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {error && (
              <div className="error-message">
                ⚠️ {error}
              </div>
            )}

            <div className="action-buttons">
              <button
                className="submit-btn"
                onClick={handleSubmit}
                disabled={loading || !subject || (inputMethod === 'text' && !questionText.trim()) || (inputMethod === 'paste' && !pastedImage)}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    {loadingMessage}
                  </>
                ) : (
                  <>
                    ✨ Solve
                  </>
                )}
              </button>
              <button className="cancel-btn" onClick={onClose}>
                Cancel
              </button>
            </div>
          </>
        ) : (
          <div className="parsed-result">
            <div className="result-header">
              <h3>✨ Solution</h3>
            </div>

            {/* Question Display */}
            <div className="solution-question-box">
              <h4>📝 Question:</h4>
              <p>{solution?.questionText}</p>
            </div>

            {/* Solution Display */}
            {solution && (
              <div className="solution-content">
                {(() => {
                  const lines = solution.solution.split('\n');
                  let inDiagram = false;
                  let diagramLines = [];
                  let lastWasEmpty = false;
                  let lastWasSection = false;
                  let currentSection = null;
                  const elements = [];
                  
                  lines.forEach((line, idx) => {
                    // Detect ASCII art diagram patterns (box drawing characters)
                    /* eslint-disable no-useless-escape */
                    const isAsciiArt = line.match(/^[\s]*[\+\-\|\/\\<>]+[\s\+\-\|\/\\<>]*$/) || 
                                      line.match(/^[\s]*[\+\-\|]{3,}/) ||
                                      line.match(/[\+\-]{5,}/) ||
                    /* eslint-enable no-useless-escape */
                                      (line.includes('|') && line.includes('+'));
                    
                    // Detect diagram start/end
                    if (line.match(/^\*\*Diagram/i) || line.includes('```') || (!inDiagram && isAsciiArt)) {
                      if (!inDiagram) {
                        // Starting a diagram
                        inDiagram = true;
                        if (isAsciiArt) {
                          diagramLines.push(line);
                        }
                      } else {
                        // Ending a diagram
                        if (line.includes('```') || line.match(/^\*\*Diagram/i)) {
                          inDiagram = false;
                        } else if (isAsciiArt) {
                          diagramLines.push(line);
                        } else {
                          // End of ASCII art
                          inDiagram = false;
                        }
                        
                        if (!inDiagram && diagramLines.length > 0) {
                          const diagram = diagramLines.join('\n');
                          diagramLines = [];
                          elements.push(<pre key={idx} className="solution-diagram">{diagram}</pre>);
                          lastWasEmpty = false;
                          lastWasSection = true;
                        }
                      }
                      return;
                    }
                    
                    // Collect diagram lines
                    if (inDiagram) {
                      diagramLines.push(line);
                      return;
                    }
                    
                    // Highlight section headers
                    if (line.match(/^\*\*.*\*\*:?$/)) {
                      const sectionName = line.replace(/\*\*/g, '').replace(/:/g, '').trim().toLowerCase();
                      currentSection = sectionName;
                      elements.push(<h4 key={idx} className="solution-section-header">{line.replace(/\*\*/g, '').replace(/:/g, '')}</h4>);
                      lastWasEmpty = false;
                      lastWasSection = true;
                      return;
                    }
                    
                    // Highlight final answer
                    if (line.match(/FINAL ANSWER:/i)) {
                      elements.push(
                        <div key={idx} className="final-answer-box">
                          <div className="final-answer-icon">🎯</div>
                          <div className="final-answer-text" dangerouslySetInnerHTML={{
                            __html: line.replace(/FINAL ANSWER:/i, '').trim()
                          }}></div>
                        </div>
                      );
                      lastWasEmpty = false;
                      lastWasSection = true;
                      return;
                    }
                    
                    // Highlight step numbers
                    if (line.match(/^(Step \d+:|^\d+\.)/)) {
                      elements.push(
                        <div key={idx} className="solution-step" dangerouslySetInnerHTML={{
                          __html: line
                        }}></div>
                      );
                      lastWasEmpty = false;
                      lastWasSection = false;
                      return;
                    }
                    
                    // Handle empty lines
                    if (!line.trim()) {
                      const compactSections = ['given', 'find', 'formula', 'concept', 'formula/concept'];
                      const isCompactSection = compactSections.some(s => currentSection && currentSection.includes(s));
                      
                      if (!lastWasEmpty && lastWasSection && !isCompactSection) {
                        elements.push(<div key={idx} className="section-spacer"></div>);
                        lastWasEmpty = true;
                      }
                      return;
                    }
                    
                    // Regular text
                    const compactSections = ['given', 'find', 'formula', 'concept', 'formula/concept'];
                    const isCompactSection = compactSections.some(s => currentSection && currentSection.includes(s));
                    const textClass = isCompactSection ? 'solution-text compact' : 'solution-text';
                    
                    elements.push(
                      <p key={idx} className={textClass} dangerouslySetInnerHTML={{
                        __html: line
                      }}></p>
                    );
                    lastWasEmpty = false;
                    lastWasSection = false;
                  });
                  
                  return elements;
                })()}
              </div>
            )}

            <div className="result-actions">
              <div className="action-buttons-row">
                <button className="download-btn" onClick={handleDownload}>
                  📥 Download
                </button>
                <button className="whatsapp-btn" onClick={handleWhatsApp}>
                  📱 WhatsApp
                </button>
              </div>
              <div className="action-buttons-row">
                <button className="parse-another-btn" onClick={handleReset}>
                  ✨ Solve Another Question
                </button>
                <button className="close-result-btn" onClick={onClose}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SingleQuestionUpload;
