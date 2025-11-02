# Verify and Update Backend on VM

## 🔍 Check Current Code Version

**On VM:**
```bash
ssh qadamuser@130.107.48.166

cd /opt/qadam-backend

# Check current commit
git log --oneline -1

# Should show: a9e334f improve-cosmos-delete-error-handling
```

If it shows an older commit, update it:

## 🔄 Update Code

```bash
cd /opt/qadam-backend

# Pull latest changes
git pull origin backend-proxy

# Verify the update
git log --oneline -1

# Should now show: a9e334f improve-cosmos-delete-error-handling

# Check the cosmos_db.py file has the new code
grep -A 5 "Attempting to delete paper_id" proxy/cosmos_db.py

# Should show the detailed logging with type information
```

## 🔄 Restart Service

```bash
# Restart the backend service
sudo systemctl restart qadam-backend

# Wait a moment
sleep 3

# Check status
sudo systemctl status qadam-backend

# Watch logs in real-time
sudo journalctl -u qadam-backend -f
```

## 🧪 Test Delete Again

1. Go to frontend Upload Resources screen
2. Try to delete a paper
3. Watch the logs

**Expected new logs:**
```
🔍 Attempting to delete paper_id=8a846bf5-1006-4678-8a50-c338defc6a76 (type: str) with partition_key=1 (type: int)
```

This will show us the exact types and help identify the issue.

## 🚨 If Still Not Updated

If `git pull` says "Already up to date" but you're on an old commit:

```bash
cd /opt/qadam-backend

# Check current branch
git branch

# Should show: * backend-proxy

# Force update
git fetch origin
git reset --hard origin/backend-proxy

# Verify
git log --oneline -1

# Restart
sudo systemctl restart qadam-backend
```

## 📋 Quick One-Liner

```bash
ssh qadamuser@130.107.48.166 "cd /opt/qadam-backend && git pull origin backend-proxy && sudo systemctl restart qadam-backend && sleep 3 && sudo systemctl status qadam-backend"
```
