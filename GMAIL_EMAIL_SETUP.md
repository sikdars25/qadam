# Gmail Email Setup Guide

## 📧 Gmail SMTP Configuration for Account Activation

QAdam uses Gmail SMTP for sending activation emails. Gmail is reliable, free, and easy to set up.

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Enable 2-Step Verification

**Important:** Gmail requires 2-Step Verification before you can generate App Passwords.

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Sign in to your Gmail account
3. Click on **"2-Step Verification"**
4. Click **"Get Started"** or **"Turn On"**
5. Enter your phone number
6. Verify with the code sent to your phone
7. Complete the setup

### Step 2: Generate Gmail App Password

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Or: Google Account → Security → 2-Step Verification → App passwords
2. In **"Select app"** dropdown: Choose **"Mail"**
3. In **"Select device"** dropdown: Choose **"Other (Custom name)"**
4. Enter name: `QAdam Academic Portal`
5. Click **"Generate"**
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
7. Remove spaces: `abcdefghijklmnop`

### Step 3: Configure Backend

Edit `backend/.env`:

```bash
# Gmail Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

**Replace with your actual Gmail and app password!**

### Step 3: Restart Backend

```bash
start-backend.bat
```

---

## ✅ Test Registration

1. Go to register page
2. Fill in all fields with a real email
3. Click "Register"
4. Check your email inbox
5. Click activation link
6. Login with your credentials

---

## 📊 Gmail SMTP Details

**Server:** smtp.gmail.com  
**Port:** 587  
**Security:** STARTTLS  
**Authentication:** Required  

**Limits:**
- ✅ Free forever
- ✅ 500 emails/day
- ✅ Excellent delivery rate
- ✅ No API key needed
- ✅ Trusted by recipients

---

## 🎨 Email Template

**Subject:** 🎓 Activate Your QAdam Account

**From:** QAdam Academic Portal <your_email@gmail.com>

**Design:**
- Purple gradient header
- Personalized greeting
- Large activation button
- Fallback link
- Security note
- Professional footer
- Mobile responsive

---

## 🔧 Troubleshooting

### Error: "Authentication failed"

**Solution 1: Use App Password (Required)**
- Don't use your regular Gmail password
- Generate App Password in Google Account Security
- Use the 16-character app password (no spaces)

**Solution 2: Enable 2-Step Verification**
- Gmail requires 2FA to generate app passwords
- Go to Google Account Security
- Enable 2-Step Verification first
- Then generate app password

### Error: "Connection refused"

**Check:**
- SMTP_SERVER: `smtp.gmail.com`
- SMTP_PORT: `587`
- Internet connection
- Firewall not blocking port 587

### Error: "Username and Password not accepted"

**Common causes:**
- Using regular password instead of app password
- App password has spaces (remove them)
- 2-Step Verification not enabled
- Wrong Gmail address

**Solution:**
1. Enable 2-Step Verification
2. Generate new app password
3. Copy without spaces
4. Update .env file
5. Restart backend

### Email Not Received

**Check 1:** Spam folder (Gmail emails rarely go to spam)
**Check 2:** Backend console for errors
**Check 3:** Gmail account is active
**Check 4:** App password is correct (16 characters, no spaces)

### Backend Console Shows:

**Success:**
```bash
✅ Activation email sent to user@example.com via Gmail SMTP
```

**Error:**
```bash
❌ Email error: [error message]
📧 Activation link for user@example.com:
   http://localhost:3000/activate?token=...
```

---

## 🔐 Security Best Practices

1. **Never commit .env file**
   - Already in .gitignore
   - App password is secret

2. **Use App Password**
   - Never use regular password
   - Generate new app password for each app

3. **Rotate passwords**
   - Revoke old app passwords
   - Generate new ones periodically

4. **Monitor usage**
   - Check Yahoo sent folder
   - Watch for unusual activity

---

## 📈 Production Deployment

### For Production Server:

1. **Update Activation Link**
   - Change from `localhost:3000` to your domain
   - Edit in `app.py` line 463

2. **Environment Variables**
   - Set in production server
   - Don't use .env file in production
   - Use server's environment variable system

3. **Monitoring**
   - Track email delivery
   - Monitor bounce rates
   - Check spam reports

---

## 💡 Tips

**Testing:**
- Use your own email for testing
- Check spam folder first time
- App password works immediately

**Development:**
- Without SMTP: Activation link shows on screen
- With SMTP: Professional email sent
- Both methods work!

**Customization:**
- Edit email template in `app.py`
- Change colors, text, branding
- Add school logo (requires image hosting)

---

## 🆚 Gmail vs SendGrid

**Gmail SMTP:**
- ✅ Free forever
- ✅ No API key needed
- ✅ Simple setup
- ✅ 500 emails/day
- ✅ Excellent deliverability
- ✅ Trusted by recipients
- ✅ Rarely hits spam

**SendGrid:**
- ✅ Better analytics dashboard
- ✅ Webhook support
- ✅ 100 emails/day free
- ⚠️ Requires API key
- ⚠️ Sender verification needed
- ⚠️ More complex setup

---

## ✨ Summary

**Setup Steps:**
1. ✅ Enable 2-Step Verification on Gmail
2. ✅ Generate Gmail App Password
3. ✅ Configure .env file
4. ✅ Restart backend
5. ✅ Test registration

**Configuration:**
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

**Result:**
- Professional activation emails
- Excellent delivery rate
- Beautiful HTML template
- Free forever (500 emails/day)
- Trusted by recipients

**Your registration system is now ready with Gmail!** 🎉
