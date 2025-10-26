# 🏗️ Setup Monorepo Structure

## Goal
Create a single repository with this structure:
```
https://github.com/sikdars25/qadam
├── frontend/          (React app)
├── backend/           (Python Flask app)
└── README.md
```

---

## ✅ Method 1: Create New Monorepo (Recommended)

### Step 1: Create New GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `qadam`
3. Description: "CBSE Question Bank Academic Management System"
4. **Public** or **Private** (your choice)
5. ✅ **Add a README file**
6. Click **Create repository**

### Step 2: Clone the New Repository

```bash
cd d:/AI/_Programs/CBSE
git clone https://github.com/sikdars25/qadam.git
cd qadam
```

### Step 3: Copy Frontend Code

```bash
# Copy frontend files (excluding git and node_modules)
xcopy d:\AI\_Programs\CBSE\aqnamic\frontend frontend\ /E /I /EXCLUDE:exclude.txt

# Create exclude.txt first with:
# node_modules
# .git
# build
```

### Step 4: Copy Backend Code

```bash
# Copy backend files (excluding git, venv, and cache)
xcopy d:\AI\_Programs\CBSE\aqnamic\backend backend\ /E /I /EXCLUDE:exclude.txt

# Add to exclude.txt:
# venv
# __pycache__
# .env
```

### Step 5: Create Root Files

Create `.gitignore` in root:
```
# Frontend
frontend/node_modules/
frontend/build/
frontend/.env.local

# Backend
backend/venv/
backend/__pycache__/
backend/.env
backend/*.pyc
backend/uploads/
backend/diagrams/
backend/textbooks/
backend/vector_db/
backend/vector_indices/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

Create `README.md` in root:
```markdown
# Qadam - CBSE Academic Management System

Full-stack application for CBSE question paper management.

## Structure
- `frontend/` - React application
- `backend/` - Python Flask API

## Setup
See individual README files in frontend/ and backend/ folders.
```

### Step 6: Commit and Push

```bash
git add .
git commit -m "Initial commit: Add frontend and backend"
git push origin main
```

---

## ✅ Method 2: Using Automated Script

I'll create a script to do this automatically:

```bash
setup_monorepo.bat
```

This will:
1. Create the new structure
2. Copy files (excluding unnecessary folders)
3. Set up .gitignore
4. Create README
5. Initialize git
6. Push to GitHub

---

## 📁 Final Structure

```
qadam/
├── .gitignore
├── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── README.md
└── backend/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    └── README.md
```

---

## 🔧 Update GitHub Actions

After moving to monorepo, update workflow paths:

**Frontend workflow** (`.github/workflows/frontend.yml`):
```yaml
on:
  push:
    paths:
      - 'frontend/**'
```

**Backend workflow** (`.github/workflows/backend.yml`):
```yaml
on:
  push:
    paths:
      - 'backend/**'
```

---

## 🎯 Benefits of Monorepo

- ✅ Single repository to manage
- ✅ Easier to keep frontend/backend in sync
- ✅ Shared documentation
- ✅ Single issue tracker
- ✅ Easier deployment coordination

---

## ⚠️ What About Old Repos?

**Option 1: Keep them**
- Archive the old repos on GitHub
- Add note: "Moved to https://github.com/sikdars25/qadam"

**Option 2: Delete them**
- After confirming monorepo works
- Delete old `qadam_frontend` and `qadam_backend` repos

---

## 📋 Migration Checklist

- [ ] Create new `qadam` repository on GitHub
- [ ] Clone new repository locally
- [ ] Copy frontend code to `frontend/` folder
- [ ] Copy backend code to `backend/` folder
- [ ] Create root `.gitignore`
- [ ] Create root `README.md`
- [ ] Update GitHub Actions workflows
- [ ] Commit and push
- [ ] Test both frontend and backend
- [ ] Archive or delete old repositories

---

**Ready to set up? I can create the automated script!** 🚀
