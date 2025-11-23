# Diagram Display Troubleshooting Guide

## Problem: No diagrams showing in solution area

## Quick Diagnosis

### 1. Check if Frontend Changes are Deployed
Open browser developer console (F12) and run:

```javascript
// Check if DiagramRenderer component is loaded
console.log('DiagramRenderer available:', typeof DiagramRenderer !== 'undefined');

// Check if the component has fallback logic
const testQuestion = 'Construct a triangle ABC';
console.log('Should detect geometry:', testQuestion.toLowerCase().includes('triangle'));
```

### 2. Check Network Requests
In Network tab of developer tools:
1. Submit a geometry question with "with-diagram" selected
2. Look for the `/solve-question` request
3. Check the response:
   - `has_diagrams: false` → Frontend should show fallback
   - `has_diagrams: true` → Backend is generating diagrams

### 3. Check Console for Errors
Look for any JavaScript errors related to:
- DiagramRenderer component
- SVG rendering issues
- Component import errors

## Step-by-Step Fix

### Step 1: Verify Frontend Deployment ✅
The enhanced frontend code has been pushed to main branch. Ensure:

```bash
# On your frontend deployment server
git pull origin main
npm run build  # or your build command
# Restart your frontend service
```

### Step 2: Clear Browser Cache
1. Open Developer Tools (F12)
2. Right-click refresh button → "Empty Cache and Hard Reload"
3. Or use Ctrl+Shift+R (Cmd+Shift+R on Mac)

### Step 3: Test with Geometry Question
Use this exact question:
```
Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°. Draw the figure with all steps of construction and label the diagram clearly
```

**Expected Result:**
- Should see a blue dashed border container labeled "📐 triangle"
- Should show an SVG triangle with vertices A, B, C
- Should show construction steps

### Step 4: If Still Not Working, Check Component Loading

Add temporary debug code to `QuestionSolver.js`:

```javascript
// Add this right before the DiagramRenderer calls
console.log('Debug - Solution data:', {
  has_diagrams: solution.has_diagrams,
  questionText: solution.questionText,
  solutionLength: solution.solution?.length
});

// Add this to check if geometry detection works
const isGeometry = solution.questionText && 
  ['triangle', 'construct', 'draw'].some(keyword => 
    solution.questionText.toLowerCase().includes(keyword.toLowerCase())
  );
console.log('Debug - Is geometry question:', isGeometry);
```

## Backend Issues (If frontend is deployed but still no diagrams)

### Check AI Service Status
```bash
# On AI VM (130.107.48.221)
curl http://localhost:8001/api/health
# Should return: {"status": "ok"} or similar

# If not running:
sudo systemctl restart qadam-ai
```

### Check Proxy Configuration
```bash
# On Proxy VM (130.107.48.166)
cd /opt/qadam-backend/proxy
cat .env | grep AI_SERVICE_URL
# Should show: AI_SERVICE_URL=http://130.107.48.221:8001

# Restart proxy if needed
sudo systemctl restart qadam-backend
```

### Test Backend Directly
```bash
# On Proxy VM
curl -X POST http://localhost:5000/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Construct a triangle ABC in which BC = 6 cm, ∠B = 60°, and ∠C = 45°",
    "subject": "Mathematics",
    "solution_type": "with-diagram"
  }'
```

## Expected Behaviors

### ✅ Working Frontend (Current State)
- Geometry questions show fallback diagrams
- SVG triangle with labels
- Construction steps in styled container
- Blue dashed border around diagram area

### ✅ Working Full System (After AI Service Fix)
- All frontend features above
- Plus AI-generated diagram descriptions
- `has_diagrams: true` in response
- Diagram count in metadata

### ❌ Broken System
- No diagram containers at all
- Plain text solution only
- No visual elements

## Emergency Fix: Force Fallback Diagrams

If the enhanced frontend isn't deployed, you can temporarily force diagrams to show:

1. Open `QuestionSolver.js`
2. Find the diagram rendering section
3. Add this temporary code:

```javascript
// Temporary force diagrams for geometry questions
const isGeometry = solution.questionText && 
  ['triangle', 'construct', 'draw', 'circle'].some(keyword => 
    solution.questionText.toLowerCase().includes(keyword.toLowerCase())
  );

if (isGeometry && !solution.has_diagrams) {
  // Force has_diagrams to true for geometry questions
  solution.has_diagrams = true;
  solution.diagrams = [{
    type: 'geometry',
    description: 'Geometry construction diagram'
  }];
}
```

## Deployment Checklist

### Frontend ✅ (Completed)
- [x] Enhanced DiagramRenderer pushed to main
- [x] Fallback logic implemented
- [x] SVG diagrams added
- [x] Styling updated

### Backend ⏳ (Needs Action)
- [ ] Verify AI service is running
- [ ] Check proxy configuration
- [ ] Test end-to-end functionality

### Production ⏳ (Needs Action)
- [ ] Deploy latest frontend code
- [ ] Clear CDN/cache if applicable
- [ ] Test with geometry questions

## Contact Information

If after following these steps diagrams still don't show:

1. **Frontend Issue**: Check browser console for JavaScript errors
2. **Backend Issue**: Check server logs for AI service errors
3. **Deployment Issue**: Verify you're using the latest code from main branch

The fallback diagram feature should work independently of the AI service once the frontend is properly deployed.
