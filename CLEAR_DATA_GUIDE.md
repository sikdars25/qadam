# Clear All Data Guide

## 🗑️ Purpose

This script clears all papers, textbooks, and parsed questions from Cosmos DB. Use this when:
- You have data inconsistencies
- Delete operations are failing
- You want to start fresh with clean data

## ⚠️ What Gets Deleted

- ✅ **Uploaded Papers** - All question papers
- ✅ **Textbooks** - All textbook files
- ✅ **Parsed Questions** - All parsed question data
- ✅ **AI Search Results** - All AI search cache

## ✅ What's Preserved

- ✅ **User Accounts** - All users remain intact
- ✅ **Question Bank** - Saved questions are preserved
- ✅ **Usage Logs** - Activity history is kept

## 🚀 How to Run

### On the VM:

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Navigate to proxy folder
cd /opt/qadam-backend/proxy

# Activate virtual environment
source venv/bin/activate

# Run the script
python3 clear_all_data.py
```

### Expected Output:

```
============================================================
🗑️  CLEAR ALL DATA - Cosmos DB
============================================================

⚠️  WARNING: This will delete ALL data from:
   - Uploaded Papers
   - Textbooks
   - Parsed Questions
   - AI Search Results

Are you sure you want to continue? Type 'YES' to confirm: YES

🚀 Starting cleanup...

🗑️  Clearing Uploaded Papers...
   Found 15 items
   Deleted 10/15...
   ✅ Deleted 15 items

🗑️  Clearing Textbooks...
   Found 3 items
   ✅ Deleted 3 items

🗑️  Clearing Parsed Questions...
   Found 45 items
   Deleted 10/45...
   Deleted 20/45...
   Deleted 30/45...
   Deleted 40/45...
   ✅ Deleted 45 items

🗑️  Clearing AI Search Results...
   Found 0 items
   ✓ Container is already empty

============================================================
✅ Cleanup complete! Total items deleted: 63
============================================================

📝 Note: User accounts and question bank are preserved
   You can now upload papers and textbooks fresh
```

## 🔐 Safety Features

1. **Confirmation Required** - Must type 'YES' to proceed
2. **Detailed Logging** - Shows what's being deleted
3. **Error Handling** - Continues even if some items fail
4. **Preserves Users** - Never touches user accounts

## 🧪 After Cleanup

1. **Verify in Frontend:**
   - Go to Upload Resources → Should show no papers
   - Go to Textbooks → Should show no textbooks

2. **Upload Fresh Data:**
   - Upload new papers
   - Upload new textbooks
   - Parse questions
   - Everything should work normally

3. **Test Delete:**
   - Try deleting a newly uploaded paper
   - Should work without 404 errors

## 🐛 Troubleshooting

### Issue: Script can't connect to Cosmos DB

**Solution:** Check .env file has correct credentials
```bash
cat .env | grep COSMOS
```

### Issue: Permission denied

**Solution:** Make sure you're in the virtual environment
```bash
source venv/bin/activate
python3 clear_all_data.py
```

### Issue: Some items fail to delete

**Solution:** The script will continue and report failures. You can:
1. Run the script again
2. Manually delete from Azure Portal
3. Check the error messages for specific issues

## 📊 What Happens Behind the Scenes

1. **Queries all items** in each container using cross-partition query
2. **Iterates through items** and deletes one by one
3. **Uses correct partition key** for each container type
4. **Reports progress** every 10 items
5. **Counts successes and failures**

## 🔄 Alternative: Azure Portal

You can also clear data from Azure Portal:
1. Go to your Cosmos DB account
2. Click on **Data Explorer**
3. Select container (e.g., `uploaded_papers`)
4. Delete items manually or use SQL queries

## ⚡ Quick Commands

```bash
# On VM - One liner
cd /opt/qadam-backend/proxy && source venv/bin/activate && python3 clear_all_data.py

# Check what's in containers before clearing
python3 << 'EOF'
from cosmos_db import get_cosmos_container
for name in ['uploaded_papers', 'textbooks', 'parsed_questions']:
    container = get_cosmos_container(name)
    items = list(container.query_items(query="SELECT VALUE COUNT(1) FROM c", enable_cross_partition_query=True))
    print(f"{name}: {items[0]} items")
EOF
```

## 📝 Notes

- The script is **idempotent** - safe to run multiple times
- Deletion is **permanent** - cannot be undone
- **Blob storage files** are NOT deleted (only database records)
- Consider backing up important data before running

---

**Use this script to resolve data inconsistencies and start fresh!** 🎯
