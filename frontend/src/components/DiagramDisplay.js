import React from 'react';
import './DiagramDisplay.css';

/**
 * DiagramDisplay Component
 * Displays ASCII art diagrams and structured diagram data
 */
const DiagramDisplay = ({ diagram }) => {
  if (!diagram) return null;

  const renderDiagram = () => {
    switch (diagram.type) {
      case 'geometry':
      case 'graph':
      case 'number_line':
      case 'vector':
      case 'tree':
      case 'venn':
      case 'physics':
        return (
          <div className="diagram-container">
            <div className="diagram-header">
              <span className="diagram-icon">📐</span>
              <h4>{diagram.description || 'Diagram'}</h4>
            </div>
            
            {diagram.ascii && (
              <pre className="diagram-ascii">
                {diagram.ascii}
              </pre>
            )}
            
            {diagram.labels && diagram.labels.length > 0 && (
              <div className="diagram-labels">
                <strong>Labels:</strong>
                <ul>
                  {diagram.labels.map((label, idx) => (
                    <li key={idx}>{label}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {diagram.equation && (
              <div className="diagram-equation">
                <strong>Equation:</strong> {diagram.equation}
              </div>
            )}
            
            {diagram.vectors && diagram.vectors.length > 0 && (
              <div className="diagram-vectors">
                <strong>Vectors:</strong> {diagram.vectors.join(', ')}
              </div>
            )}
          </div>
        );
      
      default:
        return (
          <div className="diagram-container">
            <pre className="diagram-ascii">
              {diagram.ascii || diagram.description || 'Diagram'}
            </pre>
          </div>
        );
    }
  };

  return (
    <div className="diagram-wrapper">
      {renderDiagram()}
      {diagram.step_description && (
        <div className="diagram-context">
          <em>{diagram.step_description}</em>
        </div>
      )}
    </div>
  );
};

export default DiagramDisplay;
