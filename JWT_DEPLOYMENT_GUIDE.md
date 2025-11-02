# JWT Authentication Deployment Guide

## ✅ What Was Implemented

**JWT (JSON Web Token) authentication** to fix cross-origin session cookie issues.

### Backend Changes:
- ✅ JWT library (`PyJWT`) added
- ✅ Login endpoint returns JWT token
- ✅ Protected endpoints accept JWT tokens
- ✅ Session authentication still works (backward compatible)

### Frontend Changes:
- ✅ JWT token stored in localStorage on login
- ✅ Token automatically sent in Authorization header
- ✅ Axios interceptor handles 401 errors
- ✅ Token cleared on logout

## 🚀 Deployment Steps

### Step 1: Deploy Backend (VM)

```bash
# SSH to VM
ssh qadamuser@130.107.48.166

# Pull latest code
cd /opt/qadam-backend
git pull origin backend-proxy

# Run JWT implementation script
cd proxy
chmod +x implement_jwt_backend.sh
./implement_jwt_backend.sh
```

**This will:**
1. Install PyJWT library
2. Update app.py to generate and validate JWT tokens
3. Restart backend service

### Step 2: Deploy Frontend (Automatic)

Frontend is already pushed to `main` branch. GitHub Actions will automatically:
1. Build frontend with JWT support
2. Deploy to Azure Static Web Apps
3. Takes ~2-3 minutes

**Monitor:** https://github.com/sikdars25/qadam/actions

### Step 3: Test

1. **Clear browser data:**
   - Press `F12` → Application → Clear storage
   - Or use Incognito/Private mode

2. **Login:**
   - Go to: https://zealous-ocean-06e22b51e.3.azurestaticapps.net
   - Login with credentials
   - Check console: Should see "🔑 JWT token stored"

3. **Test authenticated request:**
   - Try deleting a paper
   - Should work without 401 errors!

4. **Verify token in DevTools:**
   - Application → Local Storage
   - Should see `auth_token` with JWT value

## 🔍 How It Works

### Login Flow:
```
1. User enters credentials
2. Backend validates and generates JWT token
3. Frontend stores token in localStorage
4. Frontend stores user data
```

### Authenticated Request Flow:
```
1. Frontend gets token from localStorage
2. Axios interceptor adds: Authorization: Bearer <token>
3. Backend validates token
4. Request proceeds if valid
```

### Token Structure:
```json
{
  "user_id": "9ac28353-71fc-4a1f-95b6-42c266a58602",
  "username": "student1",
  "role": "student",
  "exp": 1730635200,  // Expiration (24 hours)
  "iat": 1730548800   // Issued at
}
```

## 🧪 Testing Commands

### Test Login (Backend):
```bash
curl -X POST https://130.107.48.166/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"student123"}'
```

**Expected Response:**
```json
{
  "message": "Login successful",
  "user": {...},
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Test Authenticated Request:
```bash
TOKEN="<your-token-here>"

curl -X DELETE https://130.107.48.166/api/delete-paper/some-id \
  -H "Authorization: Bearer $TOKEN"
```

## 🐛 Troubleshooting

### Issue: Still getting 401 errors

**Solution:**
1. Clear browser localStorage
2. Logout and login again
3. Check console for "🔑 JWT token stored"

### Issue: Token not being sent

**Solution:**
1. Check Network tab → Request Headers
2. Should see: `Authorization: Bearer eyJ...`
3. If missing, check `getToken()` function

### Issue: Backend not generating token

**Solution:**
```bash
# Check backend logs
sudo journalctl -u qadam-backend -f

# Should see: "🔑 Generated JWT token for user: ..."
```

### Issue: Token expired

**Solution:**
- Tokens expire after 24 hours
- Login again to get new token
- Frontend auto-redirects to login on 401

## 📊 Verification Checklist

- [ ] Backend script ran successfully
- [ ] Frontend deployed (green checkmark on GitHub Actions)
- [ ] Can login successfully
- [ ] Token stored in localStorage
- [ ] Can delete papers without 401 errors
- [ ] Token sent in Authorization header
- [ ] Backend logs show JWT authentication

## 🎯 Benefits

✅ **Works across any domains** - no cookie restrictions
✅ **Industry standard** - JWT is widely used
✅ **Stateless** - no server-side session storage needed
✅ **Backward compatible** - session auth still works
✅ **Secure** - tokens are signed and validated

## 📝 Next Steps

After successful deployment:

1. **Test all features:**
   - Upload papers
   - Delete papers
   - Upload textbooks
   - Parse questions

2. **Monitor logs:**
   ```bash
   sudo journalctl -u qadam-backend -f
   ```

3. **Optional: Increase token expiration:**
   Edit `jwt_auth.py`:
   ```python
   JWT_EXPIRATION_HOURS = 168  # 7 days
   ```

---

**JWT authentication is now live! No more cross-origin cookie issues!** 🎉
