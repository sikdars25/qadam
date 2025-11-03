# Run Backend Proxy Service Locally (Windows)

## Prerequisites

- Python 3.10 or 3.11
- Git
- 2GB+ RAM available

## Quick Start

### Option 1: Automated Setup (Recommended)

```powershell
# Navigate to proxy directory
cd d:\AI\_Programs\CBSE\aqnamic\proxy

# Run setup script
.\setup_local.bat
```

### Option 2: Manual Setup

```powershell
# 1. Navigate to directory
cd d:\AI\_Programs\CBSE\aqnamic
git checkout backend-proxy
cd proxy

# 2. Create virtual environment
python -m venv venv

# 3. Activate venv
.\venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Create .env file
copy .env.example .env
# Or create manually (see below)

# 6. Run the app
python app.py
```

## Environment Configuration

Create `.env` file in the `proxy` folder:

```env
# Backend Proxy Configuration

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database
DATABASE_URL=sqlite:///qadam.db

# API URLs
OCR_SERVICE_URL=http://130.107.48.145
AI_SERVICE_URL=http://130.107.48.221

# CORS
FRONTEND_URL=http://localhost:3000

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

## Running the Service

### First Time

```powershell
.\setup_local.bat
```

### Subsequent Runs

```powershell
.\run_local.bat
```

### Manual Run

```powershell
cd d:\AI\_Programs\CBSE\aqnamic\proxy
.\venv\Scripts\Activate.ps1
python app.py
```

## Testing

### Test Health Endpoint

```powershell
# In a new terminal
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Backend Proxy",
  "version": "1.0.0"
}
```

### Test API Endpoints

```powershell
# Test login
curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Test with authentication
curl http://localhost:5000/api/uploaded-papers -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
proxy/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── jwt_auth.py        # JWT authentication
├── ocr_client.py      # OCR service client
├── ai_client.py       # AI service client
├── question_parser.py # Question parsing logic
├── venv/              # Virtual environment (created)
└── qadam.db          # SQLite database (created on first run)
```

## Available Endpoints

### Public Endpoints
- `GET /api/health` - Health check
- `POST /api/login` - User login
- `POST /api/register` - User registration

### Protected Endpoints (Require JWT Token)
- `GET /api/uploaded-papers` - Get uploaded papers
- `POST /api/upload-paper` - Upload new paper
- `POST /api/parse-single-question` - Parse single question
- `GET /api/textbooks` - Get textbooks
- And more...

## Common Issues

### Issue 1: Port Already in Use

```
OSError: [WinError 10048] Only one usage of each socket address
```

**Fix:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F
```

### Issue 2: Module Not Found

```
ModuleNotFoundError: No module named 'flask'
```

**Fix:**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Issue 3: Database Error

```
sqlite3.OperationalError: no such table
```

**Fix:**
```powershell
# Delete old database
del qadam.db

# Restart app (will recreate database)
python app.py
```

### Issue 4: OCR/AI Service Connection Error

```
ConnectionError: Failed to connect to OCR service
```

**Fix:**
- Ensure OCR service is running at configured URL
- Update `OCR_SERVICE_URL` in `.env` file
- For local testing, you can run OCR service locally too

## Development Workflow

### Make Changes and Test

```powershell
# 1. Make changes to app.py or other files

# 2. Stop the server (Ctrl+C)

# 3. Restart
python app.py

# 4. Test
curl http://localhost:5000/api/health
```

### View Logs

The app prints logs to console. Watch for:
- Request logs
- Error messages
- Database operations
- API calls to OCR/AI services

## Database Management

### View Database

```powershell
# Install DB Browser for SQLite
# Or use Python

python
>>> import sqlite3
>>> conn = sqlite3.connect('qadam.db')
>>> cursor = conn.cursor()
>>> cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
>>> print(cursor.fetchall())
```

### Reset Database

```powershell
del qadam.db
python app.py
# Database will be recreated
```

## Integration with Frontend

If running frontend locally:

1. **Update frontend `.env`:**
   ```
   REACT_APP_API_URL=http://localhost:5000
   ```

2. **Update backend `.env`:**
   ```
   FRONTEND_URL=http://localhost:3000
   ```

3. **Start both services:**
   - Backend: `python app.py` (port 5000)
   - Frontend: `npm start` (port 3000)

## Stop the Server

Press `Ctrl+C` in the terminal where the app is running.

## Deactivate Virtual Environment

```powershell
deactivate
```

## Quick Reference

```powershell
# Setup (first time)
cd d:\AI\_Programs\CBSE\aqnamic\proxy
.\setup_local.bat

# Run (subsequent times)
.\run_local.bat

# Manual run
.\venv\Scripts\Activate.ps1
python app.py

# Test
curl http://localhost:5000/api/health

# Stop
Ctrl+C

# Deactivate
deactivate
```

## Next Steps

1. ✅ Backend running locally
2. Run frontend locally
3. Test full integration
4. Deploy to production

---

**Happy coding! 🚀**
