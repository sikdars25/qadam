# Cosmos DB Migration Guide: Local to Azure

## Overview

This guide helps you migrate data from your local Cosmos DB Emulator to Azure Cosmos DB in production.

## Prerequisites

1. ✅ Azure Cosmos DB account created (database name: `qadam`)
2. ✅ Local Cosmos DB Emulator running with data
3. ✅ Python environment with `azure-cosmos` package installed

## Step 1: Get Azure Cosmos DB Credentials

### From Azure Portal:

1. Go to **Azure Portal** → Your Cosmos DB Account
2. Navigate to **Settings** → **Keys**
3. Copy these values:
   - **URI** (Endpoint): `https://your-account.documents.azure.com:443/`
   - **PRIMARY KEY**: Long alphanumeric string

## Step 2: Configure Environment Variables

### Update your `.env` file:

```bash
# Azure Cosmos DB (Production)
COSMOS_ENDPOINT=https://your-cosmosdb-account.documents.azure.com:443/
COSMOS_KEY=your_primary_key_from_azure_portal
COSMOS_DATABASE=qadam

# Local Cosmos DB Emulator (optional - for migration)
COSMOS_ENDPOINT_LOCAL=https://localhost:8081
COSMOS_KEY_LOCAL=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
COSMOS_DATABASE_LOCAL=qadam_academic
```

## Step 3: Run Migration

### Option A: Using Batch Script (Windows)

```bash
cd backend
migrate_to_azure_cosmos.bat
```

### Option B: Using Python Directly

```bash
cd backend
python migrate_local_to_azure_cosmos.py
```

## What Gets Migrated

The script migrates all containers and their documents:

| Container | Partition Key | Description |
|-----------|---------------|-------------|
| `users` | `/user_id` | User accounts and authentication |
| `uploaded_papers` | `/paper_id` | Question papers uploaded by users |
| `textbooks` | `/textbook_id` | Textbooks for different subjects |
| `question_bank` | `/user_id` | Saved questions and solutions |
| `usage_logs` | `/user_id` | User activity logs |
| `parsed_questions` | `/paper_id` | Parsed questions from papers |
| `ai_search_results` | `/paper_id` | AI-powered search results |

## Migration Process

The script will:

1. ✅ Connect to local Cosmos DB Emulator
2. ✅ Connect to Azure Cosmos DB
3. ✅ Create containers in Azure (if they don't exist)
4. ✅ Copy all documents from local to Azure
5. ✅ Skip documents that already exist (by ID)
6. ✅ Generate migration log file

## Sample Output

```
======================================================================
🚀 Cosmos DB Migration: Local Emulator → Azure
======================================================================

📍 Source: https://localhost:8081 (Database: qadam_academic)
📍 Target: https://your-account.documents.azure.com:443/ (Database: qadam)

⚠️  WARNING: This will copy all data from local to Azure.
   Existing documents with same IDs will be skipped.

Proceed with migration? (yes/no): yes

🔌 Connecting to local Cosmos DB emulator...
✓ Connected to: https://localhost:8081

🔌 Connecting to Azure Cosmos DB...
✓ Connected to: https://your-account.documents.azure.com:443/

======================================================================
📦 Starting container migration...
======================================================================

📂 Migrating container: users
  ✓ Container 'users' already exists
  📖 Reading documents from local...
  📊 Found 5 documents
    ✓ Migrated: user_001
    ✓ Migrated: user_002
    ✓ Migrated: user_003
    ✓ Migrated: user_004
    ✓ Migrated: user_005
  ✅ Migration complete: 5 migrated, 0 skipped

📂 Migrating container: uploaded_papers
  ✓ Container 'uploaded_papers' already exists
  📖 Reading documents from local...
  📊 Found 3 documents
    ✓ Migrated: 08d7dae3-71ff-4fc8-8fcf-61156c0a5ba2
    ✓ Migrated: 2fe2ec5b-6203-4c99-baca-b896e30bdd21
    ✓ Migrated: 21dbbbd2-71f0-4c0c-9700-dbbb61b93540
  ✅ Migration complete: 3 migrated, 0 skipped

...

======================================================================
✅ MIGRATION COMPLETE
======================================================================
📊 Total documents migrated: 25
⏭  Total documents skipped: 0
📦 Containers processed: 7

🌐 Azure Cosmos DB: https://your-account.documents.azure.com:443/
📁 Database: qadam

✨ Your data is now in Azure Cosmos DB!

📝 Migration log saved: migration_log_20251028_214530.json
```

## Verification

### Check Azure Portal:

1. Go to **Azure Portal** → Your Cosmos DB Account
2. Navigate to **Data Explorer**
3. Expand database `qadam`
4. Check each container for documents

### Check Migration Log:

The script creates a JSON log file: `migration_log_YYYYMMDD_HHMMSS.json`

```json
{
  "timestamp": "2025-10-28T21:45:30.123456",
  "source": "https://localhost:8081",
  "target": "https://your-account.documents.azure.com:443/",
  "database": "qadam",
  "total_migrated": 25,
  "total_skipped": 0,
  "containers": [
    "users",
    "uploaded_papers",
    "textbooks",
    "question_bank",
    "usage_logs",
    "parsed_questions",
    "ai_search_results"
  ]
}
```

## Re-running Migration

The script is **idempotent** - you can run it multiple times safely:

- ✅ Existing documents (same ID) will be **skipped**
- ✅ New documents will be **migrated**
- ✅ No data will be **overwritten**

## Troubleshooting

### Error: "Azure Cosmos DB credentials not found"

**Solution:** Make sure `.env` file has:
```bash
COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_KEY=your_primary_key_here
```

### Error: "Failed to connect to local Cosmos DB"

**Solution:** 
1. Start Cosmos DB Emulator
2. Check it's running at `https://localhost:8081`
3. Verify emulator certificate is trusted

### Error: "Failed to connect to Azure Cosmos DB"

**Solution:**
1. Verify `COSMOS_ENDPOINT` is correct (ends with `:443/`)
2. Verify `COSMOS_KEY` is the PRIMARY KEY (not SECONDARY)
3. Check Azure Cosmos DB firewall settings
4. Ensure your IP is allowed (or allow Azure services)

### Error: "Container not found in source database"

**Solution:** This is normal if you haven't used that container locally. The script will skip it.

## Post-Migration

### Update Application Configuration

After migration, update your application to use Azure Cosmos DB:

**For Azure Function App:**
1. Go to **Azure Portal** → Your Function App
2. Navigate to **Configuration** → **Application Settings**
3. Update:
   ```
   COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
   COSMOS_KEY=your_primary_key
   COSMOS_DATABASE=qadam
   ```

**For Local Development:**
- Keep using local emulator, OR
- Update `.env` to point to Azure

### Verify Application

1. ✅ Test user login
2. ✅ Upload a test paper
3. ✅ Parse questions
4. ✅ Search textbooks
5. ✅ Check all features work

## Rollback

If you need to rollback:

1. **Local data is NOT deleted** - it remains in the emulator
2. **Azure data can be deleted** - delete containers in Azure Portal
3. **Re-run migration** if needed

## Best Practices

1. ✅ **Backup first** - Export local data before migration
2. ✅ **Test in dev** - Migrate to a test Cosmos DB account first
3. ✅ **Verify data** - Check Azure Portal after migration
4. ✅ **Monitor costs** - Check Azure Cosmos DB RU/s usage
5. ✅ **Keep logs** - Save migration log files

## Cost Optimization

### Free Tier
- Azure Cosmos DB offers **400 RU/s free** per account
- Sufficient for development and small-scale production

### Production
- Start with **400 RU/s per container** (minimum)
- Use **autoscale** for variable workloads
- Monitor usage in Azure Portal

## Support

For issues:
- Check migration log file
- Review Azure Portal → Cosmos DB → Metrics
- Check Function App logs

## Next Steps

1. ✅ Run migration script
2. ✅ Verify data in Azure Portal
3. ✅ Update Function App configuration
4. ✅ Test application
5. ✅ Monitor performance

Your data is now in Azure Cosmos DB and ready for production! 🎉
