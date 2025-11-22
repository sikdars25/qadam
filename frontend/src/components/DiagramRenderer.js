import React from 'react';
import './DiagramRenderer.css';

const DiagramRenderer = ({ diagrams, solutionText, questionText, subject }) => {
  // If no structured diagrams, try to generate fallback diagrams
  if (!diagrams || diagrams.length === 0) {
    if (solutionText && solutionText.includes('[DIAGRAM:')) {
      return <TextDiagramRenderer solutionText={solutionText} />;
    }
    // Generate fallback diagrams for geometry questions
    if (questionText && isGeometryQuestion(questionText)) {
      return <FallbackGeometryRenderer questionText={questionText} solutionText={solutionText} />;
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

// Helper function to detect geometry questions
const isGeometryQuestion = (questionText) => {
  const geometryKeywords = [
    'triangle', 'construct', 'draw', 'circle', 'radius', 'diameter',
    'angle', 'perpendicular', 'parallel', 'base', 'height', 'side',
    'vertex', 'vertices', 'polygon', 'rectangle', 'square'
  ];
  
  return geometryKeywords.some(keyword => 
    questionText.toLowerCase().includes(keyword.toLowerCase())
  );
};

// Fallback geometry renderer for when AI service is not available
const FallbackGeometryRenderer = ({ questionText, solutionText }) => {
  const generateGeometryDiagram = () => {
    const lowerQuestion = questionText.toLowerCase();
    
    if (lowerQuestion.includes('triangle')) {
      return {
        type: 'triangle',
        title: 'Triangle Construction',
        description: extractTriangleDetails(questionText),
        steps: generateTriangleSteps(questionText)
      };
    }
    
    if (lowerQuestion.includes('circle')) {
      return {
        type: 'circle',
        title: 'Circle Construction',
        description: extractCircleDetails(questionText),
        steps: generateCircleSteps(questionText)
      };
    }
    
    return {
      type: 'geometry',
      title: 'Geometric Construction',
      description: 'Geometric construction diagram',
      steps: ['Analyze the given measurements', 'Construct the figure step by step', 'Label all parts clearly']
    };
  };
  
  const diagram = generateGeometryDiagram();
  
  return (
    <div className="diagram-container fallback-diagram">
      <div className="diagram-item">
        <div className="diagram-header">
          <span className="diagram-type">📐 {diagram.type}</span>
          <span className="diagram-title">{diagram.title}</span>
        </div>
        <div className="diagram-content">
          <div className="construction-steps">
            <h4>📊 Construction Diagram</h4>
            <div className="diagram-visual">
              <div className="construction-placeholder">
                {diagram.type === 'triangle' && (
                  <div className="triangle-placeholder">
                    <svg width="200" height="150" viewBox="0 0 200 150">
                      <polygon points="100,20 170,130 30,130" fill="none" stroke="#007bff" strokeWidth="2"/>
                      <text x="100" y="145" textAnchor="middle" fontSize="12" fill="#333">BC</text>
                      <text x="85" y="35" textAnchor="middle" fontSize="12" fill="#333">A</text>
                      <text x="175" y="135" textAnchor="middle" fontSize="12" fill="#333">B</text>
                      <text x="25" y="135" textAnchor="middle" fontSize="12" fill="#333">C</text>
                    </svg>
                  </div>
                )}
                {diagram.type === 'circle' && (
                  <div className="circle-placeholder">
                    <svg width="150" height="150" viewBox="0 0 150 150">
                      <circle cx="75" cy="75" r="50" fill="none" stroke="#007bff" strokeWidth="2"/>
                      <line x1="75" y1="75" x2="125" y2="75" stroke="#dc3545" strokeWidth="1" strokeDasharray="5,5"/>
                      <text x="75" y="80" textAnchor="middle" fontSize="12" fill="#333">O</text>
                      <text x="130" y="80" textAnchor="middle" fontSize="12" fill="#333">r</text>
                    </svg>
                  </div>
                )}
              </div>
            </div>
            <div className="construction-info">
              <p><strong>Description:</strong> {diagram.description}</p>
              <h5>Construction Steps:</h5>
              <ol>
                {diagram.steps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper functions for extracting details
const extractTriangleDetails = (questionText) => {
  const details = [];
  
  // Extract side lengths
  const sideMatch = questionText.match(/([A-Z]+)\s*=\s*(\d+(?:\.\d+)?)\s*cm/);
  if (sideMatch) {
    details.push(`${sideMatch[1]} = ${sideMatch[2]} cm`);
  }
  
  // Extract angles
  const angleMatches = questionText.match(/∠([A-Z])\s*=\s*(\d+(?:\.\d+)?)°/g);
  if (angleMatches) {
    details.push(...angleMatches);
  }
  
  return details.length > 0 ? details.join(', ') : 'Triangle with given measurements';
};

const extractCircleDetails = (questionText) => {
  const radiusMatch = questionText.match(/radius\s*=\s*(\d+(?:\.\d+)?)\s*cm/);
  if (radiusMatch) {
    return `Radius = ${radiusMatch[1]} cm`;
  }
  
  const diameterMatch = questionText.match(/diameter\s*=\s*(\d+(?:\.\d+)?)\s*cm/);
  if (diameterMatch) {
    return `Diameter = ${diameterMatch[1]} cm`;
  }
  
  return 'Circle with given measurements';
};

const generateTriangleSteps = (questionText) => {
  const steps = [
    'Draw the base BC with the given length',
    'Construct angle B at point B using a protractor',
    'Construct angle C at point C using a protractor',
    'The intersection of the two angle rays gives point A',
    'Connect point A to points B and C',
    'Label all sides and angles clearly'
  ];
  
  // Customize based on specific measurements
  if (questionText.includes('60°') && questionText.includes('45°')) {
    steps[1] = 'Construct a 60° angle at point B';
    steps[2] = 'Construct a 45° angle at point C';
  }
  
  return steps;
};

const generateCircleSteps = (questionText) => {
  return [
    'Draw a point O as the center',
    'Set the compass to the given radius',
    'Draw the circle with center O',
    'Mark the radius if required',
    'Label the center and radius clearly'
  ];
};

export default DiagramRenderer;
