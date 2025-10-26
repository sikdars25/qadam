# ✅ Azure Deployment Setup Checklist

## 🎯 Quick Setup Guide

Follow these steps to connect your Azure Static Web App (frontend) with Azure Function App (backend).

---

## 📋 Step 1: Get Your Azure URLs

### ✅ Backend URL (Function App)
1. Go to: https://portal.azure.com
2. Navigate to: **Function Apps** → Your function app
3. Copy the URL (example):
   ```
   https://qadam-backend.azurewebsites.net
   ```
4. **Save this URL** - you'll need it multiple times

### ✅ Frontend URL (Static Web App)
1. Go to: https://portal.azure.com
2. Navigate to: **Static Web Apps** → Your static web app
3. Copy the URL (example):
   ```
   https://happy-ocean-12345.azurestaticapps.net
   ```
4. **Save this URL** - you'll need it for CORS

---

## 🔧 Step 2: Configure Backend (Function App)

### A. Set Environment Variables

1. **Go to Function App** → Configuration → Application settings
2. **Click "+ New application setting"**
3. **Add these settings:**

| Name | Value | Example |
|------|-------|---------|
| `FRONTEND_URL` | Your Static Web App URL | `https://happy-ocean-12345.azurestaticapps.net` |
| `SECRET_KEY` | Random secure string | `your-random-secret-key-123` |
| `GROQ_API_KEY` | Your Groq API key | `gsk_...` |
| `SMTP_SERVER` | Gmail SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | Your email | `your-email@gmail.com` |
| `SMTP_PASSWORD` | Gmail app password | `your-app-password` |

4. **Click "Save"**
5. **Restart** the Function App

### B. Configure CORS

1. **Go to Function App** → API → CORS
2. **Add Allowed Origins:**
   ```
   https://happy-ocean-12345.azurestaticapps.net
   ```
   (Replace with YOUR Static Web App URL)

3. **Also add for local development:**
   ```
   http://localhost:3000
   ```

4. **Enable:**
   - ✅ "Enable Access-Control-Allow-Credentials"

5. **Click "Save"**

---

## 🌐 Step 3: Configure Frontend (Static Web App)

### A. Update .env.production File

1. **Open:** `frontend/.env.production`
2. **Replace the URL** with your actual Function App URL:
   ```bash
   REACT_APP_API_URL=https://qadam-backend.azurewebsites.net
   ```
   (Replace `qadam-backend` with YOUR Function App name)

3. **Save the file**

### B. Set Environment Variables in Azure

1. **Go to Static Web App** → Configuration
2. **Click "+ Add"** under Application settings
3. **Add these settings:**

| Name | Value |
|------|-------|
| `REACT_APP_API_URL` | `https://qadam-backend.azurewebsites.net` |
| `REACT_APP_ENV` | `production` |

4. **Click "Save"**

### C. Redeploy Frontend

**Option 1: Automatic (GitHub)**
- Push changes to your GitHub repository
- Static Web App will auto-deploy

**Option 2: Manual**
```bash
cd frontend
npm run build
# Upload build folder to Azure
```

---

## 🧪 Step 4: Test the Connection

### Test 1: Backend Health Check

Open in browser:
```
https://qadam-backend.azurewebsites.net/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Backend is running"
}
```

✅ If you see this, backend is working!

### Test 2: Frontend Connection

1. **Open your Static Web App:**
   ```
   https://happy-ocean-12345.azurestaticapps.net
   ```

2. **Open Browser Console** (F12)

3. **Look for:**
   ```
   🌐 API URL: https://qadam-backend.azurewebsites.net
   🔧 Environment: production
   ```

4. **Try to load papers/questions**
   - Should fetch data from backend
   - No CORS errors in console

✅ If data loads, connection is working!

---

## 🔍 Troubleshooting

### ❌ Problem: CORS Error

**Error in console:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solutions:**
1. ✅ Check CORS settings in Function App
2. ✅ Verify Static Web App URL is in allowed origins
3. ✅ Ensure no typos (https vs http)
4. ✅ Restart Function App after CORS changes
5. ✅ Clear browser cache

### ❌ Problem: 404 Not Found

**Error:**
```
GET https://qadam-backend.azurewebsites.net/api/papers 404
```

**Solutions:**
1. ✅ Verify Function App is deployed
2. ✅ Check if Function App is running (not stopped)
3. ✅ Review deployment logs in Azure Portal
4. ✅ Test health endpoint first

### ❌ Problem: Environment Variables Not Working

**Error:**
```
process.env.REACT_APP_API_URL is undefined
```

**Solutions:**
1. ✅ Ensure variable starts with `REACT_APP_`
2. ✅ Rebuild Static Web App after adding variables
3. ✅ Check Configuration in Azure Portal
4. ✅ Clear browser cache and hard refresh (Ctrl+Shift+R)

### ❌ Problem: 500 Internal Server Error

**Error:**
```
GET https://qadam-backend.azurewebsites.net/api/papers 500
```

**Solutions:**
1. ✅ Check Function App logs in Azure Portal
2. ✅ Verify database connection settings
3. ✅ Ensure all required environment variables are set
4. ✅ Check for missing dependencies

---

## 📝 Complete Checklist

### Backend (Function App)
- [ ] Function App deployed to Azure
- [ ] `FRONTEND_URL` environment variable set
- [ ] `GROQ_API_KEY` environment variable set
- [ ] `SMTP_*` environment variables set (if using email)
- [ ] CORS configured with Static Web App URL
- [ ] CORS allows credentials enabled
- [ ] Function App is running (not stopped)
- [ ] Health check endpoint works
- [ ] No errors in Application Insights logs

### Frontend (Static Web App)
- [ ] `.env.production` updated with Function App URL
- [ ] `REACT_APP_API_URL` set in Azure configuration
- [ ] Static Web App redeployed after changes
- [ ] No CORS errors in browser console
- [ ] API calls use `process.env.REACT_APP_API_URL`
- [ ] Data loads successfully from backend

### Testing
- [ ] Backend health check returns 200 OK
- [ ] Frontend can fetch papers/questions
- [ ] File uploads work
- [ ] Authentication works (if implemented)
- [ ] All features tested in production

---

## 🎯 Your Configuration

**Fill this out with your actual values:**

```
Backend URL: https://_____________________.azurewebsites.net
Frontend URL: https://_____________________.azurestaticapps.net

Environment Variables Set:
[ ] FRONTEND_URL
[ ] REACT_APP_API_URL
[ ] GROQ_API_KEY
[ ] SMTP_SERVER
[ ] SMTP_USER
[ ] SMTP_PASSWORD

CORS Configured: [ ] Yes [ ] No
Health Check Working: [ ] Yes [ ] No
Frontend Connected: [ ] Yes [ ] No
```

---

## 🚀 Next Steps After Connection

1. **Set up custom domain** (optional)
2. **Enable Application Insights** for monitoring
3. **Set up alerts** for errors
4. **Configure auto-scaling** for Function App
5. **Set up CI/CD** with GitHub Actions
6. **Add SSL certificate** (automatic with Azure)

---

## 📞 Need Help?

### Check Logs
- **Function App:** Azure Portal → Function App → Log Stream
- **Static Web App:** Azure Portal → Static Web App → Deployment History
- **Browser:** F12 → Console tab

### Common Issues
- CORS errors → Check CORS configuration
- 404 errors → Check deployment status
- 500 errors → Check application logs
- Connection timeout → Check Function App is running

### Resources
- [Azure Static Web Apps Docs](https://docs.microsoft.com/azure/static-web-apps/)
- [Azure Functions Docs](https://docs.microsoft.com/azure/azure-functions/)
- [CORS Configuration](https://docs.microsoft.com/azure/app-service/app-service-web-tutorial-rest-api)

---

**Good luck with your deployment!** 🎉
