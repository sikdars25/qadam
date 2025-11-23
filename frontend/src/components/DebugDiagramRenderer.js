import React from 'react';

const DebugDiagramRenderer = ({ solutionText }) => {
  // ALWAYS show debug info to see what's happening
  console.log('=== DEBUG DIAGRAM RENDERER ===');
  console.log('solutionText:', solutionText);
  console.log('includes [DIAGRAM:]:', solutionText?.includes('[DIAGRAM:'));
  
  if (!solutionText) {
    return (
      <div style={{border: '2px solid red', padding: '20px', margin: '20px 0'}}>
        <h3>🔍 DEBUG: No solutionText provided</h3>
      </div>
    );
  }

  if (!solutionText.includes('[DIAGRAM:')) {
    return (
      <div style={{border: '2px solid orange', padding: '20px', margin: '20px 0'}}>
        <h3>🔍 DEBUG: No [DIAGRAM:] markers found in solution</h3>
        <p><strong>Solution text:</strong></p>
        <pre style={{background: '#f0f0f0', padding: '10px', fontSize: '12px'}}>
          {solutionText}
        </pre>
      </div>
    );
  }

  // If we get here, we found diagram markers - render them
  const parts = solutionText.split(/\[DIAGRAM:\s*([^\]]+)\]/);
  
  return (
    <div>
      <div style={{border: '2px solid green', padding: '20px', margin: '20px 0'}}>
        <h3>✅ DEBUG: Found {parts.length/2 - 1} diagram markers!</h3>
      </div>
      
      {parts.map((part, index) => {
        if (index % 2 === 0) {
          // Regular text
          return (
            <div key={index} dangerouslySetInnerHTML={{ 
              __html: part.replace(/\n/g, '<br>') 
            }} />
          );
        } else {
          // Diagram marker - render actual diagram
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
                📐 DIAGRAM FOUND AND RENDERED!
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
            </div>
          );
        }
      })}
    </div>
  );
};

export default DebugDiagramRenderer;
