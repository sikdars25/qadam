import React, { useState } from 'react';
import './CleanSolveQuestion.css';
import axiosInstance from '../config/axios';
import axios from 'axios';
import API_URL from '../config/api';

const CleanSolveQuestion = ({ user, onLogout }) => {
  const [questionText, setQuestionText] = useState('');
  const [subject, setSubject] = useState('Mathematics');
  const [solutionType, setSolutionType] = useState('step-by-step');
  const [showSolution, setShowSolution] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiSolution, setAiSolution] = useState(null);
  const [diagrams, setDiagrams] = useState([]);
  const [diagramLoading, setDiagramLoading] = useState(false);

  // Function to extract diagrams from solution text
  const extractDiagramsFromText = (solutionText) => {
    if (!solutionText) return [];
    
    const diagramRegex = /\[DIAGRAM:\s*([^\]]+)\]/g;
    const diagrams = [];
    let match;
    
    while ((match = diagramRegex.exec(solutionText)) !== null) {
      diagrams.push({
        type: 'text-based',
        description: match[1].trim(),
        text: match[1].trim()
      });
    }
    
    return diagrams;
  };

  // Function to get diagrams from separate endpoint
  const getDiagrams = async () => {
    setDiagramLoading(true);
    try {
      const response = await axios.post('http://130.107.48.166:5001/generate-diagrams', {
        question_text: questionText,
        subject: subject
      });
      
      if (response.data.success) {
        setDiagrams(response.data.diagrams || []);
      } else {
        // Try test endpoint if main fails
        try {
          const testResponse = await axios.get('http://130.107.48.166:5001/test-diagram');
          if (testResponse.data.success) {
            setDiagrams(testResponse.data.diagrams);
          }
        } catch (testErr) {
          console.log('Diagram endpoint not available - using text extraction');
          setDiagrams([]);
        }
      }
    } catch (err) {
      console.log('Diagram endpoint error:', err.message);
      setDiagrams([]);
    } finally {
      setDiagramLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!questionText.trim()) {
      setError('Please enter a question');
      return;
    }
    
    setLoading(true);
    setError('');
    setDiagrams([]);
    
    try {
      // Call AI service for text solution
      const response = await axiosInstance.post('/solve-question', {
        question_text: questionText,
        subject: subject,
        solution_type: solutionType
      });
      
      if (response.data.success) {
        setAiSolution(response.data);
        
        // Extract diagrams from the solution text
        const textDiagrams = extractDiagramsFromText(response.data.solution);
        
        // Also try to get diagrams from separate endpoint if needed
        if (solutionType === 'with-diagram' && textDiagrams.length === 0) {
          await getDiagrams();
        } else {
          // Use diagrams extracted from text
          setDiagrams(textDiagrams);
        }
        
        setShowSolution(true);
      } else {
        setError(response.data.error || 'Failed to get solution');
      }
    } catch (err) {
      console.error('AI Service Error:', err);
      setError('Error connecting to AI service. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setQuestionText('');
    setShowSolution(false);
    setLoading(false);
    setError('');
    setAiSolution(null);
    setDiagrams([]);
    setDiagramLoading(false);
  };

  // Function to generate appropriate SVG based on diagram description
  const generateDiagramSVG = (description) => {
    const desc = description.toLowerCase();
    
    // Line segment with length
    if (desc.includes('line segment') && desc.includes('length')) {
      const lengthMatch = desc.match(/(\d+(?:\.\d+)?)\s*cm/);
      const length = lengthMatch ? lengthMatch[1] : '6';
      
      return `
        <svg width="300" height="120" viewBox="0 0 300 120" xmlns="http://www.w3.org/2000/svg">
          <line x1="50" y1="60" x2="250" y2="60" stroke="#333" stroke-width="2"/>
          <circle cx="50" cy="60" r="4" fill="#dc3545"/>
          <circle cx="250" cy="60" r="4" fill="#dc3545"/>
          <text x="40" y="55" font-size="14" font-weight="bold" fill="#333">B</text>
          <text x="260" y="55" font-size="14" font-weight="bold" fill="#333">C</text>
          <text x="135" y="50" font-size="12" fill="#007bff">${length} cm</text>
          <path d="M 50 65 L 250 65" stroke="#007bff" stroke-width="1"/>
          <path d="M 245 60 L 250 65 L 245 70" stroke="#007bff" stroke-width="1" fill="none"/>
        </svg>
      `;
    }
    
    // Line segment with angles
    if (desc.includes('line segment') && (desc.includes('angle') || desc.includes('measurements'))) {
      return `
        <svg width="300" height="150" viewBox="0 0 300 150" xmlns="http://www.w3.org/2000/svg">
          <line x1="50" y1="75" x2="250" y2="75" stroke="#333" stroke-width="2"/>
          <circle cx="50" cy="75" r="4" fill="#dc3545"/>
          <circle cx="250" cy="75" r="4" fill="#dc3545"/>
          <text x="40" y="70" font-size="14" font-weight="bold" fill="#333">B</text>
          <text x="260" y="70" font-size="14" font-weight="bold" fill="#333">C</text>
          
          <!-- Angle at B -->
          <path d="M 70 75 Q 70 55 90 55" stroke="#28a745" stroke-width="1.5" fill="none"/>
          <text x="75" y="50" font-size="11" fill="#28a745">∠B</text>
          
          <!-- Angle at C -->
          <path d="M 230 75 Q 230 55 210 55" stroke="#28a745" stroke-width="1.5" fill="none"/>
          <text x="215" y="50" font-size="11" fill="#28a745">∠C</text>
        </svg>
      `;
    }
    
    // Triangle
    if (desc.includes('triangle')) {
      return `
        <svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
          <polygon points="150,40 80,160 220,160" fill="none" stroke="#333" stroke-width="2"/>
          <circle cx="150" cy="40" r="4" fill="#dc3545"/>
          <circle cx="80" cy="160" r="4" fill="#dc3545"/>
          <circle cx="220" cy="160" r="4" fill="#dc3545"/>
          <text x="145" y="35" font-size="14" font-weight="bold" fill="#333">A</text>
          <text x="70" y="175" font-size="14" font-weight="bold" fill="#333">B</text>
          <text x="225" y="175" font-size="14" font-weight="bold" fill="#333">C</text>
        </svg>
      `;
    }
    
    // Perpendicular bisector
    if (desc.includes('perpendicular') || desc.includes('bisector')) {
      return `
        <svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
          <line x1="50" y1="100" x2="250" y2="100" stroke="#333" stroke-width="2"/>
          <line x1="150" y1="50" x2="150" y2="150" stroke="#007bff" stroke-width="2"/>
          
          <circle cx="50" cy="100" r="4" fill="#dc3545"/>
          <circle cx="250" cy="100" r="4" fill="#dc3545"/>
          <circle cx="150" cy="100" r="4" fill="#007bff"/>
          
          <text x="40" y="95" font-size="14" font-weight="bold" fill="#333">P</text>
          <text x="260" y="95" font-size="14" font-weight="bold" fill="#333">Q</text>
          <text x="155" y="45" font-size="14" font-weight="bold" fill="#007bff">M</text>
          
          <!-- Right angle indicator -->
          <rect x="140" y="90" width="20" height="20" fill="none" stroke="#007bff" stroke-width="1"/>
        </svg>
      `;
    }
    
    // Circle with center
    if (desc.includes('circle') || desc.includes('circumcenter')) {
      return `
        <svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
          <circle cx="150" cy="100" r="60" fill="none" stroke="#333" stroke-width="2"/>
          <circle cx="150" cy="100" r="3" fill="#dc3545"/>
          <text x="145" y="95" font-size="14" font-weight="bold" fill="#333">O</text>
          
          <!-- Points on circle -->
          <circle cx="150" cy="40" r="4" fill="#007bff"/>
          <circle cx="210" cy="100" r="4" fill="#007bff"/>
          <circle cx="150" cy="160" r="4" fill="#007bff"/>
          <circle cx="90" cy="100" r="4" fill="#007bff"/>
          
          <text x="145" y="35" font-size="12" font-weight="bold" fill="#007bff">A</text>
          <text x="220" y="105" font-size="12" font-weight="bold" fill="#007bff">B</text>
          <text x="145" y="175" font-size="12" font-weight="bold" fill="#007bff">C</text>
          <text x="75" y="105" font-size="12" font-weight="bold" fill="#007bff">D</text>
        </svg>
      `;
    }
    
    // Default construction
    return `
      <svg width="300" height="150" viewBox="0 0 300 150" xmlns="http://www.w3.org/2000/svg">
        <line x1="50" y1="75" x2="250" y2="75" stroke="#333" stroke-width="2"/>
        <circle cx="50" cy="75" r="4" fill="#dc3545"/>
        <circle cx="250" cy="75" r="4" fill="#dc3545"/>
        <text x="40" y="70" font-size="14" font-weight="bold" fill="#333">A</text>
        <text x="260" y="70" font-size="14" font-weight="bold" fill="#333">B</text>
      </svg>
    `;
  };

  // Function to render individual diagrams
  const renderDiagram = (diagram, index) => {
    return (
      <div key={index} className="diagram-card">
        <div className="diagram-header">
          <span>📐 Diagram {index + 1}</span>
          <span className="diagram-type">{diagram.type || 'AI Generated'}</span>
        </div>
        
        {diagram.svg && (
          <div 
            className="svg-diagram" 
            dangerouslySetInnerHTML={{ __html: diagram.svg }}
          />
        )}
        
        {diagram.ascii && (
          <div className="ascii-diagram">
            <pre>{diagram.ascii}</pre>
          </div>
        )}
        
        {diagram.text && (
          <div className="text-diagram">
            <div className="diagram-text-content">
              <h5>📝 Diagram Description:</h5>
              <p>{diagram.text}</p>
            </div>
            {/* Smart visual representation based on description */}
            <div className="smart-visual">
              <div 
                className="generated-diagram"
                dangerouslySetInnerHTML={{ __html: generateDiagramSVG(diagram.text) }}
              />
            </div>
          </div>
        )}
        
        {diagram.description && (
          <div className="diagram-description">
            <p><strong>Details:</strong> {diagram.description}</p>
          </div>
        )}
      </div>
    );
  };

  if (showSolution) {
    return (
      <div className="clean-solve-container">
        <div className="solution-header">
          <h2>📊 Solution Preview</h2>
          <button onClick={handleReset} className="reset-btn">
            🔄 New Question
          </button>
        </div>

        <div className="two-column-solution">
          {/* Left Column - Text Solution */}
          <div className="text-column">
            <div className="column-header">
              <h3>📝 Step-by-Step Solution</h3>
              <span className="subject-badge">{subject}</span>
            </div>
            <div className="text-content">
              <div className="question-display">
                <h4>❓ Question:</h4>
                <p className="question-text">{aiSolution?.questionText || questionText}</p>
              </div>
              
              <div className="solution-steps">
                <h4>📋 Solution Steps:</h4>
                {aiSolution?.solution ? (
                  aiSolution.solution.split('\n').map((line, index) => {
                    if (line.trim()) {
                      // Check if it's a step (starts with number or bullet)
                      if (/^\d+\.|^[•\-\*]/.test(line.trim())) {
                        return (
                          <div key={index} className="step">
                            <span className="step-number">{line.trim().charAt(0)}</span>
                            <p>{line.trim().substring(2).trim()}</p>
                          </div>
                        );
                      } else if (line.trim().toLowerCase().includes('answer:') || 
                                 line.trim().toLowerCase().includes('solution:') ||
                                 line.trim().toLowerCase().includes('therefore')) {
                        return (
                          <div key={index} className="final-answer">
                            <h4>✅ Final Answer:</h4>
                            <p className="answer-text">{line.trim()}</p>
                          </div>
                        );
                      } else {
                        return (
                          <div key={index} className="step">
                            <span className="step-number">{index + 1}</span>
                            <p>{line.trim()}</p>
                          </div>
                        );
                      }
                    }
                    return null;
                  })
                ) : (
                  <div className="step">
                    <span className="step-number">1.</span>
                    <p>Analyzing the question and identifying key information...</p>
                  </div>
                )}
              </div>

              {!aiSolution?.solution && (
                <div className="processing-info">
                  <h4>⏳ Processing Information:</h4>
                  <p>Solution Type: <strong>{solutionType}</strong></p>
                  <p>Subject: <strong>{subject}</strong></p>
                  <p>Processing Time: <strong>{aiSolution?.processing_time?.toFixed(2)}s</strong></p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Diagram */}
          <div className="diagram-column">
            <div className="column-header">
              <h3>📐 Construction Diagrams</h3>
              <span className="diagram-badge">
                {diagramLoading ? 'Loading...' : `${diagrams.length} Diagram(s)`}
              </span>
            </div>
            <div className="diagram-content">
              <div className="diagram-container">
                <h4>🎨 Visual Representation:</h4>
                
                {diagramLoading ? (
                  <div className="diagram-loading">
                    <div className="loading-spinner"></div>
                    <p>Generating diagrams...</p>
                  </div>
                ) : diagrams.length > 0 ? (
                  <div className="diagrams-list">
                    {diagrams.map((diagram, index) => renderDiagram(diagram, index))}
                  </div>
                ) : (
                  <div className="no-diagrams">
                    <div className="empty-diagram-icon">📐</div>
                    <h5>No Diagrams Available</h5>
                    <p>Try selecting "📊 Solution with Diagram" for visual representations.</p>
                    
                    {/* Show fallback sine wave */}
                    <div className="fallback-diagram">
                      <h6>Sample Mathematical Diagram:</h6>
                      <div className="sine-wave-diagram">
                        <svg width="100%" height="250" viewBox="0 0 400 250" className="sine-svg">
                          <defs>
                            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                              <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e0e0" strokeWidth="1"/>
                            </pattern>
                          </defs>
                          <rect width="100%" height="100%" fill="url(#grid)" />
                          
                          <line x1="50" y1="125" x2="350" y2="125" stroke="#333" strokeWidth="2"/>
                          <line x1="200" y1="50" x2="200" y2="200" stroke="#333" strokeWidth="2"/>
                          
                          <polygon points="350,125 340,120 340,130" fill="#333"/>
                          <polygon points="200,50 195,60 205,60" fill="#333"/>
                          
                          <path d="M 50,125 Q 100,75 150,125 T 250,125 T 350,125" 
                                fill="none" stroke="#007bff" strokeWidth="3"/>
                          
                          <text x="360" y="130" fontSize="12" fill="#333">x</text>
                          <text x="205" y="45" fontSize="12" fill="#333">y</text>
                          <text x="190" y="220" fontSize="12" fill="#333">0</text>
                          
                          <circle cx="50" cy="125" r="4" fill="#dc3545"/>
                          <circle cx="100" cy="100" r="4" fill="#dc3545"/>
                          <circle cx="150" cy="125" r="4" fill="#dc3545"/>
                          <circle cx="200" cy="150" r="4" fill="#dc3545"/>
                          <circle cx="250" cy="125" r="4" fill="#dc3545"/>
                          <circle cx="300" cy="100" r="4" fill="#dc3545"/>
                          <circle cx="350" cy="125" r="4" fill="#dc3545"/>
                        </svg>
                      </div>
                      <p className="fallback-caption">This is a sample diagram. Real diagrams will appear when you select "Solution with Diagram".</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="clean-solve-container">
      <div className="header">
        <h2>🎯 Solve Question</h2>
        <p>Enter your question below to see a sample two-column solution layout</p>
      </div>

      <form onSubmit={handleSubmit} className="question-form">
        {/* Error Display */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="subject">Subject:</label>
          <select
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="subject-select"
          >
            <option value="Mathematics">Mathematics</option>
            <option value="Physics">Physics</option>
            <option value="Chemistry">Chemistry</option>
            <option value="Biology">Biology</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="solutionType">Solution Type:</label>
          <select
            id="solutionType"
            value={solutionType}
            onChange={(e) => setSolutionType(e.target.value)}
            className="subject-select"
          >
            <option value="step-by-step">📝 Step-by-Step Solution</option>
            <option value="high-level">🎯 High-Level Overview</option>
            <option value="with-diagram">📊 Solution with Diagram</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="question">Question:</label>
          <textarea
            id="question"
            value={questionText}
            onChange={(e) => setQuestionText(e.target.value)}
            placeholder="Enter your question here... (e.g., 'Find the area of a triangle with base 6cm and height 4cm')"
            className="question-textarea"
            rows={8}
            required
          />
          <div className="char-count">
            {questionText.length} characters
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? '⏳ Processing...' : '🚀 Get AI Solution'}
          </button>
          <button type="button" onClick={() => setQuestionText('')} className="clear-btn">
            🗑️ Clear
          </button>
        </div>
      </form>
    </div>
  );
};

export default CleanSolveQuestion;
