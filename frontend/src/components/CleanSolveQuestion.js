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

  // Function to get comprehensive diagram from backend service
  const getComprehensiveDiagram = async (solutionText) => {
    setDiagramLoading(true);
    try {
      // Call our new comprehensive diagram service
      const response = await axios.post('http://130.107.48.166:5002/analyze-diagrams', {
        solution_text: solutionText,
        question_text: questionText,
        subject: subject
      });
      
      if (response.data.success && response.data.diagram) {
        setDiagrams([response.data.diagram]); // Single unified diagram
      } else {
        // Fallback to test endpoint
        try {
          const testResponse = await axios.get('http://130.107.48.166:5002/test-diagram');
          if (testResponse.data.success && testResponse.data.diagram) {
            setDiagrams([testResponse.data.diagram]);
          }
        } catch (testErr) {
          console.log('Diagram service not available - no diagrams will be shown');
          setDiagrams([]);
        }
      }
    } catch (err) {
      console.log('Diagram service error:', err.message);
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
        
        // Get comprehensive diagram from backend service
        if (solutionType === 'with-diagram' || solutionType === 'step-by-step') {
          await getComprehensiveDiagram(response.data.solution);
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

  // Function to render backend-generated unified diagram
  const renderUnifiedDiagram = (diagram, index) => {
    return (
      <div key={index} className="unified-diagram-container">
        <div className="diagram-header">
          <span>🎨 {diagram.type === 'construction_sequence' ? 'Construction Sequence' : 
                   diagram.type === 'geometric_figure' ? 'Geometric Figure' : 
                   'Unified Diagram'}</span>
          <span className="diagram-type">{diagram.elements_count} Elements</span>
        </div>
        
        {/* Backend-generated SVG */}
        {diagram.svg && (
          <div 
            className="unified-diagram-svg"
            dangerouslySetInnerHTML={{ __html: diagram.svg }}
          />
        )}
        
        {/* Diagram description */}
        {diagram.description && (
          <div className="unified-diagram-description">
            <p><strong>📋 Description:</strong> {diagram.description}</p>
          </div>
        )}
        
        {/* Steps/Components list */}
        {(diagram.steps || diagram.components || diagram.parts) && (
          <div className="diagram-elements-list">
            <h5>📝 {diagram.steps ? 'Construction Steps:' : 
                    diagram.components ? 'Components:' : 
                    'Parts:'}</h5>
            <ul>
              {(diagram.steps || diagram.components || diagram.parts).map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
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
                <h4>🎨 Backend-Generated Unified Diagram:</h4>
                
                {diagramLoading ? (
                  <div className="diagram-loading">
                    <div className="loading-spinner"></div>
                    <p>Analyzing solution and generating comprehensive diagram...</p>
                  </div>
                ) : diagrams.length > 0 ? (
                  <div className="unified-diagrams">
                    {diagrams.map((diagram, index) => renderUnifiedDiagram(diagram, index))}
                  </div>
                ) : (
                  <div className="no-diagrams">
                    <div className="empty-diagram-icon">🎨</div>
                    <h5>No Backend Diagram Available</h5>
                    <p>The comprehensive diagram service is not running or no diagram elements were found in the solution.</p>
                    <p className="service-info">Service: http://130.107.48.166:5002/analyze-diagrams</p>
                    
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
                      <p className="fallback-caption">This is a sample diagram. Backend-generated unified diagrams will appear when the diagram service is running.</p>
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
