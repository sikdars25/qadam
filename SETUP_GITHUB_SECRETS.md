# Setting Up GitHub Secrets for GROQ_API_KEY

## 🔐 Why Use GitHub Secrets?

**Security Best Practice:**
- ✅ API keys never exposed in code
- ✅ Not visible in commit history
- ✅ Encrypted by GitHub
- ✅ Only accessible during deployment
- ✅ Can be rotated without code changes

**❌ NEVER hardcode API keys in code!**

---

## 📋 Setup Instructions

### Step 1: Get Your GROQ API Key

1. Go to https://console.groq.com/
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key or copy existing one
5. **Save it securely** - you'll need it for the next step

---

### Step 2: Add Secret to GitHub Repository

1. **Go to your GitHub repository:**
   ```
   https://github.com/sikdars25/qadam
   ```

2. **Navigate to Settings:**
   - Click on "Settings" tab (top right)

3. **Go to Secrets and Variables:**
   - In left sidebar, click "Secrets and variables"
   - Click "Actions"

4. **Add New Secret:**
   - Click "New repository secret" button
   - **Name:** `GROQ_API_KEY`
   - **Value:** Paste your Groq API key
   - Click "Add secret"

---

### Step 3: Verify Secret is Set

1. Go to repository Settings → Secrets and variables → Actions
2. You should see `GROQ_API_KEY` in the list
3. The value will be hidden (shows as `***`)

---

## 🔄 How It Works

### During GitHub Actions Deployment:

1. **Build Phase:**
   - Code is checked out
   - Dependencies installed
   - Package created

2. **Deploy Phase:**
   - Login to Azure
   - Deploy package to Azure Functions
   - **Configure App Settings** ← GROQ_API_KEY is set here
   - Configure CORS

3. **App Settings Configuration:**
   ```yaml
   - name: 'Configure App Settings'
     run: |
       az functionapp config appsettings set \
         --name qadam-backend \
         --resource-group qadam_bend_group \
         --settings \
           GROQ_API_KEY="${{ secrets.GROQ_API_KEY }}"
   ```

4. **Backend Reads from Environment:**
   ```python
   # In backend/ai_helpers.py
   groq_api_key = os.getenv('GROQ_API_KEY')
   groq_client = Groq(api_key=groq_api_key)
   ```

---

## ✅ Benefits of This Approach

### Security:
- ✅ API key never in code
- ✅ Not in git history
- ✅ Encrypted at rest
- ✅ Only accessible during deployment

### Flexibility:
- ✅ Can update key without code changes
- ✅ Different keys for different environments
- ✅ Easy to rotate keys

### Compliance:
- ✅ Follows security best practices
- ✅ No secrets in version control
- ✅ Audit trail in GitHub

---

## 🔍 Verification

### After Setting Up Secret:

1. **Trigger a deployment:**
   ```bash
   git commit --allow-empty -m "test: verify GROQ_API_KEY setup"
   git push origin main
   ```

2. **Check GitHub Actions:**
   - Go to Actions tab
   - Watch the deployment
   - Look for "Configure App Settings" step
   - Should show: "App settings configured successfully"

3. **Check Backend Logs:**
   ```bash
   az webapp log tail --name qadam-backend --resource-group qadam_bend_group
   ```
   
   **Look for:**
   ```
   ✅ Groq API initialized
   ```

4. **Test Question Solving:**
   - Upload a question
   - Should get real solution (not error)

---

## 🔧 Troubleshooting

### Issue 1: Secret Not Found

**Symptom:**
```
Error: Secret GROQ_API_KEY not found
```

**Solution:**
1. Verify secret name is exactly `GROQ_API_KEY` (case-sensitive)
2. Check it's in repository secrets (not environment secrets)
3. Re-add the secret if needed

### Issue 2: Still Shows "API Not Initialized"

**Possible Causes:**
1. Secret not set in GitHub
2. Deployment didn't run "Configure App Settings" step
3. API key is invalid

**Solution:**
1. Check GitHub Actions logs for "Configure App Settings" step
2. Verify secret is set correctly
3. Test API key directly at https://console.groq.com/

### Issue 3: Deployment Fails at App Settings Step

**Symptom:**
```
Error: Failed to configure app settings
```

**Solution:**
1. Check Azure credentials are valid
2. Verify function app name and resource group
3. Check Azure CLI is authenticated in workflow

---

## 📝 Current Configuration

### GitHub Workflow File:
`.github/workflows/main_qadam-backend.yml`

### Relevant Section:
```yaml
- name: 'Configure App Settings'
  run: |
    echo "Configuring App Settings..."
    az functionapp config appsettings set \
      --name qadam-backend \
      --resource-group qadam_bend_group \
      --settings \
        GROQ_API_KEY="${{ secrets.GROQ_API_KEY }}" \
        CORS_CREDENTIALS=true
    echo "App settings configured successfully"
```

### Backend Code:
```python
# backend/ai_helpers.py
import os
from groq import Groq

groq_api_key = os.getenv('GROQ_API_KEY')
if groq_api_key:
    groq_client = Groq(api_key=groq_api_key)
    print("✅ Groq API initialized")
else:
    print("⚠️ GROQ_API_KEY not found")
    groq_client = None
```

---

## 🎯 Next Steps

### 1. Add the Secret (If Not Already Done):
- Go to GitHub repository settings
- Add `GROQ_API_KEY` secret
- Use your Groq API key as the value

### 2. Trigger Deployment:
- Make any small change to backend code
- Commit and push
- GitHub Actions will deploy with the secret

### 3. Verify:
- Check GitHub Actions logs
- Check backend logs for "✅ Groq API initialized"
- Test question solving

---

## 🔐 Security Reminders

### DO:
- ✅ Use GitHub secrets for API keys
- ✅ Rotate keys periodically
- ✅ Use different keys for dev/prod
- ✅ Monitor API usage

### DON'T:
- ❌ Hardcode API keys in code
- ❌ Commit `.env` files with real keys
- ❌ Share API keys in chat/email
- ❌ Use same key across multiple projects

---

## 📞 Support

### If You Need Help:

1. **Check GitHub Actions logs:**
   ```
   https://github.com/sikdars25/qadam/actions
   ```

2. **Check Azure logs:**
   ```bash
   az webapp log tail --name qadam-backend --resource-group qadam_bend_group
   ```

3. **Verify secret is set:**
   - GitHub → Settings → Secrets and variables → Actions
   - Should see `GROQ_API_KEY` in the list

---

**Last Updated:** October 31, 2025 8:10 PM IST  
**Status:** Ready to configure  
**Next Action:** Add GROQ_API_KEY to GitHub secrets
