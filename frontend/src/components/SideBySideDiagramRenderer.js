import React, { useState, useEffect } from 'react';
import './SideBySideDiagramRenderer.css';

const SideBySideDiagramRenderer = ({ solutionText }) => {
  const [diagrams, setDiagrams] = useState([]);
  const [textOnly, setTextOnly] = useState('');

  useEffect(() => {
    if (!solutionText) {
      setDiagrams([]);
      setTextOnly('');
      return;
    }

    // Extract all diagram markers and descriptions
    const diagramPattern = /\[DIAGRAM:\s*([^\]]+)\]/g;
    const foundDiagrams = [];
    let match;
    let lastIndex = 0;
    let cleanText = solutionText;

    while ((match = diagramPattern.exec(solutionText)) !== null) {
      foundDiagrams.push({
        description: match[1].trim(),
        index: foundDiagrams.length
      });
    }

    // Remove diagram markers from text
    cleanText = solutionText.replace(/\[DIAGRAM:\s*[^\]]+\]/g, '');

    setDiagrams(foundDiagrams);
    setTextOnly(cleanText);
  }, [solutionText]);

  // Always render the containers, even if empty
  return (
    <div className="side-by-side-container">
      {/* Text Container - Left Side */}
      <div className="text-container">
        <div className="container-header">
          <h3>📝 Solution Steps</h3>
          <span className="item-count">{textOnly.split('\n').filter(line => line.trim()).length} lines</span>
        </div>
        <div className="text-content">
          {textOnly ? (
            textOnly.split('\n').map((line, index) => (
              <div key={index} className="text-line">
                {line.trim() ? (
                  <p>{line}</p>
                ) : (
                  <br />
                )}
              </div>
            ))
          ) : (
            <p className="empty-state">No text content available</p>
          )}
        </div>
      </div>

      {/* Diagram Container - Right Side */}
      <div className="diagram-container">
        <div className="container-header">
          <h3>📐 Construction Diagrams</h3>
          <span className="item-count">{diagrams.length} diagram(s)</span>
        </div>
        <div className="diagram-content">
          {diagrams.length > 0 ? (
            diagrams.map((diagram, index) => (
              <div key={index} className="diagram-item">
                <div className="diagram-header">
                  <span>📐 Diagram {index + 1}</span>
                </div>
                
                {/* Always show a visual diagram */}
                <div className="diagram-visual">
                  <div className="css-triangle">
                    <div className="vertex-label vertex-a">A</div>
                    <div className="vertex-label vertex-b">B</div>
                    <div className="vertex-label vertex-c">C</div>
                  </div>
                </div>
                
                <div className="diagram-description">
                  <strong>Description:</strong> {diagram.description}
                </div>
                
                <div className="diagram-steps">
                  <strong>Construction Steps:</strong>
                  <ol>
                    <li>Draw the base with given measurements</li>
                    <li>Mark the vertices according to specifications</li>
                    <li>Connect the points to form the figure</li>
                    <li>Label all sides and angles clearly</li>
                  </ol>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-diagram-state">
              <div className="empty-icon">📐</div>
              <h4>No Diagrams Found</h4>
              <p>Diagram markers like [DIAGRAM: description] were not found in the solution.</p>
              
              {/* Show a sample diagram anyway */}
              <div className="sample-diagram">
                <div className="diagram-header">
                  <span>📐 Sample Triangle</span>
                </div>
                <div className="diagram-visual">
                  <div className="css-triangle">
                    <div className="vertex-label vertex-a">A</div>
                    <div className="vertex-label vertex-b">B</div>
                    <div className="vertex-label vertex-c">C</div>
                  </div>
                </div>
                <div className="diagram-description">
                  <strong>Sample:</strong> This is how diagrams would appear if markers were found.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SideBySideDiagramRenderer;
