import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DualEndpointDiagramRenderer.css';

const DualEndpointDiagramRenderer = ({ questionText, subject }) => {
  const [textSolution, setTextSolution] = useState('');
  const [diagrams, setDiagrams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [textLoading, setTextLoading] = useState(false);
  const [diagramLoading, setDiagramLoading] = useState(false);

  // Separate function to get text solution
  const getTextSolution = async () => {
    setTextLoading(true);
    try {
      const response = await axios.post('http://130.107.48.166/solve-question', {
        question_text: questionText,
        subject: subject,
        solution_type: 'step-by-step'  // Get text only
      });
      
      if (response.data.success) {
        setTextSolution(response.data.solution || '');
      } else {
        setError('Failed to get text solution');
      }
    } catch (err) {
      setError('Error getting text solution: ' + err.message);
    } finally {
      setTextLoading(false);
    }
  };

  // Separate function to get diagrams
  const getDiagrams = async () => {
    setDiagramLoading(true);
    try {
      const response = await axios.post('http://130.107.48.166:5001/analyze-diagrams', {
        question_text: questionText,
        subject: subject,
        solution_type: 'with-diagram'
      });
      
      if (response.data.success) {
        // Handle the new response format from analyze-diagrams
        if (response.data.content) {
          // Create diagram objects from the content text
          const contentLines = response.data.content.split('\n').filter(line => line.trim());
          const diagramObjects = contentLines.map((line, index) => ({
            id: `diagram_${index + 1}`,
            title: `Diagram ${index + 1}`,
            content: line.replace(/^Diagram \d+:\s*/, ''),
            svg: response.data.svg || '',
            description: line.replace(/^Diagram \d+:\s*/, '')
          }));
          setDiagrams(diagramObjects);
        } else if (response.data.diagrams && response.data.diagrams.length > 0) {
          // Use the diagrams array if available
          setDiagrams(response.data.diagrams);
        } else {
          setDiagrams([]);
        }
      } else {
        // Try test endpoint if main fails
        try {
          const testResponse = await axios.get('http://130.107.48.166:5001/test-diagram');
          if (testResponse.data.success) {
            setDiagrams(testResponse.data.diagrams);
          }
        } catch (testErr) {
          // Silently fail - don't set error for diagram issues
          console.log('Diagram endpoint not available - using sample');
        }
      }
    } catch (err) {
      // Silently fail - don't set error for diagram issues
      console.log('Diagram endpoint error:', err.message);
    } finally {
      setDiagramLoading(false);
    }
  };

  // Get both text and diagrams when component mounts
  useEffect(() => {
    if (questionText) {
      setLoading(true);
      // Always get text solution
      getTextSolution();
      // Try to get diagrams, but don't fail if they don't work
      getDiagrams().finally(() => {
        setLoading(false);
      });
    }
  }, [questionText, subject]);

  const renderDiagram = (diagram, index) => {
    return (
      <div key={index} className="diagram-card">
        <div className="diagram-header">
          <span>📐 {diagram.title || `Diagram ${index + 1}`}</span>
        </div>
        
        <div className="diagram-content">
          {diagram.svg ? (
            <div dangerouslySetInnerHTML={{ __html: diagram.svg }} />
          ) : diagram.content ? (
            <div className="text-diagram">
              <pre className="diagram-text">{diagram.content}</pre>
            </div>
          ) : diagram.ascii ? (
            <pre className="ascii-diagram">{diagram.ascii}</pre>
          ) : (
            <div className="css-diagram">
              <div className="css-triangle">
                <div className="vertex-label vertex-a">A</div>
                <div className="vertex-label vertex-b">B</div>
                <div className="vertex-label vertex-c">C</div>
              </div>
            </div>
          )}
        </div>
        
        <div className="diagram-description">
          <strong>Description:</strong> {diagram.description || diagram.content || 'Geometric construction diagram'}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="dual-endpoint-loading">
        <div className="loading-spinner">⏳ Loading solution and diagrams...</div>
      </div>
    );
  }

  return (
    <div className="dual-endpoint-container">
      <div className="endpoint-header">
        <h2>📊 Separate Text & Diagram Solution</h2>
        <p>Text and diagrams fetched from separate endpoints for reliable rendering</p>
      </div>

      {error && error.includes('text') && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="dual-content">
        {/* Text Solution Container - Left Column */}
        <div className="text-solution-container">
          <div className="container-header">
            <div className="header-left">
              <h3>📝 Solution Steps</h3>
              <span className="header-subtitle">Step-by-step explanation</span>
            </div>
            <div className="header-right">
              {textLoading && <span className="loading-badge">Loading...</span>}
              {!textLoading && textSolution && (
                <span className="count-badge" style={{background: '#28a745'}}>
                  {textSolution.split('\n').filter(line => line.trim()).length} steps
                </span>
              )}
            </div>
          </div>
          <div className="text-content">
            {textSolution ? (
              textSolution.split('\n').map((line, index) => (
                <div key={index} className="text-line">
                  {line.trim() ? <p>{line}</p> : <br />}
                </div>
              ))
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📝</div>
                <p>No text solution available</p>
                <small>Text solution will appear here</small>
              </div>
            )}
          </div>
        </div>

        {/* Diagrams Container - Right Column */}
        <div className="diagrams-container">
          <div className="container-header">
            <div className="header-left">
              <h3>📐 Construction Diagrams</h3>
              <span className="header-subtitle">Visual geometric constructions</span>
            </div>
            <div className="header-right">
              {diagramLoading && <span className="loading-badge">Loading...</span>}
              {!diagramLoading && (
                <span className="count-badge">
                  {diagrams.length} diagram(s)
                </span>
              )}
            </div>
          </div>
          <div className="diagrams-content">
            {diagrams.length > 0 ? (
              diagrams.map((diagram, index) => renderDiagram(diagram, index))
            ) : (
              <div className="empty-diagrams">
                <div className="empty-icon">📐</div>
                <h4>No Diagrams Available</h4>
                <p>Diagrams could not be generated for this question.</p>
                
                {/* Show sample diagram */}
                <div className="sample-diagram">
                  <div className="diagram-header">
                    <span>📐 Sample Diagram</span>
                  </div>
                  <div className="css-diagram">
                    <div className="css-triangle">
                      <div className="vertex-label vertex-a">A</div>
                      <div className="vertex-label vertex-b">B</div>
                      <div className="vertex-label vertex-c">C</div>
                    </div>
                  </div>
                  <div className="diagram-description">
                    <strong>Sample:</strong> This is how diagrams would appear.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DualEndpointDiagramRenderer;
