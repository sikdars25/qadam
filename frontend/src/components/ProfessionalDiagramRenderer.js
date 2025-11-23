import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

const ProfessionalDiagramRenderer = ({ solutionText, questionText }) => {
  const diagramContainerRef = useRef(null);

  // Initialize Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
      themeVariables: {
        primaryColor: '#007bff',
        primaryTextColor: '#333',
        primaryBorderColor: '#007bff',
        lineColor: '#007bff',
        secondaryColor: '#f8f9fa',
        tertiaryColor: '#e9ecef'
      }
    });
  }, []);

  // Generate Mermaid diagram based on question type
  const generateMermaidDiagram = (description) => {
    const lowerDesc = description.toLowerCase();
    const lowerQuestion = questionText.toLowerCase();

    // Triangle construction diagrams
    if (lowerDesc.includes('triangle') || lowerQuestion.includes('triangle')) {
      return `
graph TD
    A[Vertex A] --> B[Vertex B]
    B --> C[Vertex C]
    C --> A
    style A fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    style B fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    style C fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    classDef default fill:#f8f9fa,stroke:#007bff,stroke-width:2px
      `;
    }

    // Line segment diagrams
    if (lowerDesc.includes('line segment') || lowerDesc.includes('line')) {
      return `
graph LR
    B[Point B] --> C[Point C]
    style B fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    style C fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    classDef default fill:#f8f9fa,stroke:#007bff,stroke-width:2px
      `;
    }

    // Angle construction diagrams
    if (lowerDesc.includes('angle')) {
      return `
graph TD
    B[Vertex B] --> A[Ray BA]
    B --> C[Ray BC]
    style A fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    style B fill:#ffcdd2,stroke:#dc3545,stroke-width:3px
    style C fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    classDef default fill:#f8f9fa,stroke:#007bff,stroke-width:2px
      `;
    }

    // Circle construction diagrams
    if (lowerDesc.includes('circle')) {
      return `
graph TD
    O[Center O] --> R[Radius]
    O --> C[Circumference]
    style O fill:#ffcdd2,stroke:#dc3545,stroke-width:3px
    style R fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    style C fill:#e3f2fd,stroke:#007bff,stroke-width:2px
    classDef default fill:#f8f9fa,stroke:#007bff,stroke-width:2px
      `;
    }

    // Default geometric diagram
    return `
graph TD
    Start[Construction Start] --> Step1[Step 1: Draw Base]
    Step1 --> Step2[Step 2: Mark Points]
    Step2 --> Step3[Step 3: Complete Figure]
    Step3 --> End[Final Diagram]
    style Start fill:#e8f5e8,stroke:#28a745,stroke-width:2px
    style End fill:#e8f5e8,stroke:#28a745,stroke-width:2px
    classDef default fill:#f8f9fa,stroke:#007bff,stroke-width:2px
    `;
  };

  // Render diagram using Mermaid
  const renderDiagram = async (description, index) => {
    const diagramId = `mermaid-diagram-${index}`;
    const mermaidCode = generateMermaidDiagram(description);
    
    try {
      // Create container for diagram
      const container = document.createElement('div');
      container.id = diagramId;
      container.style.cssText = `
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #007bff;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,123,255,0.1);
      `;

      // Add header
      const header = document.createElement('div');
      header.innerHTML = `
        <div style="display: flex; align-items: center; margin-bottom: 15px; font-weight: 600; color: #007bff;">
          📐 Professional Diagram
        </div>
      `;
      container.appendChild(header);

      // Add diagram content
      const diagramContent = document.createElement('div');
      diagramContent.innerHTML = `
        <div class="mermaid">
          ${mermaidCode}
        </div>
      `;
      container.appendChild(diagramContent);

      // Add description
      const descDiv = document.createElement('div');
      descDiv.innerHTML = `
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6; font-style: italic; color: #666;">
          <strong>${description}</strong>
        </div>
      `;
      container.appendChild(descDiv);

      return container.outerHTML;
    } catch (error) {
      console.error('Mermaid rendering error:', error);
      return `<div style="border: 2px dashed #dc3545; padding: 20px; margin: 20px 0; background: #f8d7da;">
        <strong>⚠️ Diagram Error:</strong> Could not render diagram<br>
        <em>${description}</em>
      </div>`;
    }
  };

  // Process solution text and replace diagram markers
  const processSolutionWithDiagrams = async () => {
    if (!solutionText || !solutionText.includes('[DIAGRAM:')) {
      return solutionText;
    }

    const diagramPattern = /\[DIAGRAM:\s*([^\]]+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    let diagramIndex = 0;

    while ((match = diagramPattern.exec(solutionText)) !== null) {
      // Add text before diagram
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: solutionText.slice(lastIndex, match.index)
        });
      }

      // Add diagram
      parts.push({
        type: 'diagram',
        description: match[1].trim(),
        index: diagramIndex++
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

    return parts;
  };

  // Render processed content
  const [processedContent, setProcessedContent] = React.useState(null);

  useEffect(() => {
    const processContent = async () => {
      const parts = await processSolutionWithDiagrams();
      setProcessedContent(parts);
    };
    processContent();
  }, [solutionText]);

  // Re-render Mermaid diagrams when content changes
  useEffect(() => {
    if (processedContent && diagramContainerRef.current) {
      setTimeout(() => {
        mermaid.init();
      }, 100);
    }
  }, [processedContent]);

  if (!processedContent) {
    return <div>Loading diagrams...</div>;
  }

  return (
    <div className="professional-diagram-container" ref={diagramContainerRef}>
      {processedContent.map((part, index) => {
        if (part.type === 'text') {
          return (
            <div key={`text-${index}`} dangerouslySetInnerHTML={{ __html: part.content.replace(/\n/g, '<br>') }} />
          );
        } else {
          return (
            <div key={`diagram-${index}`}>
              <div 
                className="mermaid-diagram-wrapper"
                style={{
                  background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                  border: '2px solid #007bff',
                  borderRadius: '8px',
                  padding: '20px',
                  margin: '20px 0',
                  boxShadow: '0 4px 8px rgba(0,123,255,0.1)'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  marginBottom: '15px',
                  fontWeight: '600',
                  color: '#007bff'
                }}>
                  📐 Professional Diagram
                </div>
                <div className="mermaid">
                  {generateMermaidDiagram(part.description)}
                </div>
                <div style={{
                  marginTop: '15px',
                  paddingTop: '15px',
                  borderTop: '1px solid #dee2e6',
                  fontStyle: 'italic',
                  color: '#666'
                }}>
                  <strong>{part.description}</strong>
                </div>
              </div>
            </div>
          );
        }
      })}
    </div>
  );
};

export default ProfessionalDiagramRenderer;
