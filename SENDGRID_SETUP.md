# SendGrid Email Setup Guide

## 📧 SendGrid Integration for Account Activation

QAdam now uses SendGrid for reliable email delivery. SendGrid offers a free tier with 100 emails/day.

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Create SendGrid Account

1. Go to [https://sendgrid.com](https://sendgrid.com)
2. Click "Start for Free"
3. Sign up with your email
4. Verify your email address

### Step 2: Get API Key

1. Log in to SendGrid Dashboard
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name: `QAdam Academic Portal`
5. Permissions: **Full Access** (or at least Mail Send)
6. Click **Create & View**
7. **Copy the API key** (you won't see it again!)

### Step 3: Verify Sender Identity

**Option A: Single Sender Verification (Quick)**
1. Go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in your details:
   - From Name: `QAdam Academic Portal`
   - From Email: Your email (e.g., `your-email@gmail.com`)
   - Reply To: Same email
   - Company: `QAdam`
   - Address: Your address
4. Click **Create**
5. Check your email and verify

**Option B: Domain Authentication (Professional)**
- Requires DNS access to your domain
- Better for production
- Follow SendGrid's domain authentication wizard

### Step 4: Configure Backend

Edit `backend/.env`:

```bash
# SendGrid Configuration
SENDGRID_API_KEY=SG.your_actual_api_key_here
SENDGRID_FROM_EMAIL=your-verified-email@gmail.com
SENDGRID_FROM_NAME=QAdam Academic Portal
```

**Important:** 
- `SENDGRID_FROM_EMAIL` must match your verified sender email
- Don't share your API key publicly

### Step 5: Install SendGrid Package

```bash
cd backend
pip install sendgrid
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### Step 6: Restart Backend

```bash
start-backend.bat
```

---

## ✅ Test Registration

1. Go to register page
2. Fill in all fields with a real email
3. Click "Register"
4. Check your email inbox (and spam folder)
5. Click activation link
6. Login with your credentials

---

## 📊 SendGrid Free Tier

**Limits:**
- ✅ 100 emails/day forever
- ✅ No credit card required
- ✅ Professional email templates
- ✅ Delivery analytics
- ✅ Email validation

**Perfect for:**
- Development
- Testing
- Small schools (up to 100 registrations/day)

---

## 🎨 Email Template Preview

**Subject:** 🎓 Activate Your QAdam Account

**Design:**
- Purple gradient header with QAdam logo
- Personalized greeting
- Large "Activate My Account" button
- Fallback activation link
- Security note
- Professional footer
- Mobile responsive

---

## 🔧 Troubleshooting

### Email Not Received

**Check 1: Spam Folder**
- SendGrid emails might go to spam initially
- Mark as "Not Spam" to train filters

**Check 2: Sender Verification**
```bash
# Backend console should show:
✅ Activation email sent to user@example.com via SendGrid
```

If you see:
```bash
⚠️  SendGrid not configured. Set SENDGRID_API_KEY in .env
📧 Activation link for user@example.com:
   http://localhost:3000/activate?token=...
```
Then SendGrid is not configured. Check your .env file.

**Check 3: API Key**
- Make sure API key is correct
- No extra spaces in .env file
- API key starts with `SG.`

**Check 4: From Email**
- Must match verified sender in SendGrid
- Check SendGrid dashboard for verification status

### SendGrid Error Messages

**"The from email does not match a verified Sender Identity"**
- Solution: Verify your sender email in SendGrid dashboard
- Go to Settings → Sender Authentication

**"Invalid API Key"**
- Solution: Generate new API key
- Update .env file
- Restart backend

**"Rate limit exceeded"**
- Solution: You've sent 100 emails today
- Wait 24 hours or upgrade plan

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   - Already in .gitignore
   - API key is secret

2. **Use environment variables**
   - Don't hardcode API key in code
   - Use os.getenv()

3. **Rotate API keys**
   - Generate new key every few months
   - Delete old keys in SendGrid

4. **Monitor usage**
   - Check SendGrid dashboard
   - Set up alerts for unusual activity

---

## 📈 Production Deployment

### For Production Server:

1. **Domain Authentication**
   - Authenticate your domain in SendGrid
   - Better deliverability
   - Professional appearance

2. **Update Activation Link**
   - Change from `localhost:3000` to your domain
   - Edit in `app.py` line 462

3. **Environment Variables**
   - Set in production server
   - Don't use .env file in production
   - Use server's environment variable system

4. **Monitoring**
   - Enable SendGrid webhooks
   - Track bounces and spam reports
   - Monitor delivery rates

---

## 💡 Tips

**Testing:**
- Use your own email for testing
- Check spam folder first time
- Verify sender before bulk testing

**Development:**
- Without SendGrid: Activation link shows on screen
- With SendGrid: Professional email sent
- Both methods work!

**Customization:**
- Edit email template in `app.py`
- Change colors, text, branding
- Add school logo (requires image hosting)

---

## 📞 Support

**SendGrid Issues:**
- SendGrid Support: https://support.sendgrid.com
- Documentation: https://docs.sendgrid.com

**QAdam Issues:**
- Check backend console for errors
- Activation link always shows in console as fallback

---

## ✨ Summary

**Setup Steps:**
1. ✅ Create SendGrid account (free)
2. ✅ Get API key
3. ✅ Verify sender email
4. ✅ Configure .env file
5. ✅ Install sendgrid package
6. ✅ Restart backend
7. ✅ Test registration

**Result:**
- Professional activation emails
- Reliable delivery
- Beautiful HTML template
- Free forever (100/day)

**Your registration system is now production-ready!** 🎉
