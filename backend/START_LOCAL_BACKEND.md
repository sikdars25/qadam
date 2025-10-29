# 🚀 Start MySQL and Backend Locally

## Quick Start

### Step 1: Start MySQL

**Option A: Run the batch file**
```bash
cd d:/AI/_Programs/CBSE/aqnamic/backend
start_mysql_local.bat
```

**Option B: Windows Services**
1. Press `Win + R`
2. Type: `services.msc`
3. Find "MySQL80" or "MySQL"
4. Right-click → **Start**

**Option C: Command Line (as Administrator)**
```bash
net start MySQL80
```

**Option D: MySQL Workbench**
- Open MySQL Workbench
- Click "Start" on your MySQL instance

---

### Step 2: Verify MySQL is Running

**Test connection:**
```bash
mysql -h localhost -u root -p
```

**Enter your MySQL root password**

**If successful, you'll see:**
```
mysql>
```

**Type `exit` to quit**

---

### Step 3: Check .env File

**Open:** `backend/.env`

**Verify these settings:**
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=qadam_academic
```

**Update the password to match your MySQL root password!**

---

### Step 4: Initialize Database

**Run:**
```bash
cd d:/AI/_Programs/CBSE/aqnamic/backend
python database.py
```

**This will:**
- Create the `qadam_academic` database
- Create all required tables
- Set up the schema

**Expected output:**
```
✓ Connected to MySQL database
✓ Users table ready
✓ Sample questions table ready
✓ Uploaded papers table ready
...
✅ MySQL database initialized successfully!
```

---

### Step 5: Start Flask Backend

**Run:**
```bash
cd d:/AI/_Programs/CBSE/aqnamic/backend
python app.py
```

**Expected output:**
```
✓ Connected to MySQL database
...
* Running on http://127.0.0.1:5000
* Debug mode: on
```

---

### Step 6: Test Backend

**Open browser:**
```
http://localhost:5000/api/health
```

**Should return:**
```json
{"status": "healthy"}
```

**Test login:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

---

## Troubleshooting

### MySQL Won't Start

**Error: "The service name is invalid"**

**Check MySQL service name:**
```bash
sc query | findstr MySQL
```

**Common names:**
- MySQL80
- MySQL
- MySQL57

**Start with correct name:**
```bash
net start MySQL80
```

---

### Can't Connect to MySQL

**Error: "Access denied for user 'root'@'localhost'"**

**Fix:**
1. Reset MySQL root password
2. Update `.env` file with correct password

**Error: "Can't connect to MySQL server on 'localhost'"**

**Fix:**
1. Check MySQL service is running
2. Check port 3306 is not blocked
3. Try: `127.0.0.1` instead of `localhost`

---

### Database Initialization Fails

**Error: "Database 'qadam_academic' doesn't exist"**

**Fix:**
```bash
mysql -u root -p -e "CREATE DATABASE qadam_academic;"
```

**Then run:**
```bash
python database.py
```

---

### Flask App Won't Start

**Error: "ModuleNotFoundError: No module named 'mysql'"**

**Fix:**
```bash
pip install mysql-connector-python
```

**Or install all dependencies:**
```bash
pip install -r requirements.txt
```

---

## Alternative: Use XAMPP

If you don't have MySQL installed:

### Install XAMPP:
1. Download: https://www.apachefriends.org/download.html
2. Install XAMPP
3. Open XAMPP Control Panel
4. Click "Start" next to MySQL

### Configure XAMPP MySQL:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=qadam_academic
```

**Note:** XAMPP MySQL default password is empty

---

## Quick Commands Reference

### Start MySQL:
```bash
net start MySQL80
```

### Stop MySQL:
```bash
net stop MySQL80
```

### Connect to MySQL:
```bash
mysql -u root -p
```

### Create Database:
```sql
CREATE DATABASE qadam_academic;
```

### Show Databases:
```sql
SHOW DATABASES;
```

### Use Database:
```sql
USE qadam_academic;
```

### Show Tables:
```sql
SHOW TABLES;
```

---

## Testing Locally vs Azure

### Local Backend:
- URL: `http://localhost:5000`
- Database: Local MySQL
- Files: Local filesystem
- Logs: Console output

### Azure Backend:
- URL: `https://qadam-backend.azurewebsites.net`
- Database: Azure MySQL (needs env vars)
- Files: Azure Blob Storage (recommended)
- Logs: Azure Log Stream

---

## Current Status

**You're testing locally to:**
1. ✅ Verify backend works
2. ✅ Test MySQL connection
3. ✅ Debug any issues
4. ✅ Prepare for Azure deployment

**After local testing works:**
- Add MySQL env vars in Azure Portal
- Test Azure deployment
- Verify everything works in production

---

## Next Steps

1. ✅ **Start MySQL** - Run start_mysql_local.bat
2. ✅ **Check .env** - Verify MySQL password
3. ✅ **Initialize DB** - Run python database.py
4. ✅ **Start Flask** - Run python app.py
5. ✅ **Test endpoints** - Check /api/health
6. ✅ **Test login** - Try logging in

---

**Run this now:**
```bash
cd d:/AI/_Programs/CBSE/aqnamic/backend
start_mysql_local.bat
```

Good luck! 🚀
