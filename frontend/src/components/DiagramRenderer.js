import React from 'react';
import './DiagramRenderer.css';

const DiagramRenderer = ({ diagrams, solutionText }) => {
  if (!diagrams || diagrams.length === 0) {
    // If no structured diagrams, check for diagram markers in text
    if (solutionText && solutionText.includes('[DIAGRAM:')) {
      return <TextDiagramRenderer solutionText={solutionText} />;
    }
    return null;
  }

  return (
    <div className="diagram-container">
      {diagrams.map((diagram, index) => (
        <div key={index} className="diagram-item">
          <div className="diagram-header">
            <span className="diagram-type">{diagram.type || 'Diagram'}</span>
            {diagram.title && <span className="diagram-title">{diagram.title}</span>}
          </div>
          <div className="diagram-content">
            {diagram.type === 'ascii' ? (
              <pre className="ascii-diagram">{diagram.content}</pre>
            ) : diagram.type === 'svg' ? (
              <div 
                className="svg-diagram"
                dangerouslySetInnerHTML={{ __html: diagram.content }}
              />
            ) : diagram.type === 'description' ? (
              <div className="diagram-description">
                <div className="diagram-placeholder">
                  📊 {diagram.content}
                </div>
                <p className="diagram-note">
                  <em>Note: Diagram would be displayed here in a full implementation.</em>
                </p>
              </div>
            ) : (
              <div className="diagram-generic">
                <div className="diagram-placeholder">
                  📈 {diagram.description || 'Diagram'}
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

const TextDiagramRenderer = ({ solutionText }) => {
  // Extract diagram markers from text and render them as placeholders
  const diagramPattern = /\[DIAGRAM:\s*([^\]]+)\]/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = diagramPattern.exec(solutionText)) !== null) {
    // Add text before diagram
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: solutionText.slice(lastIndex, match.index)
      });
    }

    // Add diagram placeholder
    parts.push({
      type: 'diagram',
      description: match[1].trim()
    });

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < solutionText.length) {
    parts.push({
      type: 'text',
      content: solutionText.slice(lastIndex)
    });
  }

  return (
    <div className="text-diagram-container">
      {parts.map((part, index) => {
        if (part.type === 'text') {
          return <span key={index}>{part.content}</span>;
        } else {
          return (
            <div key={index} className="inline-diagram-placeholder">
              <div className="diagram-box">
                📊 <strong>Diagram:</strong> {part.description}
              </div>
              <p className="diagram-note">
                <em>Diagram visualization would appear here</em>
              </p>
            </div>
          );
        }
      })}
    </div>
  );
};

export default DiagramRenderer;
