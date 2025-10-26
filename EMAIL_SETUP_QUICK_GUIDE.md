# Gmail Email Setup - Quick Guide

## 🚀 5-Minute Setup

### Step 1: Enable 2-Step Verification

1. Go to: **https://myaccount.google.com/security**
2. Click **"2-Step Verification"**
3. Click **"Get Started"** or **"Turn On"**
4. Enter your phone number
5. Verify with code
6. Complete setup

### Step 2: Generate App Password

1. Go to: **https://myaccount.google.com/apppasswords**
2. Select app: **"Mail"**
3. Select device: **"Other (Custom name)"**
4. Enter: `QAdam Academic Portal`
5. Click **"Generate"**
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
7. Remove spaces: `abcdefghijklmnop`

### Step 3: Update .env File

Edit `backend/.env`:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

**Replace with your actual Gmail and app password!**

### Step 4: Restart Backend

```bash
start-backend.bat
```

### Step 5: Test

1. Register with any email
2. Check inbox for activation email
3. Click activation link
4. Login successfully

---

## ✅ Success Indicators

**Backend console shows:**
```
✅ Activation email sent to user@example.com via Gmail SMTP
```

**User receives:**
- Professional HTML email
- Purple gradient design
- Large "Activate My Account" button
- Activation link

---

## ❌ Common Errors

### "Authentication failed"
- ❌ Using regular password instead of app password
- ✅ Generate app password and use that

### "Username and Password not accepted"
- ❌ App password has spaces
- ✅ Remove all spaces from app password

### "2-Step Verification required"
- ❌ 2FA not enabled
- ✅ Enable 2-Step Verification first

---

## 📧 Email Configuration

```bash
# Gmail SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

**Important:**
- Use Gmail address (not Yahoo, Outlook, etc.)
- Use App Password (not regular password)
- Remove spaces from app password
- Restart backend after changes

---

## 🎯 Quick Links

- **Enable 2FA:** https://myaccount.google.com/security
- **Generate App Password:** https://myaccount.google.com/apppasswords
- **Full Guide:** See `GMAIL_EMAIL_SETUP.md`

---

## ✨ Benefits

- ✅ Free forever (500 emails/day)
- ✅ Excellent delivery rate
- ✅ Rarely hits spam
- ✅ Trusted by recipients
- ✅ Simple setup
- ✅ No API key needed

---

**That's it! Your email system is ready.** 🎉
