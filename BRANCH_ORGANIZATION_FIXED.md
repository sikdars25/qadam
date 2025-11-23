# Branch Organization - FIXED

## ✅ Correct Branch Structure

### 🌐 main branch
- **Purpose**: Frontend application only
- **Contains**: 
  - `frontend/` - React application
  - `staticwebapp.config.json` - Azure deployment config
  - `.github/workflows/` - CI/CD pipelines
  - Documentation files
- **Deployed to**: Azure Static Web Apps

### 🔧 backend-proxy branch  
- **Purpose**: Proxy services and API endpoints
- **Contains**:
  - `proxy/` - Flask proxy application
  - `diagram_endpoint.py` - Separate diagram service
  - Proxy configuration and deployment scripts
- **Deployed to**: Proxy server (130.107.48.166)

### 🤖 backend-ai branch
- **Purpose**: AI services and machine learning
- **Contains**:
  - `ai/` - AI service implementation
  - ML models and processing
  - AI configuration files
- **Deployed to**: AI VM (130.107.48.221)

## 🚀 Deployment Commands

### Frontend (main branch)
```bash
cd frontend
npm run build
git add .
git commit -m "Update frontend"
git push origin main
# Auto-deploys to Azure Static Web Apps
```

### Proxy (backend-proxy branch)
```bash
git checkout backend-proxy
# Make changes to proxy/ or diagram_endpoint.py
git add .
git commit -m "Update proxy service"
git push origin backend-proxy
# Deploy to proxy server:
ssh qadamuser@130.107.48.166
cd /opt/qadam-backend
git pull origin backend-proxy
```

### AI Service (backend-ai branch)
```bash
git checkout backend-ai
# Make changes to ai/ folder
git add .
git commit -m "Update AI service"
git push origin backend-ai
# Deploy to AI VM:
ssh qadamuser@130.107.48.221
cd /opt/qadam-backend
git pull origin backend-ai
```

## 📋 Current Status

✅ **FIXED**: Main branch now contains ONLY frontend files
✅ **CORRECT**: Proxy files are in backend-proxy branch
✅ **CORRECT**: AI files are in backend-ai branch
✅ **DEPLOYED**: Diagram endpoint is in backend-proxy branch
✅ **READY**: Frontend calls separate endpoints correctly

## 🎯 Diagram Solution Architecture

### Frontend (main branch)
- `DualEndpointDiagramRenderer.js` calls two separate endpoints
- Text: `http://130.107.48.166/solve-question` (proxy)
- Diagrams: `http://130.107.48.166:5001/generate-diagrams` (diagram endpoint)

### Backend (backend-proxy branch)
- Main proxy: Port 5000 - handles text solutions
- Diagram endpoint: Port 5001 - handles diagram generation
- Both services run independently

### AI Service (backend-ai branch)
- AI processing on port 8001
- Generates diagrams and solutions
- Called by proxy services

This separation eliminates integration conflicts and ensures reliable diagram rendering!
