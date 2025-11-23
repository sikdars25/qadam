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
          setError('Failed to get diagrams: ' + response.data.error);
        }
      }
    } catch (err) {
      setError('Error getting diagrams: ' + err.message);
    } finally {
      setDiagramLoading(false);
    }
  };

  // Get both text and diagrams when component mounts
  useEffect(() => {
    if (questionText) {
      setLoading(true);
      Promise.all([getTextSolution(), getDiagrams()]).finally(() => {
        setLoading(false);
      });
    }
  }, [questionText, subject]);

  const renderDiagram = (diagram, index) => {
    return (
      <div key={index} className="diagram-card">
        <div className="diagram-header">
          <span>📐 Diagram {index + 1}</span>
        </div>
        
        <div className="diagram-content">
          {diagram.svg ? (
            <div dangerouslySetInnerHTML={{ __html: diagram.svg }} />
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
          <strong>Description:</strong> {diagram.description || 'Geometric construction diagram'}
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

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="dual-content">
        {/* Text Solution Container */}
        <div className="text-solution-container">
          <div className="container-header">
            <h3>📝 Text Solution</h3>
            {textLoading && <span className="loading-badge">Loading...</span>}
          </div>
          <div className="text-content">
            {textSolution ? (
              textSolution.split('\n').map((line, index) => (
                <div key={index} className="text-line">
                  {line.trim() ? <p>{line}</p> : <br />}
                </div>
              ))
            ) : (
              <p className="empty-state">No text solution available</p>
            )}
          </div>
        </div>

        {/* Diagrams Container */}
        <div className="diagrams-container">
          <div className="container-header">
            <h3>📐 Construction Diagrams</h3>
            {diagramLoading && <span className="loading-badge">Loading...</span>}
            <span className="count-badge">{diagrams.length} diagram(s)</span>
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
