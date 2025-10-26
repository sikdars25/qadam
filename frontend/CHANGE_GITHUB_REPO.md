# 🔄 Change Frontend GitHub Repository

## Current Repository
```
https://github.com/sikdars25/qadam_frontend.git
```

---

## ✅ Method 1: Change to New Repo (Keep History)

### Step 1: Create New GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `qadam-frontend-new` (or your preferred name)
3. **DO NOT** initialize with README, .gitignore, or license
4. Click **Create repository**
5. Copy the new repository URL (e.g., `https://github.com/sikdars25/qadam-frontend-new.git`)

### Step 2: Change Remote URL

```bash
cd d:/AI/_Programs/CBSE/aqnamic/frontend

# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/sikdars25/NEW_REPO_NAME.git

# Verify
git remote -v
```

### Step 3: Push to New Repository

```bash
# Push all branches
git push -u origin main

# Or if your branch is named master
git push -u origin master
```

---

## ✅ Method 2: Just Update Remote URL (Simpler)

If you just want to change the URL without removing:

```bash
cd d:/AI/_Programs/CBSE/aqnamic/frontend

# Update remote URL
git remote set-url origin https://github.com/sikdars25/NEW_REPO_NAME.git

# Verify
git remote -v

# Push
git push -u origin main
```

---

## ✅ Method 3: Using Batch Script

I can create a script to do this automatically:

```bash
change_frontend_repo.bat
```

---

## 📋 Complete Example

**Scenario:** Change from `qadam_frontend` to `qadam-app-frontend`

```bash
# 1. Create new repo on GitHub: qadam-app-frontend

# 2. Change remote
cd d:/AI/_Programs/CBSE/aqnamic/frontend
git remote set-url origin https://github.com/sikdars25/qadam-app-frontend.git

# 3. Push
git push -u origin main
```

---

## 🔍 Verify Change

```bash
# Check current remote
git remote -v

# Should show:
# origin  https://github.com/sikdars25/NEW_REPO_NAME.git (fetch)
# origin  https://github.com/sikdars25/NEW_REPO_NAME.git (push)
```

---

## ⚠️ Important Notes

### Keep Old Repo?
- **Yes:** Just change the remote URL, old repo stays as is
- **No:** You can delete the old repo from GitHub after pushing to new one

### Collaborators
- If others are working on this, notify them of the new repo URL
- They'll need to update their remotes too

### CI/CD
- If you have GitHub Actions, they'll automatically work with the new repo
- No changes needed to workflow files

---

## 🎯 Quick Commands

```bash
# Change to new repo (one command)
git remote set-url origin https://github.com/USERNAME/NEW_REPO.git

# Push to new repo
git push -u origin main
```

---

## 📝 What Happens

- ✅ All your code stays the same
- ✅ All commit history is preserved
- ✅ All branches are preserved
- ✅ Only the remote URL changes
- ✅ Old repo is not affected (unless you delete it)

---

**Ready to change? Just tell me the new repository URL!** 🚀
