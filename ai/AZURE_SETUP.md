# Azure Setup Guide for AI Function App

## Prerequisites

- Azure account
- Groq API key from https://console.groq.com

## Step 1: Create Azure Function App

1. Go to Azure Portal (https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Function App" and click "Create"

### Configuration:
- **Subscription**: Your subscription
- **Resource Group**: Create new or use existing (e.g., `qadam_ai_group`)
- **Function App name**: `qadam-ai`
- **Runtime stack**: Python
- **Version**: 3.10
- **Region**: Choose closest to your users
- **Operating System**: Linux
- **Plan type**: Consumption (Serverless)

4. Click "Review + Create" then "Create"

## Step 2: Download Publish Profile

1. Go to your Function App: `qadam-ai`
2. Click "Get publish profile" in the top menu
3. Save the downloaded `.PublishSettings` file

## Step 3: Add GitHub Secret

1. Go to your GitHub repository: https://github.com/sikdars25/qadam/settings/secrets/actions
2. Click "New repository secret"
3. Name: `AZURE_AI_FUNCTIONAPP_PUBLISH_PROFILE`
4. Value: Paste the entire contents of the `.PublishSettings` file
5. Click "Add secret"

## Step 4: Configure Environment Variables

1. Go to Azure Portal → `qadam-ai` Function App
2. Click "Configuration" in the left menu
3. Click "Application settings"
4. Click "+ New application setting"

Add the following:

### Required:
- **Name**: `GROQ_API_KEY`
- **Value**: Your Groq API key from https://console.groq.com

5. Click "Save" at the top
6. Click "Continue" to restart the app

## Step 5: Enable CORS (Optional)

If you need to call this from a web frontend:

1. Go to Azure Portal → `qadam-ai` Function App
2. Click "CORS" in the left menu
3. Add allowed origins:
   - `https://zealous-ocean-06e22b51e.3.azurestaticapps.net` (your frontend)
   - `http://localhost:3000` (for local development)
4. Click "Save"

## Step 6: Deploy

1. Push code to `backend-ai` branch:
```bash
git checkout backend-ai
git push origin backend-ai
```

2. GitHub Actions will automatically deploy to Azure

3. Monitor deployment:
   - https://github.com/sikdars25/qadam/actions

## Step 7: Verify Deployment

1. Check health endpoint:
```bash
curl https://qadam-ai.azurewebsites.net/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Service",
  "features": {
    "groq_api": true,
    "tfidf_vectorizer": true
  }
}
```

2. Test solve-question endpoint:
```bash
curl -X POST https://qadam-ai.azurewebsites.net/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is 2 + 2?",
    "subject": "Mathematics"
  }'
```

## Troubleshooting

### Issue: "Groq API not initialized"
**Solution**: Make sure `GROQ_API_KEY` is set in Application Settings

### Issue: 404 errors
**Solution**: Wait 2-3 minutes after deployment for functions to warm up

### Issue: Deployment fails
**Solution**: 
1. Check GitHub Actions logs
2. Verify publish profile is correct
3. Ensure Function App exists in Azure

## Monitoring

View logs in Azure Portal:
1. Go to `qadam-ai` Function App
2. Click "Log stream" in the left menu
3. Watch real-time logs

## Cost Estimate

With Azure Consumption plan:
- **First 1 million executions**: FREE
- **Additional executions**: $0.20 per million
- **Memory**: $0.000016/GB-s

Expected monthly cost: **$0** (within free tier)

## Support

For issues, check:
- GitHub Actions logs: https://github.com/sikdars25/qadam/actions
- Azure Function logs: Portal → qadam-ai → Log stream
- Groq API status: https://status.groq.com
