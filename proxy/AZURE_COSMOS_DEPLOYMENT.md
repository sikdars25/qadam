# Azure Cosmos DB Deployment Guide

## Prerequisites
- Azure Cosmos DB database created with name: `qadam`
- Azure Function App deployed
- Cosmos DB API: **SQL (Core)**

## Step 1: Get Cosmos DB Connection Details

1. Go to **Azure Portal** → Your Cosmos DB Account
2. Navigate to **Settings** → **Keys**
3. Copy these values:
   - **URI**: `https://your-cosmosdb-account.documents.azure.com:443/`
   - **PRIMARY KEY**: Long alphanumeric string

## Step 2: Configure Azure Function App

1. Go to **Azure Portal** → Your Function App
2. Navigate to **Settings** → **Configuration**
3. Click **+ New application setting** for each:

### Required Settings

```
Name: COSMOS_ENDPOINT
Value: https://your-cosmosdb-account.documents.azure.com:443/

Name: COSMOS_KEY
Value: [Your PRIMARY KEY from Step 1]

Name: COSMOS_DATABASE
Value: qadam
```

### Keep Existing Settings
- `GROQ_API_KEY`
- `FRONTEND_URL`
- `SECRET_KEY`
- `SMTP_*` settings
- etc.

4. Click **Save** at the top
5. Click **Continue** to restart the Function App

## Step 3: Initialize Cosmos DB Containers

The containers will be **automatically created** on first run when the Function App starts.

Expected containers:
- `users` - User accounts
- `uploaded_papers` - Question papers
- `textbooks` - Textbooks
- `question_bank` - Saved questions
- `usage_logs` - Activity logs
- `ai_search_results` - AI search results
- `parsed_questions` - Parsed questions from papers

## Step 4: Verify Connection

### Check Function App Logs

1. Go to **Azure Portal** → Your Function App
2. Navigate to **Monitoring** → **Log stream**
3. Look for these messages:

```
✓ Connected to Cosmos DB: https://your-cosmosdb-account.documents.azure.com:443/
📦 Database 'qadam' ready
✓ Container 'users' ready - User accounts and authentication
✓ Container 'uploaded_papers' ready - Question papers uploaded by users
✓ Container 'textbooks' ready - Textbooks for different subjects
✓ Container 'question_bank' ready - Saved questions and solutions
✓ Container 'usage_logs' ready - User activity logs
✓ Container 'ai_search_results' ready - AI-powered search results
✓ Container 'parsed_questions' ready - Parsed questions from uploaded papers
✅ Cosmos DB initialization complete
```

### Test API Endpoints

Test these endpoints to verify Cosmos DB is working:

```bash
# Health check
GET https://your-function-app.azurewebsites.net/api/health

# Get papers (should return empty array initially)
GET https://your-function-app.azurewebsites.net/api/papers

# Get textbooks (should return empty array initially)
GET https://your-function-app.azurewebsites.net/api/textbooks
```

## Step 5: Deploy Updated Code

### Push Changes to GitHub

```bash
cd d:\AI\_Programs\CBSE\aqnamic
git add backend/cosmos_db.py backend/requirements.txt backend/.env.example
git commit -m "Update Cosmos DB configuration for Azure deployment"
git push origin main
```

### Redeploy Function App

If using GitHub Actions or Azure DevOps, the deployment will happen automatically.

Or manually:
1. Go to **Azure Portal** → Your Function App
2. Navigate to **Deployment** → **Deployment Center**
3. Click **Sync** to pull latest code

## Step 6: Migrate Existing Data (Optional)

If you have existing data in MySQL, use the migration script:

```bash
cd backend
python migrate_mysql_to_cosmos.py
```

This will copy all data from MySQL to Cosmos DB.

## Troubleshooting

### Connection Errors

**Error:** `❌ Error connecting to Cosmos DB`

**Solutions:**
1. Verify `COSMOS_ENDPOINT` is correct (should end with `:443/`)
2. Verify `COSMOS_KEY` is the PRIMARY KEY (not SECONDARY)
3. Check Cosmos DB firewall settings - allow Azure services
4. Ensure Function App has network access to Cosmos DB

### Container Not Found Errors

**Error:** `⚠️ Container not found`

**Solutions:**
1. Restart the Function App to trigger initialization
2. Manually create containers in Azure Portal:
   - Go to Cosmos DB → Data Explorer
   - Create containers with partition key `/user_id`, `/paper_id`, etc.

### Performance Issues

**Tips:**
1. Increase Cosmos DB throughput (RU/s) in Azure Portal
2. Use partition keys efficiently (already configured)
3. Enable indexing for frequently queried fields

## Cost Optimization

### Free Tier
- Azure Cosmos DB offers **400 RU/s free** per account
- Sufficient for development and small-scale production

### Production Settings
- Start with **400 RU/s per container** (minimum)
- Scale up based on usage
- Use **autoscale** for variable workloads

## Security Best Practices

1. **Never commit** `.env` file with real keys
2. Use **Azure Key Vault** for production secrets
3. Enable **firewall rules** in Cosmos DB
4. Rotate keys periodically
5. Use **Managed Identity** for Function App (advanced)

## Next Steps

1. ✅ Configure environment variables
2. ✅ Verify connection in logs
3. ✅ Test API endpoints
4. ✅ Upload test data
5. ✅ Monitor performance in Azure Portal

## Support

For issues, check:
- Function App logs
- Cosmos DB metrics in Azure Portal
- Application Insights (if enabled)

## Architecture

```
Frontend (Static Web App)
    ↓
Backend (Function App)
    ↓
Azure Cosmos DB (qadam database)
    ├── users
    ├── uploaded_papers
    ├── textbooks
    ├── question_bank
    ├── usage_logs
    ├── ai_search_results
    └── parsed_questions
```

All operations use Cosmos DB as primary database with MySQL as optional fallback.
