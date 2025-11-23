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

  // Function to generate connected SVG diagram sequence
  const generateConnectedDiagramSequence = (diagrams, questionText) => {
    if (!diagrams || diagrams.length === 0) return null;
    
    // Create a connected construction sequence
    const svgWidth = 400;
    const svgHeight = 250;
    const stepSpacing = 80;
    const startX = 50;
    const startY = 125;
    
    let svgContent = `<svg width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">`;
    
    // Add title
    svgContent += `<text x="${svgWidth/2}" y="25" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">Construction Sequence</text>`;
    
    // Add question reference
    svgContent += `<text x="${svgWidth/2}" y="45" font-size="12" fill="#666" text-anchor="middle" font-style="italic">For: ${questionText.substring(0, 50)}${questionText.length > 50 ? '...' : ''}</text>`;
    
    // Process each diagram and create connected elements
    diagrams.forEach((diagram, index) => {
      const x = startX + (index * stepSpacing);
      const desc = diagram.text.toLowerCase();
      
      // Connection line from previous step
      if (index > 0) {
        svgContent += `<line x1="${x - stepSpacing + 20}" y1="${startY}" x2="${x - 20}" y2="${startY}" stroke="#007bff" stroke-width="2" stroke-dasharray="5,5"/>`;
        svgContent += `<text x="${x - stepSpacing/2}" y="${startY - 10}" font-size="10" fill="#007bff" text-anchor="middle">Step ${index}</text>`;
      }
      
      // Generate specific construction based on description
      if (desc.includes('line segment') && desc.includes('length')) {
        const lengthMatch = desc.match(/(\d+(?:\.\d+)?)\s*cm/);
        const length = lengthMatch ? lengthMatch[1] : '6';
        
        svgContent += `
          <g transform="translate(${x - 30}, ${startY - 30})">
            <line x1="0" y1="30" x2="60" y2="30" stroke="#333" stroke-width="2"/>
            <circle cx="0" cy="30" r="3" fill="#dc3545"/>
            <circle cx="60" cy="30" r="3" fill="#dc3545"/>
            <text x="-5" y="25" font-size="10" font-weight="bold" fill="#333">${index === 0 ? 'B' : 'P'}</text>
            <text x="65" y="25" font-size="10" font-weight="bold" fill="#333">${index === 0 ? 'C' : 'Q'}</text>
            <text x="25" y="20" font-size="8" fill="#007bff" text-anchor="middle">${length}cm</text>
          </g>
        `;
      } else if (desc.includes('line segment') && (desc.includes('angle') || desc.includes('measurements'))) {
        svgContent += `
          <g transform="translate(${x - 30}, ${startY - 40})">
            <line x1="0" y1="40" x2="60" y2="40" stroke="#333" stroke-width="2"/>
            <circle cx="0" cy="40" r="3" fill="#dc3545"/>
            <circle cx="60" cy="40" r="3" fill="#dc3545"/>
            <text x="-5" y="35" font-size="10" font-weight="bold" fill="#333">B</text>
            <text x="65" y="35" font-size="10" font-weight="bold" fill="#333">C</text>
            
            <!-- Angle indicators -->
            <path d="M 10 40 Q 10 30 20 30" stroke="#28a745" stroke-width="1" fill="none"/>
            <text x="12" y="28" font-size="8" fill="#28a745">∠B</text>
            
            <path d="M 50 40 Q 50 30 40 30" stroke="#28a745" stroke-width="1" fill="none"/>
            <text x="45" y="28" font-size="8" fill="#28a745">∠C</text>
          </g>
        `;
      } else if (desc.includes('triangle')) {
        svgContent += `
          <g transform="translate(${x - 30}, ${startY - 50})">
            <polygon points="30,10 10,60 50,60" fill="none" stroke="#333" stroke-width="2"/>
            <circle cx="30" cy="10" r="3" fill="#dc3545"/>
            <circle cx="10" cy="60" r="3" fill="#dc3545"/>
            <circle cx="50" cy="60" r="3" fill="#dc3545"/>
            <text x="28" y="8" font-size="10" font-weight="bold" fill="#333">A</text>
            <text x="5" y="70" font-size="10" font-weight="bold" fill="#333">B</text>
            <text x="52" y="70" font-size="10" font-weight="bold" fill="#333">C</text>
          </g>
        `;
      } else if (desc.includes('perpendicular') || desc.includes('bisector')) {
        svgContent += `
          <g transform="translate(${x - 30}, ${startY - 40})">
            <line x1="0" y1="40" x2="60" y2="40" stroke="#333" stroke-width="2"/>
            <line x1="30" y1="20" x2="30" y2="60" stroke="#007bff" stroke-width="2"/>
            <circle cx="0" cy="40" r="3" fill="#dc3545"/>
            <circle cx="60" cy="40" r="3" fill="#dc3545"/>
            <circle cx="30" cy="40" r="3" fill="#007bff"/>
            <text x="-5" y="35" font-size="10" font-weight="bold" fill="#333">P</text>
            <text x="65" y="35" font-size="10" font-weight="bold" fill="#333">Q</text>
            <text x="32" y="18" font-size="10" font-weight="bold" fill="#007bff">M</text>
            <rect x="25" y="35" width="10" height="10" fill="none" stroke="#007bff" stroke-width="1"/>
          </g>
        `;
      } else if (desc.includes('circle') || desc.includes('circumcenter')) {
        svgContent += `
          <g transform="translate(${x - 30}, ${startY - 40})">
            <circle cx="30" cy="40" r="25" fill="none" stroke="#333" stroke-width="2"/>
            <circle cx="30" cy="40" r="2" fill="#dc3545"/>
            <text x="28" y="38" font-size="10" font-weight="bold" fill="#333">O</text>
            <circle cx="30" cy="15" r="3" fill="#007bff"/>
            <circle cx="55" cy="40" r="3" fill="#007bff"/>
            <circle cx="30" cy="65" r="3" fill="#007bff"/>
            <circle cx="5" cy="40" r="3" fill="#007bff"/>
            <text x="28" y="12" font-size="8" font-weight="bold" fill="#007bff">A</text>
            <text x="58" y="43" font-size="8" font-weight="bold" fill="#007bff">B</text>
            <text x="28" y="72" font-size="8" font-weight="bold" fill="#007bff">C</text>
            <text x="0" y="43" font-size="8" font-weight="bold" fill="#007bff">D</text>
          </g>
        `;
      } else {
        // Default line segment
        svgContent += `
          <g transform="translate(${x - 30}, ${startY - 30})">
            <line x1="0" y1="30" x2="60" y2="30" stroke="#333" stroke-width="2"/>
            <circle cx="0" cy="30" r="3" fill="#dc3545"/>
            <circle cx="60" cy="30" r="3" fill="#dc3545"/>
            <text x="-5" y="25" font-size="10" font-weight="bold" fill="#333">${String.fromCharCode(65 + index)}</text>
            <text x="65" y="25" font-size="10" font-weight="bold" fill="#333">${String.fromCharCode(66 + index)}</text>
          </g>
        `;
      }
      
      // Step number
      svgContent += `<text x="${x}" y="${startY + 50}" font-size="10" fill="#666" text-anchor="middle">Step ${index + 1}</text>`;
    });
    
    // Add flow arrow
    if (diagrams.length > 1) {
      svgContent += `<path d="M ${startX + diagrams.length * stepSpacing - 20} ${startY} L ${startX + diagrams.length * stepSpacing + 10} ${startY}" stroke="#28a745" stroke-width="2" marker-end="url(#arrowhead)"/>`;
      svgContent += `<defs><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#28a745"/></marker></defs>`;
    }
    
    svgContent += '</svg>';
    return svgContent;
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
                <h4>🎨 Visual Construction Flow:</h4>
                
                {diagramLoading ? (
                  <div className="diagram-loading">
                    <div className="loading-spinner"></div>
                    <p>Generating construction sequence...</p>
                  </div>
                ) : diagrams.length > 0 ? (
                  <div className="connected-diagrams">
                    {/* Show connected sequence */}
                    <div 
                      className="sequence-diagram"
                      dangerouslySetInnerHTML={{ 
                        __html: generateConnectedDiagramSequence(diagrams, questionText) 
                      }}
                    />
                    
                    {/* Show individual diagram descriptions below */}
                    <div className="diagram-descriptions">
                      <h5>📋 Construction Steps:</h5>
                      {diagrams.map((diagram, index) => (
                        <div key={index} className="step-description">
                          <span className="step-number">Step {index + 1}:</span>
                          <p>{diagram.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="no-diagrams">
                    <div className="empty-diagram-icon">📐</div>
                    <h5>No Construction Steps Available</h5>
                    <p>Try selecting "📊 Solution with Diagram" for visual constructions.</p>
                    
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
                      <p className="fallback-caption">This is a sample diagram. Real construction sequences will appear when you select "Solution with Diagram".</p>
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
