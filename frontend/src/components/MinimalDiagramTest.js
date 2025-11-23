import React from 'react';

const MinimalDiagramTest = ({ solutionText }) => {
  console.log('MinimalDiagramTest called with:', solutionText);

  // ALWAYS return visible containers - no conditions
  return (
    <div style={{ padding: '20px', background: '#f0f0f0', margin: '20px 0' }}>
      <h2 style={{ color: '#007bff', textAlign: 'center', marginBottom: '30px' }}>
        🧪 DIAGRAM TEST CONTAINER - ALWAYS VISIBLE
      </h2>
      
      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
        {/* Test Container 1 - Always Shows */}
        <div style={{
          flex: 1,
          border: '3px solid #28a745',
          borderRadius: '10px',
          padding: '20px',
          background: 'white'
        }}>
          <h3 style={{ color: '#28a745', margin: '0 0 15px 0' }}>
            📝 TEST: Text Container
          </h3>
          <div style={{ background: '#f8f9fa', padding: '10px', borderRadius: '5px' }}>
            <strong>Raw solutionText received:</strong>
            <pre style={{ fontSize: '12px', background: '#e9ecef', padding: '10px', marginTop: '10px' }}>
              {solutionText ? solutionText.substring(0, 200) + '...' : 'NULL'}
            </pre>
          </div>
        </div>

        {/* Test Container 2 - Always Shows Diagram */}
        <div style={{
          flex: 1,
          border: '3px solid #007bff',
          borderRadius: '10px',
          padding: '20px',
          background: 'white'
        }}>
          <h3 style={{ color: '#007bff', margin: '0 0 15px 0' }}>
            📐 TEST: Diagram Container
          </h3>
          
          {/* Always show this diagram */}
          <div style={{
            border: '2px solid #007bff',
            borderRadius: '8px',
            padding: '20px',
            background: 'linear-gradient(135deg, #f0f8ff 0%, #e3f2fd 100%)',
            textAlign: 'center'
          }}>
            <div style={{
              fontSize: '18px',
              fontWeight: 'bold',
              color: '#007bff',
              marginBottom: '20px'
            }}>
              📐 GUARANTEED DIAGRAM
            </div>
            
            {/* CSS Triangle */}
            <div style={{
              width: '0',
              height: '0',
              borderLeft: '80px solid transparent',
              borderRight: '80px solid transparent',
              borderBottom: '120px solid #007bff',
              margin: '20px auto',
              position: 'relative'
            }}>
              <div style={{
                position: 'absolute',
                top: '-30px',
                left: '-10px',
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#333',
                background: 'white',
                padding: '2px 6px',
                border: '1px solid #dee2e6',
                borderRadius: '4px'
              }}>A</div>
              <div style={{
                position: 'absolute',
                bottom: '-30px',
                left: '-100px',
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#333',
                background: 'white',
                padding: '2px 6px',
                border: '1px solid #dee2e6',
                borderRadius: '4px'
              }}>B</div>
              <div style={{
                position: 'absolute',
                bottom: '-30px',
                right: '-100px',
                fontSize: '16px',
                fontWeight: 'bold',
                color: '#333',
                background: 'white',
                padding: '2px 6px',
                border: '1px solid #dee2e6',
                borderRadius: '4px'
              }}>C</div>
            </div>
            
            <div style={{
              marginTop: '20px',
              padding: '15px',
              background: 'white',
              borderRadius: '8px',
              border: '1px solid #dee2e6'
            }}>
              <strong>📝 Description:</strong> Test diagram that always appears
            </div>
          </div>
        </div>
      </div>

      {/* Debug Info */}
      <div style={{
        border: '2px solid #ffc107',
        borderRadius: '8px',
        padding: '15px',
        background: '#fff3cd',
        textAlign: 'center'
      }}>
        <strong>🔍 DEBUG INFO:</strong> This test container should ALWAYS be visible.
        If you can see this, the component is working. SolutionText length: {solutionText?.length || 0}
      </div>
    </div>
  );
};

export default MinimalDiagramTest;
