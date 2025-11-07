# Branch Organization Guidelines

## Overview
This repository uses a clear branch separation to maintain clean separation between frontend and backend code.

## Branch Structure

### `main` Branch
- **Purpose**: Frontend React application only
- **Contents**: 
  - `frontend/` directory with React components
  - Frontend configuration files
  - Frontend dependencies (package.json, etc.)
  - Frontend documentation
- **Should NOT contain**:
  - Any backend OCR code
  - `ocr/` directory
  - Backend environment files
  - Python backend files

### `backend-ocr` Branch
- **Purpose**: Backend OCR service and mathematical processing
- **Contents**:
  - `ocr/` directory with Python OCR service
  - Backend configuration files
  - Backend dependencies (requirements.txt, etc.)
  - Backend documentation
  - Mathematical symbol processing code
- **Should NOT contain**:
  - Frontend React code
  - `frontend/` directory
  - Frontend dependencies

### Other Branches
- `backend-ai`: AI service backend
- `backend-proxy`: Proxy service backend
- `ocr-service`: Legacy OCR service (deprecated)

## Guidelines

### When to Commit to `main`
- Frontend React component changes
- UI/UX improvements
- Frontend dependency updates
- Frontend configuration changes
- Frontend math display improvements (KaTeX, MathJax, etc.)

### When to Commit to `backend-ocr`
- OCR service improvements
- Mathematical symbol detection changes
- Backend API modifications
- Python dependency updates
- Backend configuration changes
- OCR preprocessing enhancements

### Branch Switching Workflow
1. **For Frontend Work**: 
   ```bash
   git checkout main
   # Make frontend changes
   git add frontend/
   git commit -m "Frontend: description of changes"
   git push origin main
   ```

2. **For Backend OCR Work**:
   ```bash
   git checkout backend-ocr
   # Make backend changes
   git add ocr/
   git commit -m "Backend: description of changes"
   git push origin backend-ocr
   ```

### Common Mistakes to Avoid
1. **Never commit OCR code to main branch**
2. **Never commit frontend code to backend-ocr branch**
3. **Always check current branch before making changes**
4. **Use descriptive commit messages with "Frontend:" or "Backend:" prefixes**

### Verification Commands
- Check current branch: `git branch`
- Check what's being committed: `git status`
- Review changes before commit: `git diff --cached`

## Recent Cleanup Actions
- Removed `ocr/.env` from main branch (should only be in backend-ocr)
- Ensured main branch contains only frontend React code
- Maintained proper branch separation

This organization ensures:
- Clean deployment pipelines
- Clear code ownership
- Proper separation of concerns
- Easier code maintenance and debugging
