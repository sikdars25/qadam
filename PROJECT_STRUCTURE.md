# QAdam Project Structure

## 📁 Directory Layout

```
qadam/
├── frontend/                    # React Frontend (Azure Static Web App)
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/                     # Main Backend (Azure Function App)
│   ├── HttpTrigger/            # Azure Function trigger
│   ├── app.py                  # Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── cosmos_db.py            # Cosmos DB operations
│   ├── ai_service_new.py       # AI service (Groq + TF-IDF)
│   ├── blob_storage.py         # Azure Blob Storage helper
│   ├── ocr_client.py           # OCR service client
│   └── question_parser.py      # Question parsing logic
│
├── ocr/                        # OCR Service (Separate Azure Function App)
│   ├── HttpTrigger/            # Azure Function trigger
│   ├── app.py                  # Flask app with PaddleOCR
│   ├── requirements.txt        # OCR-specific dependencies
│   ├── README.md               # API documentation
│   └── AZURE_SETUP.md          # Deployment guide
│
└── .github/
    └── workflows/
        ├── azure-static-web-apps.yml      # Frontend deployment
        ├── main_qadam-backend.yml         # Backend deployment
        └── deploy-ocr-function.yml        # OCR service deployment
```

## 🎯 Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│              (Azure Static Web App)                          │
│                                                              │
│  - React UI                                                  │
│  - User authentication                                       │
│  - File uploads                                              │
│  - Question display                                          │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Main Backend                              │
│                (qadam-backend)                               │
│                                                              │
│  - API Routes                                                │
│  - Business Logic                                            │
│  - Cosmos DB (database)                                      │
│  - Blob Storage (file storage)                               │
│  - AI Service (Groq + TF-IDF)                                │
│  - Question Parsing                                          │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   │ (calls OCR service)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    OCR Service                               │
│                  (qadam-ocr)                                 │
│                                                              │
│  - PaddleOCR Engine                                          │
│  - Image OCR                                                 │
│  - PDF OCR                                                   │
│  - 80+ Languages                                             │
│  - Handwriting Recognition                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Deployment

### Frontend
- **Platform:** Azure Static Web Apps
- **Trigger:** Push to `main` branch (frontend/ changes)
- **URL:** `https://your-app.azurestaticapps.net`

### Main Backend
- **Platform:** Azure Function App (Consumption Plan)
- **Trigger:** Push to `main` branch (backend/ changes)
- **URL:** `https://qadam-backend.azurewebsites.net`

### OCR Service
- **Platform:** Azure Function App (Consumption Plan)
- **Trigger:** Push to `main` branch (ocr/ changes)
- **URL:** `https://qadam-ocr.azurewebsites.net`

## 📦 Dependencies

### Frontend
- React 18
- React Router
- Axios
- TailwindCSS

### Main Backend
- Flask 2.3.3
- Azure Cosmos DB
- Azure Blob Storage
- Groq API (AI)
- scikit-learn (TF-IDF)
- PyMuPDF (PDF processing)

### OCR Service
- Flask 2.3.3
- PaddleOCR 2.7.3
- PaddlePaddle 2.5.2
- OpenCV
- PyMuPDF

## 🔧 Environment Variables

### Frontend
```
REACT_APP_API_URL=https://qadam-backend.azurewebsites.net
```

### Main Backend
```
COSMOS_ENDPOINT=https://...
COSMOS_KEY=...
COSMOS_DATABASE=qadam
AZURE_STORAGE_CONNECTION_STRING=...
BLOB_CONTAINER_NAME=qadam-uploads
GROQ_API_KEY=...
OCR_SERVICE_URL=https://qadam-ocr.azurewebsites.net
FRONTEND_URL=https://your-app.azurestaticapps.net
```

### OCR Service
```
FRONTEND_URL=https://your-app.azurewebsites.net
DEFAULT_OCR_LANGUAGE=en
```

## 💰 Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Static Web App | Free | $0 |
| Function App (Backend) | Consumption | ~$0 (within free tier) |
| Function App (OCR) | Consumption | ~$0 (within free tier) |
| Cosmos DB | Free Tier | $0 (400 RU/s, 25 GB) |
| Blob Storage | Standard LRS | ~$0 (within free tier) |
| Groq API | Free | $0 |
| **Total** | | **$0/month** |

## 🎯 Key Features

### Main Backend
- ✅ User authentication & sessions
- ✅ Question paper upload & parsing
- ✅ Textbook indexing (TF-IDF)
- ✅ AI-powered solution generation (Groq)
- ✅ Semantic search
- ✅ Persistent file storage (Blob)
- ✅ NoSQL database (Cosmos DB)

### OCR Service
- ✅ Image text extraction
- ✅ PDF text extraction
- ✅ 80+ language support
- ✅ Handwriting recognition
- ✅ High accuracy (PaddleOCR)
- ✅ No system dependencies

## 📚 Documentation

- **Frontend:** `frontend/README.md`
- **Backend:** `backend/README.md`
- **OCR Service:** `ocr/README.md`
- **OCR Setup:** `ocr/AZURE_SETUP.md`
- **Blob Storage:** `backend/BLOB_STORAGE_SETUP.md`
- **AI Migration:** `backend/MIGRATION_TO_NEW_AI.md`
- **Azure Limitations:** `backend/AZURE_LIMITATIONS.md`

## 🔗 Quick Links

- **GitHub Repository:** https://github.com/YOUR_USERNAME/qadam
- **Frontend:** https://your-app.azurestaticapps.net
- **Backend API:** https://qadam-backend.azurewebsites.net/api
- **OCR API:** https://qadam-ocr.azurewebsites.net/api
- **GitHub Actions:** https://github.com/YOUR_USERNAME/qadam/actions

## 🛠️ Local Development

### Frontend
```bash
cd frontend
npm install
npm start
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### OCR Service
```bash
cd ocr
pip install -r requirements.txt
python app.py
```

## 🎉 Status

- ✅ Frontend deployed
- ✅ Backend deployed
- ✅ OCR service ready (needs Azure setup)
- ✅ Cosmos DB configured
- ✅ Blob Storage configured
- ✅ AI service migrated to Groq
- ✅ All dependencies optimized for Azure free tier
