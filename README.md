# 🎓 Academic Portal - CBSE Question Paper Management System

A comprehensive AI-powered web application for managing CBSE question papers, solving questions, and organizing study materials. Built with React.js, Python Flask, SQLite, and Groq AI.

## 🎯 Core Features

### 📝 Question Management
- **Answer Full Paper**: Solve complete question papers with AI-powered solutions
- **Answer Chapterwise**: Map questions to textbook chapters and solve them contextually
- **Question Bank**: Auto-save solved questions with solutions for future reference
- **All Questions**: View and solve all parsed questions from uploaded papers

### 📤 Upload Hub
- **Upload Textbooks**: Upload and manage textbook PDFs with vectorization support
- **Upload Question Papers**: Upload papers with automatic question parsing
- **Vectorization Status**: Track which textbooks have been indexed for AI search
- **Parsing Status**: See which papers have been parsed into individual questions

### 🤖 AI-Powered Features
- **Automatic Question Parsing**: OCR + AI to extract questions from PDFs
- **Step-by-Step Solutions**: Detailed solutions with proper formatting
- **Semantic Chapter Mapping**: FAISS-based vector search for accurate question-chapter matching
- **Multi-tier OCR**: PaddleOCR, Groq Vision API, and Tesseract for accurate text extraction

## 🏗️ Architecture

### 3-Tier Application Structure:

1. **Frontend (Presentation Tier)**: React.js with Axios for API calls
2. **Backend (Application Tier)**: Python Flask REST API with AI services
3. **Database (Data Tier)**: SQLite with FAISS vector database for semantic search

### Technology Stack:
- **Frontend**: React 18, Axios, CSS3
- **Backend**: Flask, Groq AI API, FAISS, PyMuPDF
- **OCR**: PaddleOCR, Tesseract, Groq Vision API
- **Database**: SQLite (main), FAISS (vector search)

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn
- Tesseract OCR (for text extraction)
- Groq API Key (for AI features)

## 🚀 Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

4. Initialize the database:
```bash
python database.py
```

5. Start the Flask server:
```bash
python app.py
```

The backend server will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

### OCR Setup (Optional but Recommended)

1. Install Tesseract OCR:
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **Linux**: `sudo apt-get install tesseract-ocr`
   - **Mac**: `brew install tesseract`

2. Install PaddleOCR (for better math symbol recognition):
```bash
pip install paddleocr paddlepaddle
```

## 🔐 Default Login Credentials

The application comes with two pre-configured student accounts:

- **Student 1**
  - Username: `student1`
  - Password: `password123`

- **Student 2**
  - Username: `student2`
  - Password: `password123`

## 📁 Project Structure

```
aqnamic/
├── backend/
│   ├── app.py                    # Flask application & API endpoints
│   ├── database.py               # Database initialization & schema
│   ├── ai_service.py             # AI features (Groq, FAISS, chapter extraction)
│   ├── question_parser.py        # Question parsing with OCR + AI
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (Groq API key)
│   ├── academic.db              # SQLite database (auto-generated)
│   ├── uploads/                 # Uploaded papers directory
│   ├── textbooks/               # Uploaded textbooks directory
│   ├── vector_indices/          # FAISS vector indices for textbooks
│   └── diagrams/                # Extracted diagrams from papers
│
└── frontend/
    ├── public/
    │   └── index.html           # HTML template
    ├── src/
    │   ├── components/
    │   │   ├── Login.js         # Login page
    │   │   ├── Dashboard.js     # Main dashboard
    │   │   ├── Sidebar.js       # Navigation sidebar
    │   │   ├── SampleQuestions.js      # Answer Full Paper
    │   │   ├── ChapterQuestions.js     # Answer Chapterwise
    │   │   ├── QuestionBank.js         # Question Bank with filters
    │   │   ├── UploadPapers.js         # Upload Hub (textbooks & papers)
    │   │   ├── ParsedQuestionsView.js  # All Questions tab
    │   │   └── [Component].css         # Corresponding styles
    │   ├── App.js               # Main app component
    │   ├── index.js             # React entry point with axios config
    │   └── [styles].css         # Global styles
    └── package.json             # Node dependencies
```

## 🎨 Detailed Features

### 1. Answer Full Paper
- Select uploaded question papers by subject
- View all questions from the paper
- Solve questions with AI-powered step-by-step solutions
- Auto-save solutions to Question Bank
- Support for MCQs, short answers, and long answers
- Diagram detection and display

### 2. Answer Chapterwise
- Select question paper and textbook
- Map questions to textbook chapters using AI semantic search
- Filter questions by chapter
- View textbook pages for reference
- Solve questions with chapter context
- Track which questions have been solved

### 3. Question Bank
- View all solved questions with solutions
- Filter by question paper
- Search questions
- Alternating row colors for better readability
- View, delete, and manage saved questions
- Transparent badge design for clean UI

### 4. Upload Hub

#### Textbooks Tab:
- Upload textbook PDFs
- Auto-fill title from filename
- Vectorization status (Yes/No badges)
- Delete uploaded textbooks

#### Question Papers Tab:
- Upload question paper PDFs
- Automatic question parsing with OCR + AI
- Parsing status (Yes/No badges)
- Clean duplicate questions
- Delete uploaded papers

#### All Questions Tab:
- View all parsed questions from all papers
- Filter by paper and question type
- Search across all questions
- Solve questions directly from the list
- Auto-save to Question Bank

## 🛠️ API Endpoints

### Authentication
- `POST /api/login` - User authentication with session management
- `POST /api/logout` - Clear user session

### Question Papers
- `POST /api/upload-paper` - Upload question paper PDF
- `GET /api/uploaded-papers` - Get all uploaded papers
- `POST /api/parse-questions/<paper_id>` - Parse questions from paper
- `GET /api/parsed-questions` - Get all parsed questions
- `GET /api/parsed-questions?paper_id=<id>` - Get questions from specific paper
- `DELETE /api/delete-paper/<paper_id>` - Delete paper and its questions
- `POST /api/clean-duplicate-questions` - Remove duplicate questions

### Textbooks
- `POST /api/upload-textbook` - Upload textbook PDF
- `GET /api/textbooks` - Get all textbooks
- `GET /api/textbooks?subject=<subject>` - Get textbooks by subject
- `GET /api/textbook-pdf/<textbook_id>` - Serve textbook PDF
- `POST /api/extract-chapters/<textbook_id>` - Extract and vectorize chapters
- `DELETE /api/delete-textbook/<textbook_id>` - Delete textbook

### AI Features
- `POST /api/solve-question` - Get AI-powered solution for a question
- `POST /api/map-questions-to-chapters` - Map questions to chapters using FAISS

### Question Bank
- `POST /api/save-solved-question` - Save solved question to bank
- `GET /api/question-bank` - Get all saved questions for user
- `DELETE /api/question-bank/<question_id>` - Delete saved question

### Utilities
- `GET /api/diagram/<paper_id>/<filename>` - Serve extracted diagrams
- `GET /api/health` - Health check

## 🎯 Database Schema

### Users Table
- id, username (unique), password, full_name, created_at

### Uploaded Papers Table
- id, title, subject, file_path, uploaded_by (FK), uploaded_at

### Textbooks Table
- id, title, subject, author, file_path, uploaded_by (FK), is_indexed (boolean), uploaded_at

### Parsed Questions Table
- id, paper_id (FK), question_number, question_text, question_type
- sub_parts, has_diagram, has_math, marks, embedding_id, parsed_data (JSON), created_at

### Question Bank Table
- id, question_text, solution, source, paper_id (FK), textbook_id (FK)
- chapter_name, user_id (FK), created_at

### AI Search Results Table
- id, paper_id (FK), textbook_id (FK), search_results (JSON)
- total_chapters, total_questions, unmatched_count, created_at

## 🔧 Configuration

### Backend Configuration
- **Port**: 5000
- **Upload folders**: 
  - Papers: `backend/uploads/`
  - Textbooks: `backend/textbooks/`
  - Diagrams: `backend/diagrams/`
  - Vector indices: `backend/vector_indices/`
- **Allowed file types**: PDF, DOC, DOCX, TXT
- **Database**: `backend/academic.db`
- **Session secret**: Set in `app.secret_key` (change for production)
- **CORS**: Enabled with credentials support

### Frontend Configuration
- **Port**: 3000
- **API base URL**: `http://localhost:5000`
- **Axios**: Configured with `withCredentials: true` for session cookies

### Environment Variables (.env)
```bash
GROQ_API_KEY=your_groq_api_key_here
```

## 📝 Usage

1. **Start Backend**: `cd backend && python app.py`
2. **Start Frontend**: `cd frontend && npm start`
3. **Login**: Use Student 1 or Student 2 credentials
4. **Upload Materials**:
   - Go to "Upload Hub"
   - Upload textbooks (Textbooks tab)
   - Upload question papers (Question Papers tab)
   - Optionally vectorize textbooks for AI search
5. **Parse Questions**:
   - Click "Parse Questions" on uploaded papers
   - Wait for OCR + AI processing
   - View in "All Questions" tab
6. **Solve Questions**:
   - **Answer Full Paper**: Select paper and solve all questions
   - **Answer Chapterwise**: Map to textbook chapters and solve
   - **All Questions**: Solve any parsed question
7. **View Solutions**: Check "Question Bank" for all solved questions

## 🎨 UI/UX Features

- **Modern Design**: Purple gradient theme throughout
- **Responsive Layout**: Works on mobile and desktop
- **Smooth Animations**: Transitions and hover effects
- **Intuitive Navigation**: Sidebar with clear menu items
- **Clean Interface**: Alternating row colors, transparent badges
- **Color-Coded Status**: Green (Yes/Parsed/Vectorized), Red (No/Unparsed)
- **Icon-Only Actions**: Compact action buttons with tooltips
- **Modal Dialrams**: Click to enlarge diagrams
- **Solution Display**: Formatted with sections, diagrams, and final answers

## 🔒 Security Notes

**Current Implementation**:
- Flask session-based authentication
- Session cookies with credentials
- Basic password storage (plain text)

**For Production, Implement**:
- ✅ Password hashing (bcrypt, argon2)
- ✅ JWT tokens for stateless authentication
- ✅ HTTPS encryption (SSL/TLS)
- ✅ Input validation and sanitization
- ✅ Stricter CORS configuration
- ✅ Rate limiting on API endpoints
- ✅ File upload size limits
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection
- ✅ CSRF tokens

## 🚀 Deployment Considerations

### Backend
- Use production WSGI server (Gunicorn, uWSGI)
- Set strong `app.secret_key`
- Configure proper CORS origins
- Set up file storage (AWS S3, Azure Blob)
- Use production database (PostgreSQL, MySQL)
- Implement logging and monitoring
- Set up backup strategy for database and files

### Frontend
- Build for production: `npm run build`
- Serve with Nginx or Apache
- Configure environment variables
- Enable gzip compression
- Set up CDN for static assets
- Implement error tracking (Sentry)

### AI Services
- Monitor Groq API usage and limits
- Implement caching for repeated questions
- Set up fallback mechanisms
- Consider self-hosted AI models for privacy

## 🐛 Known Issues

- OCR accuracy depends on PDF quality
- Mathematical symbols may require manual verification
- Large PDFs (>50 pages) may take time to parse
- FAISS indexing requires sufficient memory
- Session management needs production-grade implementation

## 📄 License

This project is created for educational purposes.

## 👥 Support

For issues or questions, please refer to the documentation or contact your system administrator.
