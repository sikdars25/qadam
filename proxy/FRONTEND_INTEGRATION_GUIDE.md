# Frontend Integration Guide - Diagram Display

## 🎯 CORRECT ENDPOINT TO CALL

### ❌ WRONG (What frontend might be calling now):
```
POST /generate-diagrams
```
- Only returns raw AI diagrams
- Empty when AI service unavailable
- No text extraction or processing

### ✅ CORRECT (What frontend should call):
```
POST /analyze-diagrams
```
- Extracts diagram texts from solution
- Works with fallback when AI service unavailable
- Returns processed, formatted diagram content

## 📋 Request Format
```javascript
const response = await fetch('http://localhost:5001/analyze-diagrams', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question_text: "Construct a triangle ABC in which BC = 6 cm, angle B = 60°, and angle C = 45°",
    subject: "Mathematics",
    solution_type: "with-diagram"
  })
});
```

## 🎨 Response Format (What frontend gets)
```json
{
  "success": true,
  "diagrams": [
    {
      "id": "diagram_1",
      "title": "Diagram 1",
      "content": "Base segment BC with given length"
    },
    {
      "id": "diagram_2", 
      "title": "Diagram 2",
      "content": "Angle constructed at point B"
    },
    {
      "id": "diagram_3",
      "title": "Diagram 3", 
      "content": "Angle constructed at point C"
    },
    {
      "id": "diagram_4",
      "title": "Diagram 4",
      "content": "Triangle ABC completed"
    }
  ],
  "content": "Diagram 1: Base segment BC with given length\n\nDiagram 2: Angle constructed at point B\n\nDiagram 3: Angle constructed at point C\n\nDiagram 4: Triangle ABC completed",
  "text_content": "Diagram 1: Base segment BC with given length\n\nDiagram 2: Angle constructed at point B\n\nDiagram 3: Angle constructed at point C\n\nDiagram 4: Triangle ABC completed",
  "svg": "<svg>...</svg>",
  "type": "combined_text",
  "elements_count": 4
}
```

## 🖥️ Frontend Implementation Options

### Option 1: Display Combined Content
```javascript
const response = await fetch('/analyze-diagrams', {...});
const data = await response.json();

// Display in right-side diagram area
document.getElementById('diagram-container').innerHTML = `
  <h3>Construction Diagrams</h3>
  <pre>${data.content}</pre>
`;
```

### Option 2: Display Individual Diagrams
```javascript
const response = await fetch('/analyze-diagrams', {...});
const data = await response.json();

// Display each diagram separately
let diagramHTML = '<h3>Construction Diagrams</h3>';
data.diagrams.forEach(diagram => {
  diagramHTML += `
    <div class="diagram-item">
      <h4>${diagram.title}</h4>
      <p>${diagram.content}</p>
    </div>
  `;
});

document.getElementById('diagram-container').innerHTML = diagramHTML;
```

### Option 3: Display SVG
```javascript
const response = await fetch('/analyze-diagrams', {...});
const data = await response.json();

// Display visual SVG
document.getElementById('diagram-container').innerHTML = data.svg;
```

## 🚀 Deployment
- Backend endpoint: `http://localhost:5001/analyze-diagrams`
- Production endpoint: `http://130.107.48.166:5001/analyze-diagrams`
- Method: POST
- Content-Type: application/json

## ✅ Expected Result
The right-side diagram area should display:
```
Diagram 1: Base segment BC with given length

Diagram 2: Angle constructed at point B

Diagram 3: Angle constructed at point C

Diagram 4: Triangle ABC completed
```
