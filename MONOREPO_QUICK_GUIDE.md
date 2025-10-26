# ⚡ Quick Guide: Setup Monorepo

## Goal
```
https://github.com/sikdars25/qadam
├── frontend/     (React code)
└── backend/      (Python code)
```

---

## 🚀 Quick Setup (5 Minutes)

### 1. Create GitHub Repository
- Go to: https://github.com/new
- Name: `qadam`
- ✅ Add README
- Click **Create**

### 2. Run Setup Script
```bash
cd d:/AI/_Programs/CBSE/aqnamic
setup_monorepo.bat
```

### 3. Done! ✅

---

## 📋 What the Script Does

1. ✅ Clones new `qadam` repository
2. ✅ Copies `frontend/` code (React app)
3. ✅ Copies `backend/` code (Python app)
4. ✅ Creates root `.gitignore`
5. ✅ Creates root `README.md`
6. ✅ Commits everything
7. ✅ Pushes to GitHub

---

## 🎯 Result

Your repository will look like:
```
qadam/
├── .gitignore
├── README.md
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
└── backend/
    ├── app.py
    ├── ai_service.py
    ├── database.py
    ├── requirements.txt
    ├── .env.example
    └── README.md
```

---

## 🔧 After Setup

### Run Frontend
```bash
cd qadam/frontend
npm install
npm start
```

### Run Backend
```bash
cd qadam/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## 📦 Old Repositories

After confirming the monorepo works:

**Option 1: Archive**
- Go to old repo → Settings → Archive

**Option 2: Delete**
- Go to old repo → Settings → Delete

---

**Run:** `setup_monorepo.bat` to create your monorepo! 🚀
