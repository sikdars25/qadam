# Admin User Management Setup

## 🎯 Overview

Admin user management system that allows administrators to:
- ✅ View all registered users
- ✅ Activate/Deactivate user accounts
- ✅ Delete user accounts
- ✅ View user statistics
- ✅ Access admin-only dashboard

---

## 🚀 Setup Steps

### Step 1: Add is_admin Column & Create Admin User

Run the admin creation script:

```bash
cd backend
python create_admin.py
```

**Expected Output:**
```
==================================================
Creating Admin User
==================================================

✓ Added is_admin column to users table
✓ Created new admin user: admin

Current users table schema:
  - id (INTEGER)
  - username (TEXT)
  - password (TEXT)
  - full_name (TEXT)
  - created_at (TIMESTAMP)
  - phone (TEXT)
  - email (TEXT)
  - is_active (BOOLEAN)
  - is_admin (BOOLEAN)
  - activation_token (TEXT)

==================================================
Admin User Created!
==================================================

Admin Login Credentials:
  Email: sikdar.moving@gmail.com
  Username: admin
  Password: admin123

⚠️  IMPORTANT: Change the admin password after first login!
```

### Step 2: Restart Backend

```bash
cd ..
start-backend.bat
```

### Step 3: Login as Admin

1. Go to login page: http://localhost:3000/login
2. Enter credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
3. Click "Login"
4. You'll be redirected to Admin Dashboard

---

## 👨‍💼 Admin Dashboard Features

### **Dashboard Overview:**

**Statistics Cards:**
- 👥 Total Users
- ✅ Active Users
- ⏸️ Inactive Users
- 👨‍💼 Admins

**Users Table:**
- View all registered users
- See user details (username, email, phone, status, role)
- See registration date
- Manage user accounts

### **User Management Actions:**

**1. Activate/Deactivate Users:**
- Click ▶️ to activate inactive user
- Click ⏸️ to deactivate active user
- Deactivated users cannot login

**2. Delete Users:**
- Click 🗑️ to delete user account
- Confirmation prompt before deletion
- Admin accounts cannot be deleted (protected)

**3. View User Details:**
- Username, Full Name
- Email, Phone
- Active/Inactive status
- Admin/User role
- Registration date

---

## 🔐 Admin Credentials

**Default Admin Account:**
- **Email:** sikdar.moving@gmail.com
- **Username:** admin
- **Password:** admin123

**⚠️ IMPORTANT:**
- Change the password after first login
- Keep admin credentials secure
- Don't share admin access

---

## 🎨 Admin Dashboard UI

**Header:**
- 👨‍💼 Admin Dashboard title
- ADMIN badge
- Admin name display
- Logout button

**Statistics Section:**
- 4 stat cards with icons
- Real-time user counts
- Color-coded information

**Users Table:**
- Sortable columns
- Status badges (Active/Inactive)
- Role badges (Admin/User)
- Action buttons
- Hover effects
- Responsive design

---

## 🔧 API Endpoints

### **Get All Users**
```
GET /api/admin/users
```

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": 1,
      "username": "admin",
      "full_name": "System Administrator",
      "email": "sikdar.moving@gmail.com",
      "phone": null,
      "is_active": true,
      "is_admin": true,
      "created_at": "2025-10-24 00:00:00"
    }
  ]
}
```

### **Toggle User Active Status**
```
POST /api/admin/users/:id/toggle-active
```

**Response:**
```json
{
  "success": true,
  "message": "User activated successfully",
  "is_active": true
}
```

### **Delete User**
```
DELETE /api/admin/users/:id
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## 🛡️ Security Features

**Admin Protection:**
- Admin accounts cannot be deleted
- Admin accounts cannot be deactivated
- Only admins can access admin dashboard
- Non-admin users redirected to regular dashboard

**User Protection:**
- Confirmation prompt before deletion
- Cannot delete yourself
- Deactivated users cannot login

**Route Protection:**
- `/admin` route only accessible to admins
- `/dashboard` route only accessible to regular users
- Automatic redirection based on role

---

## 📊 User Flow

### **Admin Login Flow:**
```
1. Admin enters credentials
   ↓
2. Backend checks is_admin = true
   ↓
3. Frontend receives is_admin: true
   ↓
4. Redirects to /admin
   ↓
5. Admin Dashboard loads
   ↓
6. Fetches all users
   ↓
7. Displays user management interface
```

### **Regular User Login Flow:**
```
1. User enters credentials
   ↓
2. Backend checks is_admin = false
   ↓
3. Frontend receives is_admin: false
   ↓
4. Redirects to /dashboard
   ↓
5. Regular Dashboard loads
   ↓
6. User sees question bank, etc.
```

---

## 🎯 Usage Examples

### **Activate a User:**
1. Find user in table
2. Click ▶️ button
3. User status changes to "✅ Active"
4. User can now login

### **Deactivate a User:**
1. Find user in table
2. Click ⏸️ button
3. User status changes to "⏸️ Inactive"
4. User cannot login anymore

### **Delete a User:**
1. Find user in table
2. Click 🗑️ button
3. Confirm deletion
4. User removed from database

---

## 🔍 Troubleshooting

### **Admin Login Not Working:**

**Check 1:** Run create_admin.py
```bash
cd backend
python create_admin.py
```

**Check 2:** Verify database has is_admin column
```bash
sqlite3 qadam.db
.schema users
```

**Check 3:** Check admin exists
```sql
SELECT * FROM users WHERE is_admin = 1;
```

### **Admin Dashboard Not Loading:**

**Check 1:** Backend running
**Check 2:** Check browser console for errors
**Check 3:** Verify API endpoint responds
```bash
curl http://localhost:5000/api/admin/users
```

### **Cannot Delete User:**

**Reason 1:** Trying to delete admin account (protected)
**Reason 2:** User doesn't exist
**Reason 3:** Database error

---

## 📱 Responsive Design

**Desktop:**
- Full table view
- 4 stat cards in row
- All columns visible

**Tablet:**
- Scrollable table
- 2 stat cards per row
- Compact view

**Mobile:**
- Horizontal scroll table
- 1 stat card per row
- Touch-friendly buttons

---

## ✨ Features Summary

**Admin Dashboard:**
- ✅ View all users
- ✅ Real-time statistics
- ✅ Activate/Deactivate users
- ✅ Delete user accounts
- ✅ Protected admin accounts
- ✅ Responsive design
- ✅ Beautiful UI with gradients
- ✅ Confirmation prompts
- ✅ Success/Error messages
- ✅ Hover effects
- ✅ Role badges
- ✅ Status badges

**Security:**
- ✅ Role-based access control
- ✅ Admin-only routes
- ✅ Protected admin accounts
- ✅ Confirmation before deletion
- ✅ Session management

---

## 🎉 Complete Setup Checklist

- [ ] Run `python create_admin.py`
- [ ] Verify admin user created
- [ ] Restart backend
- [ ] Login with admin credentials
- [ ] Access admin dashboard
- [ ] Test user activation/deactivation
- [ ] Test user deletion
- [ ] Change admin password

---

**Your admin user management system is ready!** 👨‍💼
