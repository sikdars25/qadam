import React from 'react';
import './TwoColumnTest.css';

const TwoColumnTest = () => {
  return (
    <div className="two-column-test">
      <div className="test-header">
        <h2>🧪 Two-Column Layout Test</h2>
        <p>This should always show two columns</p>
      </div>
      
      <div className="two-columns">
        {/* Left Column */}
        <div className="left-column">
          <div className="column-header">
            <h3>📝 Text Solution</h3>
            <span className="subtitle">Step-by-step explanation</span>
          </div>
          <div className="column-content">
            <p>1. Draw triangle ABC with the given dimensions.</p>
            <p>2. Mark the given angles and sides as specified.</p>
            <p>3. Use the appropriate construction method.</p>
            <p>4. Verify the construction meets all requirements.</p>
          </div>
        </div>

        {/* Right Column */}
        <div className="right-column">
          <div className="column-header">
            <h3>📐 Construction Diagrams</h3>
            <span className="subtitle">Visual geometric constructions</span>
          </div>
          <div className="column-content">
            <div className="sample-diagram">
              <div className="diagram-box">
                <div className="triangle">
                  <div className="vertex-a">A</div>
                  <div className="vertex-b">B</div>
                  <div className="vertex-c">C</div>
                </div>
              </div>
              <p className="diagram-caption">Sample triangle ABC</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TwoColumnTest;
