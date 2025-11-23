import React from 'react';
import './DiagramSamples.css';

const DiagramSamples = () => {
  const sampleDiagrams = [
    {
      title: "Triangle Construction",
      description: "Construct a triangle ABC with given sides and angles",
      diagram: (
        <div className="sample-diagram">
          <div className="diagram-header">
            <span>📐 Triangle ABC</span>
          </div>
          <div className="diagram-content">
            <div className="css-triangle">
              <div className="vertex-label vertex-a">A</div>
              <div className="vertex-label vertex-b">B</div>
              <div className="vertex-label vertex-c">C</div>
            </div>
          </div>
          <div className="diagram-info">
            <p><strong>Steps:</strong></p>
            <ol>
              <li>Draw base BC = 6 cm</li>
              <li>Construct angle B = 60°</li>
              <li>Construct angle C = 45°</li>
              <li>Complete triangle ABC</li>
            </ol>
          </div>
        </div>
      )
    },
    {
      title: "Angle Construction",
      description: "Construct a 60° angle at point B",
      diagram: (
        <div className="sample-diagram">
          <div className="diagram-header">
            <span>📐 60° Angle</span>
          </div>
          <div className="diagram-content">
            <div className="angle-diagram">
              <div className="angle-vertex">B</div>
              <div className="angle-ray ray-1"></div>
              <div className="angle-ray ray-2"></div>
              <div className="angle-arc">60°</div>
            </div>
          </div>
          <div className="diagram-info">
            <p><strong>Steps:</strong></p>
            <ol>
              <li>Draw point B</li>
              <li>Draw ray BA</li>
              <li>Construct 60° angle using protractor</li>
              <li>Draw ray BC</li>
            </ol>
          </div>
        </div>
      )
    },
    {
      title: "Circle Construction",
      description: "Construct a circle with given radius",
      diagram: (
        <div className="sample-diagram">
          <div className="diagram-header">
            <span>⭕ Circle with Radius</span>
          </div>
          <div className="diagram-content">
            <div className="circle-diagram">
              <div className="circle-center">O</div>
              <div className="circle-radius"></div>
              <div className="circle-arc"></div>
            </div>
          </div>
          <div className="diagram-info">
            <p><strong>Steps:</strong></p>
            <ol>
              <li>Mark center point O</li>
              <li>Set compass to given radius</li>
              <li>Draw circle with center O</li>
              <li>Label radius and center</li>
            </ol>
          </div>
        </div>
      )
    },
    {
      title: "Line Segment Construction",
      description: "Construct a line segment of given length",
      diagram: (
        <div className="sample-diagram">
          <div className="diagram-header">
            <span>📏 Line Segment</span>
          </div>
          <div className="diagram-content">
            <div className="line-diagram">
              <div className="line-endpoint point-a">A</div>
              <div className="line-segment"></div>
              <div className="line-endpoint point-b">B</div>
              <div className="line-label">6 cm</div>
            </div>
          </div>
          <div className="diagram-info">
            <p><strong>Steps:</strong></p>
            <ol>
              <li>Draw point A</li>
              <li>Measure 6 cm with ruler</li>
              <li>Mark point B at 6 cm</li>
              <li>Connect A and B with straight line</li>
            </ol>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="diagram-samples">
      <div className="samples-header">
        <h2>📐 Geometry Diagram Samples</h2>
        <p>Interactive samples of geometric constructions</p>
      </div>
      
      <div className="samples-grid">
        {sampleDiagrams.map((sample, index) => (
          <div key={index} className="sample-card">
            <div className="sample-title">
              <h3>{sample.title}</h3>
              <p>{sample.description}</p>
            </div>
            {sample.diagram}
          </div>
        ))}
      </div>

      <div className="samples-footer">
        <div className="info-box">
          <h3>🎯 About Diagram Samples</h3>
          <p>
            These are sample diagrams demonstrating geometric constructions. 
            Each diagram shows the steps and visual representation of common 
            mathematical constructions used in CBSE curriculum.
          </p>
          <div className="features">
            <div className="feature">
              <span className="feature-icon">📐</span>
              <span>Interactive visual diagrams</span>
            </div>
            <div className="feature">
              <span className="feature-icon">📝</span>
              <span>Step-by-step construction guide</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🎨</span>
              <span>Professional styling and layout</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagramSamples;
