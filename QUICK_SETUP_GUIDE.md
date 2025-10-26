# 🚀 Quick Setup Guide - Git Remote & Push

## Problem

```
error: src refspec main does not match any
fatal: 'origin' does not appear to be a git repository
```

**Cause:** 
1. Your branch is `master`, not `main`
2. No remote repository configured

---

## ✅ Solution (3 Steps)

### Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: **`qadam`**
3. **DO NOT** initialize with README (you already have code)
4. Click **Create repository**
5. Copy the repository URL (e.g., `https://github.com/sikdars25/qadam.git`)

---

### Step 2: Add Remote & Push

**Option A: Use Script (Easiest)**
```bash
setup_git_remote.bat
```

**Option B: Manual Commands**
```bash
# Add remote
git remote add origin https://github.com/sikdars25/qadam.git

# Push to master branch
git push -u origin master
```

---

### Step 3: Verify

1. Go to: `https://github.com/sikdars25/qadam`
2. Check files are uploaded
3. Go to **Actions** tab
4. Workflow should be visible

---

## 📋 Current Status

- ✅ Branch: `master` (not main)
- ✅ Workflow: Updated to trigger on `master`
- ❌ Remote: Not configured (needs setup)

---

## 🔧 What Was Fixed

### Workflow File Updated

**Before:**
```yaml
on:
  push:
    branches:
      - main  # ❌ Your branch is master
```

**After:**
```yaml
on:
  push:
    branches:
      - master  # ✅ Matches your branch
```

---

## 🎯 Complete Setup Commands

```bash
# 1. Check current branch
git branch
# Output: * master

# 2. Add remote (replace with your URL)
git remote add origin https://github.com/sikdars25/qadam.git

# 3. Stage workflow file
git add .github/workflows/main_qadam-backend.yml

# 4. Commit
git commit -m "Add: GitHub Actions workflow for backend (monorepo)"

# 5. Push to master
git push -u origin master
```

---

## 🚨 Troubleshooting

### Error: "remote origin already exists"

```bash
# Update the URL instead
git remote set-url origin https://github.com/sikdars25/qadam.git
```

### Error: "repository not found"

**Cause:** Repository doesn't exist on GitHub

**Fix:** Create it first at https://github.com/new

### Error: "authentication failed"

**Cause:** Need to login to GitHub

**Fix:** 
1. Use GitHub Desktop, or
2. Setup Git credentials, or
3. Use SSH key

---

## ✅ After Setup

Once pushed, your repository will have:

```
https://github.com/sikdars25/qadam
├── .github/workflows/main_qadam-backend.yml  ← Workflow
├── backend/                                   ← Backend code
├── frontend/                                  ← Frontend code
└── README.md
```

---

## 🧪 Test Deployment

After pushing:

1. Go to: `https://github.com/sikdars25/qadam/actions`
2. Click on the workflow
3. Click **"Run workflow"**
4. Select branch: `master`
5. Click **"Run workflow"** button

---

## 📝 Quick Reference

| Command | Purpose |
|---------|---------|
| `git branch` | Check current branch |
| `git remote -v` | Check remote configuration |
| `git remote add origin URL` | Add remote repository |
| `git push -u origin master` | Push to master branch |

---

**Run:** `setup_git_remote.bat` for automated setup! 🚀
