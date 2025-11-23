import React from 'react';

const SimpleDiagramRenderer = ({ solutionText }) => {
  if (!solutionText || !solutionText.includes('[DIAGRAM:')) {
    return null;
  }

  // Simple replacement - convert diagram markers to visual diagrams
  const renderDiagrams = (text) => {
    const parts = text.split(/\[DIAGRAM:\s*([^\]]+)\]/);
    
    return parts.map((part, index) => {
      if (index % 2 === 0) {
        // Regular text
        return <span key={index}>{part}</span>;
      } else {
        // Diagram marker - create visual diagram
        return (
          <div key={index} style={{
            border: '2px dashed #007bff',
            borderRadius: '8px',
            padding: '20px',
            margin: '20px 0',
            background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
            boxShadow: '0 4px 8px rgba(0,123,255,0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '15px',
              fontWeight: '600',
              color: '#007bff'
            }}>
              📐 Diagram
            </div>
            <div style={{ textAlign: 'center' }}>
              <svg width="200" height="150" viewBox="0 0 200 150">
                <polygon points="100,20 170,130 30,130" fill="none" stroke="#007bff" strokeWidth="2"/>
                <text x="100" y="145" textAnchor="middle" fontSize="12" fill="#333">BC</text>
                <text x="85" y="35" textAnchor="middle" fontSize="12" fill="#333">A</text>
                <text x="175" y="135" textAnchor="middle" fontSize="12" fill="#333">B</text>
                <text x="25" y="135" textAnchor="middle" fontSize="12" fill="#333">C</text>
              </svg>
            </div>
            <div style={{ marginTop: '15px', fontStyle: 'italic', color: '#666' }}>
              <strong>{part}</strong>
            </div>
          </div>
        );
      }
    });
  };

  return (
    <div className="simple-diagram-container">
      {renderDiagrams(solutionText)}
    </div>
  );
};

export default SimpleDiagramRenderer;
