import React from 'react';

const BulletproofDiagramRenderer = ({ solutionText }) => {
  if (!solutionText || !solutionText.includes('[DIAGRAM:')) {
    return null;
  }

  // Split on diagram markers and render
  const parts = solutionText.split(/\[DIAGRAM:\s*([^\]]+)\]/);
  
  return (
    <div>
      {parts.map((part, index) => {
        if (index % 2 === 0) {
          // Regular text - render with line breaks
          return (
            <div key={index} dangerouslySetInnerHTML={{ 
              __html: part.replace(/\n/g, '<br>') 
            }} />
          );
        } else {
          // Diagram marker - render simple HTML diagram
          return (
            <div key={index} style={{
              border: '3px solid #007bff',
              borderRadius: '10px',
              padding: '25px',
              margin: '25px 0',
              backgroundColor: '#f0f8ff',
              boxShadow: '0 6px 12px rgba(0,123,255,0.2)',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '18px',
                fontWeight: 'bold',
                color: '#007bff',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                📐 CONSTRUCTION DIAGRAM
              </div>
              
              {/* Simple CSS Triangle */}
              <div style={{
                width: '0',
                height: '0',
                borderLeft: '100px solid transparent',
                borderRight: '100px solid transparent',
                borderBottom: '150px solid #007bff',
                margin: '20px auto',
                position: 'relative'
              }}>
                {/* Triangle Labels */}
                <div style={{
                  position: 'absolute',
                  top: '160px',
                  left: '-10px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#333'
                }}>B</div>
                <div style={{
                  position: 'absolute',
                  top: '160px',
                  right: '-10px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#333'
                }}>C</div>
                <div style={{
                  position: 'absolute',
                  top: '-25px',
                  left: '-10px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  color: '#333'
                }}>A</div>
              </div>
              
              {/* Diagram Description */}
              <div style={{
                marginTop: '30px',
                padding: '15px',
                backgroundColor: 'white',
                borderRadius: '8px',
                border: '1px solid #dee2e6',
                fontSize: '14px',
                color: '#666',
                fontStyle: 'italic'
              }}>
                <strong>📝 Description:</strong> {part}
              </div>
              
              {/* Construction Steps */}
              <div style={{
                marginTop: '20px',
                textAlign: 'left',
                fontSize: '14px',
                color: '#333'
              }}>
                <strong>🔧 Construction Steps:</strong>
                <ol style={{
                  margin: '10px 0',
                  paddingLeft: '20px'
                }}>
                  <li>Draw the base BC with given measurements</li>
                  <li>Mark the vertices according to specifications</li>
                  <li>Connect the vertices to form the triangle</li>
                  <li>Label all sides and angles clearly</li>
                </ol>
              </div>
            </div>
          );
        }
      })}
    </div>
  );
};

export default BulletproofDiagramRenderer;
