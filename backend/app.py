from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from database import init_db, get_db_connection
from db_config import convert_query
import os
import json
import mysql.connector
from mysql.connector import Error as MySQLError
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Cosmos DB imports
try:
    from cosmos_db import (
        init_cosmos_db,
        # User operations
        create_user,
        get_user_by_username,
        get_user_by_id,
        update_user,
        delete_user,
        get_all_users,
        cosmos_to_mysql_format,
        # Question Bank operations
        save_question_to_bank,
        get_user_questions,
        delete_question,
        # Uploaded Papers operations
        save_uploaded_paper,
        get_user_papers,
        get_all_papers,
        get_paper_by_id,
        delete_paper,
        # Textbooks operations
        save_textbook,
        get_textbooks_by_subject,
        get_all_textbooks,
        get_textbook_by_id,
        delete_textbook,
        # Usage Logs operations
        log_user_activity,
        get_user_activity_logs,
        # Parsed Questions operations
        save_parsed_question,
        get_parsed_questions_by_paper,
        delete_parsed_questions_by_paper,
        get_all_parsed_questions,
        # AI Search Results operations
        save_ai_search_results,
        get_last_ai_search_result
    )
    COSMOS_DB_ENABLED = True
    print("✅ Cosmos DB enabled")
except ImportError as e:
    print(f"⚠️ Cosmos DB disabled: {e}")
    print("   Install: pip install azure-cosmos")
    COSMOS_DB_ENABLED = False
except Exception as e:
    print(f"⚠️ Cosmos DB disabled due to error: {e}")
    COSMOS_DB_ENABLED = False

# Try to import AI service (lightweight version)
try:
    from ai_service_new import (
        analyze_question_paper,
        generate_question_solution as generate_solution,
        index_textbook as extract_chapters_from_textbook,
        semantic_search_textbook,
        TextbookIndex,
        get_service_status
    )
    AI_ENABLED = True
    print("✅ AI features enabled (lightweight)")
except ImportError as e:
    print(f"AI features disabled due to missing dependencies: {e}")
    print("Run: pip install -r requirements.txt")
    AI_ENABLED = False
except Exception as e:
    print(f"AI features disabled due to error: {e}")
    import traceback
    traceback.print_exc()
    AI_ENABLED = False

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Session configuration
# Detect if running in Azure (production) or locally
is_production = (
    os.getenv('FLASK_ENV') == 'production' or 
    os.getenv('WEBSITE_SITE_NAME') is not None or  # Azure App Service
    os.getenv('FUNCTIONS_WORKER_RUNTIME') is not None  # Azure Functions
)
app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_production else 'Lax'
app.config['SESSION_COOKIE_SECURE'] = is_production  # Only use Secure in production (HTTPS)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cross-domain cookies
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
print(f"🍪 Session cookies: SameSite={'None' if is_production else 'Lax'}, Secure={is_production}, Production={is_production}")

# CORS Configuration for Azure
# Get frontend URL from environment variable
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

ALLOWED_ORIGINS = [
    'https://nice-plant-017975e1e.3.azurestaticapps.net',
    'https://zealous-ocean-06e22b51e.3.azurestaticapps.net',  # Current Static Web App
    FRONTEND_URL,  # Azure Static Web App (production)
    'http://localhost:3000',  # Local React development
    'http://localhost:5000',  # Local Flask testing
    'http://127.0.0.1:3000',  # Alternative localhost
    'http://127.0.0.1:5000',  # Alternative localhost
]

# Configure CORS with specific settings for Azure
CORS(app, 
     resources={
         r"/api/*": {
             "origins": ALLOWED_ORIGINS,
             "supports_credentials": True,
             "allow_credentials": True
         }
     },
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Cookie'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     expose_headers=['Content-Type', 'Authorization', 'Set-Cookie'])

# Debug: Print CORS configuration on startup
print("=" * 50)
print("CORS Configuration:")
print(f"Allowed Origins: {ALLOWED_ORIGINS}")
print(f"Supports Credentials: True")
print("=" * 50)

# Add after_request handler to ensure CORS headers are always set
@app.after_request
def after_request(response):
    """Ensure CORS headers are set on all responses"""
    origin = request.headers.get('Origin')
    
    # Check if origin is allowed
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Cookie'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, Authorization, Set-Cookie'
    
    return response

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize databases
init_db()  # MySQL (for backward compatibility)

# Initialize Cosmos DB if enabled
if COSMOS_DB_ENABLED:
    try:
        init_cosmos_db()
        print("✅ Cosmos DB initialized")
    except Exception as e:
        print(f"⚠️ Cosmos DB initialization failed: {e}")
        COSMOS_DB_ENABLED = False

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint - Uses Cosmos DB if enabled, falls back to MySQL"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    print(f"🔍 Login attempt: username={username}")
    
    user = None
    
    # Try Cosmos DB first if enabled
    if COSMOS_DB_ENABLED:
        try:
            print(f"🔍 Querying Cosmos DB for user: {username}")
            cosmos_user = get_user_by_username(username)
            if cosmos_user:
                user = cosmos_to_mysql_format(cosmos_user)
                print(f"✓ User found in Cosmos DB: {username}")
                print(f"   User data: id={user.get('id')}, username={user.get('username')}, has_password={bool(user.get('password'))}")
            else:
                print(f"⚠️ User not found in Cosmos DB: {username}")
        except Exception as e:
            print(f"⚠️ Cosmos DB query failed, falling back to MySQL: {e}")
            import traceback
            traceback.print_exc()
    
    # Fallback to MySQL if Cosmos DB not available or user not found
    if not user:
        print(f"⚠️ User not found in Cosmos DB, trying MySQL fallback...")
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                
                # Get user by username
                try:
                    cursor.execute(
                        'SELECT id, username, password, full_name, is_active, is_admin FROM users WHERE username = %s',
                        (username,)
                    )
                    user = cursor.fetchone()
                except MySQLError:
                    # Fallback for older schema
                    cursor.execute(
                        'SELECT id, username, password, full_name FROM users WHERE username = %s',
                        (username,)
                    )
                    user = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if user:
                    print(f"✓ User found in MySQL: {username}")
            else:
                print(f"⚠️ MySQL connection not available")
        except Exception as e:
            print(f"⚠️ MySQL query failed (expected in Azure): {e}")
            # Don't return error here - user might not exist in either DB
    
    # Verify password
    if not user:
        print(f"❌ User not found: {username}")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    stored_password = user['password']
    print(f"🔑 Password type: {'hashed' if stored_password.startswith(('pbkdf2:', 'scrypt:', '$2b$', '$2a$', '$2y$')) else 'plain'}")
    
    # Check if password is hashed
    if stored_password.startswith(('pbkdf2:', 'scrypt:', '$2b$', '$2a$', '$2y$')):
        if not check_password_hash(stored_password, password):
            print(f"❌ Hashed password verification failed")
            return jsonify({'error': 'Invalid credentials'}), 401
        print(f"✅ Hashed password verified")
    else:
        # Plain text password
        if stored_password != password:
            print(f"❌ Plain text password mismatch")
            return jsonify({'error': 'Invalid credentials'}), 401
        print(f"✅ Plain text password matched")
    
    # Check if account is activated
    if 'is_active' in user.keys() and not user['is_active']:
        return jsonify({'error': 'Please activate your account. Check your email for activation link.'}), 403
    
    # Set session for authenticated user
    session.permanent = True  # Make session permanent (uses PERMANENT_SESSION_LIFETIME)
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    # Check if user is admin
    is_admin = user['is_admin'] if 'is_admin' in user.keys() else 0
    
    print(f"✅ Session created for user {user['username']} (ID: {user['id']})")
    
    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'is_admin': bool(is_admin)
        }
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/test-cosmos', methods=['GET'])
def test_cosmos():
    """Test Cosmos DB connection and list users"""
    try:
        if not COSMOS_DB_ENABLED:
            return jsonify({'error': 'Cosmos DB not enabled'}), 500
        
        from cosmos_db import get_cosmos_container, database
        container = get_cosmos_container('users')
        
        # Get container properties
        container_props = container.read()
        partition_key_def = container_props.get('partitionKey', {})
        
        # Query all users with cross-partition
        query = "SELECT c.id, c.username, c.email, c.password FROM c"
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        # Try to query with partition key
        test_username = "student1"
        query_with_pk = "SELECT * FROM c"
        items_with_pk = list(container.query_items(
            query=query_with_pk,
            partition_key=test_username,
            enable_cross_partition_query=False
        ))
        
        return jsonify({
            'cosmos_enabled': COSMOS_DB_ENABLED,
            'partition_key_definition': partition_key_def,
            'user_count_cross_partition': len(items),
            'user_count_with_pk_student1': len(items_with_pk),
            'users': items[:5],  # First 5 users
            'test_query_result': items_with_pk[:1] if items_with_pk else []
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/session-check', methods=['GET'])
def session_check():
    """Check if user is authenticated"""
    user_id = session.get('user_id')
    username = session.get('username')
    
    if user_id:
        return jsonify({
            'authenticated': True,
            'user_id': user_id,
            'username': username
        })
    else:
        return jsonify({
            'authenticated': False,
            'message': 'No active session'
        }), 401

# OTP storage (in-memory for demo - use Redis in production)
otp_storage = {}

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to phone number"""
    import random
    data = request.get_json()
    phone = data.get('phone')
    
    if not phone or len(phone) != 10:
        return jsonify({'error': 'Valid 10-digit phone number required'}), 400
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with timestamp (for expiry check)
    from datetime import datetime, timedelta
    otp_storage[phone] = {
        'otp': otp,
        'expires_at': datetime.now() + timedelta(minutes=5)
    }
    
    # Try to send SMS for Indian numbers
    sms_sent = False
    try:
        # For Indian numbers, try SMS gateway
        if phone.startswith(('6', '7', '8', '9')):  # Indian mobile numbers
            sms_sent = send_sms_india(phone, otp)
    except Exception as e:
        print(f"SMS sending failed: {e}")
    
    # Always print to console for demo/testing
    print(f"📱 OTP for +91-{phone}: {otp}")
    
    return jsonify({
        'success': True,
        'message': f'OTP sent successfully{" via SMS" if sms_sent else " (check console)"}',
        'otp': otp,  # For demo - shows OTP in response
        'sms_sent': sms_sent
    })

def send_sms_india(phone, otp):
    """Send SMS to Indian phone number using SMS gateway"""
    # Option 1: Fast2SMS (Free tier available)
    # Option 2: MSG91
    # Option 3: Twilio
    
    # For now, using Fast2SMS (requires API key)
    import os
    api_key = os.getenv('FAST2SMS_API_KEY', '')
    
    if not api_key:
        print("⚠️  No SMS API key configured. Set FAST2SMS_API_KEY in .env")
        return False
    
    try:
        import requests
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        payload = {
            "route": "v3",
            "sender_id": "QADAM",
            "message": f"Your QAdam verification code is: {otp}. Valid for 5 minutes.",
            "language": "english",
            "flash": 0,
            "numbers": phone
        }
        
        headers = {
            'authorization': api_key,
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': "no-cache"
        }
        
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('return'):
                print(f"✅ SMS sent successfully to +91-{phone}")
                return True
        
        print(f"⚠️  SMS sending failed: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ SMS error: {e}")
        return False

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for phone number"""
    from datetime import datetime
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')
    
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    
    stored_data = otp_storage.get(phone)
    
    if not stored_data:
        return jsonify({'error': 'OTP expired or not found'}), 400
    
    # Check if OTP is expired
    if datetime.now() > stored_data['expires_at']:
        otp_storage.pop(phone, None)
        return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400
    
    if stored_data['otp'] == otp:
        # OTP verified successfully - don't delete yet, might be needed for login
        return jsonify({'success': True, 'message': 'Phone verified successfully'})
    else:
        return jsonify({'error': 'Invalid OTP'}), 401

@app.route('/api/login-otp', methods=['POST'])
def login_otp():
    """Login with phone and OTP"""
    from datetime import datetime
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')
    
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    
    # Verify OTP
    stored_data = otp_storage.get(phone)
    if not stored_data:
        return jsonify({'error': 'OTP expired or not found'}), 401
    
    # Check expiry
    if datetime.now() > stored_data['expires_at']:
        otp_storage.pop(phone, None)
        return jsonify({'error': 'OTP has expired'}), 401
    
    if stored_data['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 401
    
    # Find user by phone
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, username, full_name FROM users WHERE phone = %s',
        (phone,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        # Clear OTP after successful login
        otp_storage.pop(phone, None)
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name']
            }
        })
    else:
        return jsonify({'error': 'No account found with this phone number'}), 404

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user - Uses Cosmos DB if enabled, falls back to MySQL"""
    data = request.get_json()
    full_name = data.get('fullName')
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    # Validate required fields (phone is optional)
    if not all([full_name, username, email, password]):
        return jsonify({'error': 'Full name, username, email, and password are required'}), 400
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # Validate phone if provided
    if phone and len(phone) != 10:
        return jsonify({'error': 'Valid 10-digit phone number required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Hash password
    hashed_password = generate_password_hash(password)
    
    # Try Cosmos DB first if enabled
    if COSMOS_DB_ENABLED:
        try:
            # Check if username already exists
            existing_user = get_user_by_username(username)
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 409
            
            # Create user in Cosmos DB
            new_user = create_user(
                username=username,
                password=hashed_password,
                full_name=full_name,
                email=email,
                phone=phone,
                is_admin=False
            )
            
            if new_user:
                print(f"✅ User registered in Cosmos DB: {username}")
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! You can now login.',
                    'user': {
                        'id': new_user['id'],
                        'username': new_user['username'],
                        'full_name': new_user['full_name'],
                        'email': new_user.get('email')
                    }
                })
            else:
                print(f"⚠️ Cosmos DB registration failed, falling back to MySQL")
        except Exception as e:
            print(f"⚠️ Cosmos DB registration error, falling back to MySQL: {e}")
    
    # Fallback to MySQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if username already exists
        cursor.execute(
            'SELECT id FROM users WHERE username = %s',
            (username,)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        cursor.execute(
            'SELECT id FROM users WHERE email = %s',
            (email,)
        )
        existing_email = cursor.fetchone()
        
        if existing_email:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409
        
        # Check if phone already exists (only if phone is provided)
        if phone:
            cursor.execute(
                'SELECT id FROM users WHERE phone = %s',
                (phone,)
            )
            existing_phone = cursor.fetchone()
            
            if existing_phone:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Phone number already registered'}), 409
        
        # Generate activation token
        import secrets
        activation_token = secrets.token_urlsafe(32)
        
        # Insert new user (inactive by default)
        try:
            cursor.execute(
                '''INSERT INTO users (username, password, full_name, email, phone, is_active, activation_token) 
                   VALUES (%s, %s, %s, %s, %s, 0, %s)''',
                (username, hashed_password, full_name, email, phone, activation_token)
            )
        except Exception as db_error:
            # Fallback for older database schema
            if 'no column named' in str(db_error).lower():
                print("Using fallback insert (older schema)")
                cursor.execute(
                    'INSERT INTO users (username, password, full_name) VALUES (%s, %s, %s)',
                    (username, hashed_password, full_name)
                )
                activation_token = None  # No activation for old schema
            else:
                raise db_error
        
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        # Send activation email
        if activation_token:
            activation_sent, activation_link = send_activation_email(email, full_name, activation_token)
            
            if not activation_sent:
                # Email not configured - return activation link in response
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! Email not configured.',
                    'activation_required': True,
                    'activation_link': activation_link,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'full_name': full_name,
                        'email': email
                    }
                })
            else:
                # Email sent successfully
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! Please check your email to activate your account.',
                    'activation_required': True,
                    'email_sent': True,
                    'user': {
                        'id': user_id,
                        'username': username,
                        'full_name': full_name,
                        'email': email
                    }
                })
        
        # Fallback for old schema without activation
        return jsonify({
            'success': True,
            'message': 'Registration successful!',
            'activation_required': False,
            'user': {
                'id': user_id,
                'username': username,
                'full_name': full_name,
                'email': email
            }
        })
    except Exception as e:
        conn.close()
        error_msg = str(e)
        print(f"❌ Registration error: {error_msg}")  # Log the actual error
        
        # Provide helpful error messages
        if 'no column named email' in error_msg.lower():
            return jsonify({
                'error': 'Database not updated. Please run: python migrate_database.py',
                'details': 'Email column missing from database'
            }), 500
        elif 'no column named is_active' in error_msg.lower():
            return jsonify({
                'error': 'Database not updated. Please run: python migrate_database.py',
                'details': 'Activation columns missing from database'
            }), 500
        else:
            return jsonify({'error': f'Registration failed: {error_msg}'}), 500

@app.route('/api/activate/<token>', methods=['GET'])
def activate_account(token):
    """Activate user account with token"""
    conn = get_db_connection()
    
    print(f"🔍 Activation attempt with token: {token[:10]}...")
    
    # Find user with this activation token
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT id, username, email, is_active FROM users WHERE activation_token = %s',
        (token,)
    )
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ No user found with this activation token")
        cursor.close()
        conn.close()
        return jsonify({'error': 'Invalid activation token. This link may have already been used or expired.'}), 400
    
    if user['is_active']:
        print(f"✓ Account already activated: {user['username']}")
        cursor.close()
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Account already activated! You can login now.',
            'username': user['username']
        }), 200
    
    # Activate the account
    print(f"✅ Activating account: {user['username']}")
    cursor.execute(
        'UPDATE users SET is_active = 1, activation_token = NULL WHERE id = %s',
        (user['id'],)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ Account activated successfully: {user['username']}")
    
    return jsonify({
        'success': True,
        'message': 'Account activated successfully! You can now login.',
        'username': user['username']
    })

def send_activation_email(email, full_name, activation_token):
    """Send activation email to user using SMTP (Yahoo)"""
    import os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Create activation link
    activation_link = f"http://localhost:3000/activate?token={activation_token}"
    
    # Get SMTP configuration from environment
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.mail.yahoo.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    if not smtp_user or not smtp_password:
        print("⚠️  Email not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
        print(f"📧 Activation link for {email}:")
        print(f"   {activation_link}")
        return False, activation_link
    
    print(f"🔄 Attempting to send email to {email}...")
    print(f"   SMTP Server: {smtp_server}:{smtp_port}")
    print(f"   From: {smtp_user}")
    
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🎓 Activate Your QAdam Account'
        msg['From'] = f'QAdam Academic Portal <{smtp_user}>'
        msg['To'] = email
        
        # Email HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
          </head>
          <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">
              <tr>
                <td align="center">
                  <table width="600" cellpadding="0" cellspacing="0" style="background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                      <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 32px;">🎓 QAdam</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Academic Portal</p>
                      </td>
                    </tr>
                    
                    <!-- Content -->
                    <tr>
                      <td style="padding: 40px 30px;">
                        <h2 style="color: #333; margin: 0 0 20px 0; font-size: 24px;">Welcome, {full_name}! 👋</h2>
                        <p style="color: #666; line-height: 1.6; margin: 0 0 20px 0; font-size: 16px;">
                          Thank you for registering with QAdam Academic Portal. We're excited to have you join our learning community!
                        </p>
                        <p style="color: #666; line-height: 1.6; margin: 0 0 30px 0; font-size: 16px;">
                          To complete your registration and activate your account, please click the button below:
                        </p>
                        
                        <!-- Button -->
                        <table width="100%" cellpadding="0" cellspacing="0">
                          <tr>
                            <td align="center" style="padding: 20px 0;">
                              <a href="{activation_link}" 
                                 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        padding: 16px 40px;
                                        text-decoration: none;
                                        border-radius: 8px;
                                        font-weight: 600;
                                        font-size: 16px;
                                        display: inline-block;
                                        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
                                Activate My Account
                              </a>
                            </td>
                          </tr>
                        </table>
                        
                        <p style="color: #999; font-size: 14px; line-height: 1.6; margin: 30px 0 0 0;">
                          Or copy and paste this link in your browser:<br>
                          <a href="{activation_link}" style="color: #667eea; word-break: break-all;">{activation_link}</a>
                        </p>
                        
                        <div style="background-color: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 30px 0;">
                          <p style="color: #666; font-size: 14px; margin: 0; line-height: 1.5;">
                            <strong>Security Note:</strong> This link will expire once used. If you didn't create this account, please ignore this email.
                          </p>
                        </div>
                      </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                      <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #e0e0e0;">
                        <p style="color: #999; font-size: 12px; margin: 0 0 10px 0;">
                          QAdam Academic Portal - CBSE Senior School
                        </p>
                        <p style="color: #999; font-size: 12px; margin: 0;">
                          This is an automated email. Please do not reply.
                        </p>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email via SMTP
        print(f"🔌 Connecting to SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print(f"🔐 Starting TLS...")
            server.starttls()
            print(f"🔑 Logging in...")
            server.login(smtp_user, smtp_password)
            print(f"📤 Sending message...")
            server.send_message(msg)
        
        print(f"✅ Activation email sent to {email} via Gmail SMTP")
        return True, activation_link
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print(f"   Check your Gmail app password")
        print(f"📧 Activation link for {email}:")
        print(f"   {activation_link}")
        return False, activation_link
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        print(f"📧 Activation link for {email}:")
        print(f"   {activation_link}")
        return False, activation_link
    except Exception as e:
        print(f"❌ Email error: {type(e).__name__}: {e}")
        print(f"📧 Activation link for {email}:")
        print(f"   {activation_link}")
        return False, activation_link

@app.route('/api/sample-questions', methods=['GET'])
def get_sample_questions():
    """Get all sample questions"""
    subject = request.args.get('subject')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if subject:
        cursor.execute(
            'SELECT * FROM sample_questions WHERE subject = %s ORDER BY created_at DESC',
            (subject,)
        )
    else:
        cursor.execute(
            'SELECT * FROM sample_questions ORDER BY created_at DESC'
        )
    
    questions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(questions)

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get all unique subjects"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT DISTINCT subject FROM sample_questions ORDER BY subject'
    )
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify([s['subject'] for s in subjects])

@app.route('/api/upload-paper', methods=['POST'])
def upload_paper():
    """Upload a paper"""
    try:
        print("📤 Upload request received")
        
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        title = request.form.get('title')
        subject = request.form.get('subject')
        user_id = request.form.get('user_id')
        
        print(f"📝 Title: {title}, Subject: {subject}, User: {user_id}")
        print(f"📄 Filename: {file.filename}")
        
        if not title or not subject:
            print("❌ Missing title or subject")
            return jsonify({'error': 'Title and subject required'}), 400
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"❌ Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Allowed: PDF, DOC, DOCX, TXT'}), 400
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"✓ Upload folder ready: {app.config['UPLOAD_FOLDER']}")
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"💾 Saving to: {filepath}")
        file.save(filepath)
        print(f"✓ File saved successfully")
        
        # Verify file exists
        if not os.path.exists(filepath):
            print(f"❌ File not found after save: {filepath}")
            return jsonify({'error': 'Failed to save file'}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"✓ File size: {file_size} bytes")
        
        paper_id = None
        saved = False
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                # Get additional metadata from form
                board = request.form.get('board', 'CBSE')
                year = request.form.get('year', datetime.now().year)
                
                paper_doc = save_uploaded_paper(
                    user_id=str(user_id),
                    title=title,
                    subject=subject,
                    board=board,
                    year=year,
                    file_path=filepath
                )
                
                if paper_doc:
                    paper_id = paper_doc.get('id')
                    saved = True
                    print(f"✓ Paper saved to Cosmos DB with ID: {paper_id}")
            except Exception as e:
                print(f"⚠️ Cosmos DB save failed, trying MySQL: {e}")
        
        # Fallback to MySQL
        if not saved:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO uploaded_papers (title, subject, file_path, user_id) VALUES (%s, %s, %s, %s)',
                    (title, subject, filepath, user_id)
                )
                conn.commit()
                paper_id = cursor.lastrowid
                conn.close()
                saved = True
                print(f"✓ Paper saved to MySQL with ID: {paper_id}")
            except Exception as mysql_error:
                print(f"⚠️ MySQL save failed: {mysql_error}")
                # Clean up the uploaded file if database save failed
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"✓ Cleaned up file: {filepath}")
                return jsonify({
                    'error': 'Failed to save paper metadata',
                    'message': 'Database unavailable. Please try again later.'
                }), 503
        
        return jsonify({
            'success': True,
            'message': 'Paper uploaded successfully',
            'paper_id': paper_id,
            'filename': filename
        })
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/uploaded-papers', methods=['GET'])
def get_uploaded_papers():
    """Get all uploaded papers - Uses Cosmos DB if enabled, falls back to MySQL"""
    try:
        papers = []
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                cosmos_papers = get_all_papers()
                if cosmos_papers:
                    papers = cosmos_papers
                    print(f"✓ Fetched {len(papers)} papers from Cosmos DB")
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed, falling back to MySQL: {e}")
        
        # Fallback to MySQL
        if not papers:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT p.*, u.full_name as uploaded_by_name 
                FROM uploaded_papers p
                LEFT JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            ''')
            papers = cursor.fetchall()
            cursor.close()
            conn.close()
            print(f"✓ Fetched {len(papers)} papers from MySQL")
        
        return jsonify(papers)
        
    except Exception as e:
        print(f"❌ Error in get_uploaded_papers: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-paper/<paper_id>', methods=['DELETE'])
def delete_paper_endpoint(paper_id):
    """Delete a question paper and its associated data - Uses Cosmos DB if enabled"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        print(f"🗑️ Delete paper request - Session: user_id={user_id}, username={username}, paper_id={paper_id}")
        
        if not user_id:
            print(f"❌ No user_id in session - returning 401")
            return jsonify({'error': 'User not authenticated'}), 401
        
        deleted = False
        file_path = None
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                # Get paper info first
                paper_doc = get_paper_by_id(paper_id)
                if paper_doc:
                    print(f"📄 Found paper in Cosmos DB: {paper_doc.get('title')}")
                    print(f"📋 Paper document: {paper_doc}")
                    file_path = paper_doc.get('file_path')
                    # Use the user_id from the paper document as partition key
                    paper_user_id = paper_doc.get('user_id')
                    print(f"🔑 Using partition key user_id: {paper_user_id} (type: {type(paper_user_id).__name__})")
                    deleted = delete_paper(paper_id, paper_user_id)
                    if deleted:
                        print(f"✓ Deleted paper from Cosmos DB: {paper_id}")
                    else:
                        print(f"⚠️ Cosmos DB delete returned False for paper: {paper_id}")
                else:
                    print(f"⚠️ Paper not found in Cosmos DB: {paper_id}")
            except Exception as e:
                print(f"⚠️ Cosmos DB delete failed, trying MySQL: {e}")
        
        # Fallback to MySQL
        if not deleted:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Get paper info
                cursor.execute(
                    'SELECT file_path FROM uploaded_papers WHERE id = %s',
                    (paper_id,)
                )
                paper = cursor.fetchone()
                
                if not paper:
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'Paper not found'}), 404
                
                file_path = paper['file_path']
                
                # Delete parsed questions
                cursor.execute('DELETE FROM parsed_questions WHERE paper_id = %s', (paper_id,))
                print(f"✓ Deleted parsed questions for paper {paper_id}")
                
                # Delete the paper record
                cursor.execute('DELETE FROM uploaded_papers WHERE id = %s', (paper_id,))
                conn.commit()
                cursor.close()
                conn.close()
                deleted = True
                print(f"✓ Deleted paper from MySQL: {paper_id}")
            except Exception as mysql_error:
                print(f"⚠️ MySQL not available: {mysql_error}")
                # If both Cosmos DB and MySQL failed, return error
                if not deleted:
                    return jsonify({
                        'error': 'Failed to delete paper - database unavailable',
                        'message': 'Both Cosmos DB and MySQL are unavailable. Please try again later.'
                    }), 503
        
        # Delete the physical file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ Deleted file: {file_path}")
        
        # Delete FAISS index if exists
        faiss_index_path = f"./vector_db/paper_{paper_id}_questions.index"
        if os.path.exists(faiss_index_path):
            os.remove(faiss_index_path)
            print(f"✓ Deleted FAISS index")
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Paper deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete paper'}), 500
            
    except Exception as e:
        print(f"Error deleting paper: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-textbook', methods=['POST'])
def upload_textbook():
    """Upload a textbook"""
    try:
        print("📚 Textbook upload request received")
        
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        title = request.form.get('title')
        subject = request.form.get('subject')
        author = request.form.get('author', '')
        user_id = request.form.get('user_id')
        
        print(f"📝 Title: {title}, Subject: {subject}, Author: {author}, User: {user_id}")
        print(f"📄 Filename: {file.filename}")
        
        if not title or not subject:
            print("❌ Missing title or subject")
            return jsonify({'error': 'Title and subject required'}), 400
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"❌ Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Allowed: PDF, DOC, DOCX, TXT'}), 400
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"✓ Upload folder ready: {app.config['UPLOAD_FOLDER']}")
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"textbook_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"💾 Saving to: {filepath}")
        file.save(filepath)
        print(f"✓ File saved successfully")
        
        # Verify file exists
        if not os.path.exists(filepath):
            print(f"❌ File not found after save: {filepath}")
            return jsonify({'error': 'Failed to save file'}), 500
        
        file_size = os.path.getsize(filepath)
        print(f"✓ File size: {file_size} bytes")
        
        textbook_id = None
        saved = False
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                # Get additional metadata from form
                board = request.form.get('board', 'CBSE')
                
                textbook_doc = save_textbook(
                    title=title,
                    subject=subject,
                    board=board,
                    file_path=filepath,
                    user_id=str(user_id) if user_id else None
                )
                
                if textbook_doc:
                    textbook_id = textbook_doc.get('id')
                    saved = True
                    print(f"✓ Textbook saved to Cosmos DB with ID: {textbook_id}")
            except Exception as e:
                print(f"⚠️ Cosmos DB save failed, trying MySQL: {e}")
        
        # Fallback to MySQL
        if not saved:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO textbooks (title, subject, file_path, user_id) VALUES (%s, %s, %s, %s)',
                    (title, subject, filepath, user_id)
                )
                conn.commit()
                textbook_id = cursor.lastrowid
                conn.close()
                saved = True
                print(f"✓ Textbook saved to MySQL with ID: {textbook_id}")
            except Exception as mysql_error:
                print(f"⚠️ MySQL save failed: {mysql_error}")
                # Clean up the uploaded file if database save failed
                if os.path.exists(filepath):
                    os.remove(filepath)
                    print(f"✓ Cleaned up file: {filepath}")
                return jsonify({
                    'error': 'Failed to save textbook metadata',
                    'message': 'Database unavailable. Please try again later.'
                }), 503
        
        return jsonify({
            'success': True,
            'message': 'Textbook uploaded successfully',
            'textbook_id': textbook_id,
            'filename': filename
        })
        
    except Exception as e:
        print(f"❌ Textbook upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/textbooks', methods=['GET'])
def get_textbooks():
    """Get all textbooks - Uses Cosmos DB if enabled, falls back to MySQL"""
    try:
        subject = request.args.get('subject')
        textbooks = []
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                if subject:
                    cosmos_textbooks = get_textbooks_by_subject(subject)
                else:
                    cosmos_textbooks = get_all_textbooks()
                
                if cosmos_textbooks:
                    textbooks = cosmos_textbooks
                    print(f"✓ Fetched {len(textbooks)} textbooks from Cosmos DB")
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed, falling back to MySQL: {e}")
        
        # Fallback to MySQL
        if not textbooks:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            if subject:
                cursor.execute('''
                    SELECT t.*, u.full_name as uploaded_by_name 
                    FROM textbooks t
                    LEFT JOIN users u ON t.user_id = u.id
                    WHERE t.subject = %s
                    ORDER BY t.created_at DESC
                ''', (subject,))
            else:
                cursor.execute('''
                    SELECT t.*, u.full_name as uploaded_by_name 
                    FROM textbooks t
                    LEFT JOIN users u ON t.user_id = u.id
                    ORDER BY t.created_at DESC
                ''')
            
            textbooks = cursor.fetchall()
            cursor.close()
            conn.close()
            print(f"✓ Fetched {len(textbooks)} textbooks from MySQL")
        
        # Debug: Log textbook IDs
        if textbooks:
            print(f"📚 Returning {len(textbooks)} textbooks")
            for tb in textbooks:
                print(f"   - {tb.get('title', 'Unknown')}: ID={tb.get('id', 'MISSING')}")
        
        return jsonify(textbooks)
        
    except Exception as e:
        print(f"❌ Error in get_textbooks: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/textbook-pdf/<textbook_id>', methods=['GET'])
def serve_textbook_pdf(textbook_id):
    """Serve textbook PDF file"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT file_path, title FROM textbooks WHERE id = %s',
            (textbook_id,)
        )
        textbook = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not textbook:
            return jsonify({'error': 'Textbook not found'}), 404
        
        file_path = textbook['file_path']
        if not os.path.exists(file_path):
            return jsonify({'error': 'Textbook file not found'}), 404
        
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f"{textbook['title']}.pdf"
        )
    except Exception as e:
        print(f"Error serving textbook PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/textbook-page-image/<textbook_id>/<int:page_number>', methods=['GET'])
def serve_textbook_page_image(textbook_id, page_number):
    """Serve textbook page as image (requires PDF to image conversion)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT file_path FROM textbooks WHERE id = %s',
            (textbook_id,)
        )
        textbook = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not textbook:
            return jsonify({'error': 'Textbook not found'}), 404
        
        # This would require PDF to image conversion
        # For now, return an error suggesting to use PDF viewer
        return jsonify({
            'error': 'Page image conversion not yet implemented',
            'message': 'Please use the PDF Viewer option to view textbook pages'
        }), 501
        
    except Exception as e:
        print(f"Error serving page image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/map-questions-to-chapters', methods=['POST'])
def map_questions_to_chapters_endpoint():
    """Map questions to textbook chapters using semantic search"""
    try:
        if not AI_ENABLED:
            return jsonify({'error': 'AI features not available'}), 503
        
        data = request.json
        print(f"📥 Received data: {type(data)}")
        print(f"   Keys: {data.keys() if data else 'None'}")
        
        questions = data.get('questions', []) if data else []
        textbook_id = data.get('textbook_id') if data else None
        
        print(f"   Questions: {len(questions) if questions else 0}")
        print(f"   Textbook ID: {textbook_id}")
        
        if not questions or not textbook_id:
            print(f"❌ Missing data - questions: {len(questions) if questions else 0}, textbook_id: {textbook_id}")
            return jsonify({
                'error': 'Missing questions or textbook_id',
                'received': {
                    'questions_count': len(questions) if questions else 0,
                    'textbook_id': textbook_id,
                    'data_keys': list(data.keys()) if data else []
                }
            }), 400
        
        print(f"📚 Mapping {len(questions)} questions to chapters for textbook {textbook_id}")
        
        # Use the AI service function
        result = map_questions_to_chapters(questions, textbook_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in map_questions_to_chapters_endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-textbook/<textbook_id>', methods=['DELETE'])
def delete_textbook_endpoint(textbook_id):
    """Delete a textbook - Uses Cosmos DB if enabled"""
    try:
        deleted = False
        file_path = None
        subject = None
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                # Get textbook info first
                textbook_doc = get_textbook_by_id(textbook_id)
                if textbook_doc:
                    file_path = textbook_doc.get('file_path')
                    subject = textbook_doc.get('subject')
                    deleted = delete_textbook(textbook_id, subject)
                    if deleted:
                        print(f"✓ Deleted textbook from Cosmos DB: {textbook_id}")
            except Exception as e:
                print(f"⚠️ Cosmos DB delete failed, trying MySQL: {e}")
        
        # Fallback to MySQL
        if not deleted:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Get textbook info
                cursor.execute(
                    'SELECT file_path FROM textbooks WHERE id = %s',
                    (textbook_id,)
                )
                textbook = cursor.fetchone()
                
                if not textbook:
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'Textbook not found'}), 404
                
                file_path = textbook['file_path']
                
                # Delete the textbook record
                cursor.execute('DELETE FROM textbooks WHERE id = %s', (textbook_id,))
                conn.commit()
                cursor.close()
                conn.close()
                deleted = True
                print(f"✓ Deleted textbook from MySQL: {textbook_id}")
            except Exception as mysql_error:
                print(f"⚠️ MySQL not available: {mysql_error}")
                # If both Cosmos DB and MySQL failed, return error
                if not deleted:
                    return jsonify({
                        'error': 'Failed to delete textbook - database unavailable',
                        'message': 'Both Cosmos DB and MySQL are unavailable. Please try again later.'
                    }), 503
        
        # Delete the physical file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ Deleted file: {file_path}")
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Textbook deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete textbook'}), 500
            
    except Exception as e:
        print(f"Error deleting textbook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/textbook-file/<textbook_id>', methods=['GET'])
def get_textbook_file(textbook_id):
    """Get textbook file info"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM textbooks WHERE id = %s',
        (textbook_id,)
    )
    textbook = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not textbook:
        return jsonify({'error': 'Textbook not found'}), 404
    
    file_path = textbook['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    file_ext = file_path.rsplit('.', 1)[1].lower()
    
    return jsonify({
        'success': True,
        'file_type': file_ext,
        'file_name': os.path.basename(file_path),
        'title': textbook['title'],
        'subject': textbook['subject'],
        'author': textbook['author']
    })

@app.route('/api/download-textbook/<textbook_id>', methods=['GET'])
@app.route('/api/textbooks/<textbook_id>', methods=['GET'])
def download_textbook(textbook_id):
    """Serve textbook file"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM textbooks WHERE id = %s',
        (textbook_id,)
    )
    textbook = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not textbook:
        return jsonify({'error': 'Textbook not found'}), 404
    
    file_path = textbook['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, mimetype='application/pdf' if file_path.endswith('.pdf') else None)

@app.route('/api/paper-file/<paper_id>', methods=['GET'])
def get_paper_file(paper_id):
    """Get paper file for viewing"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM uploaded_papers WHERE id = %s',
        (paper_id,)
    )
    paper = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404
    
    file_path = paper['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Get file extension
    file_ext = file_path.rsplit('.', 1)[1].lower()
    
    return jsonify({
        'success': True,
        'file_type': file_ext,
        'file_name': os.path.basename(file_path),
        'title': paper['title'],
        'subject': paper['subject']
    })

@app.route('/api/download-paper/<paper_id>', methods=['GET'])
def download_paper(paper_id):
    """Download or serve paper file"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM uploaded_papers WHERE id = %s',
        (paper_id,)
    )
    paper = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404
    
    file_path = paper['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Serve the file with proper MIME type
    return send_file(file_path, mimetype='application/pdf' if file_path.endswith('.pdf') else None)

@app.route('/api/analyze-paper', methods=['POST'])
def analyze_paper():
    """Analyze question paper against textbook"""
    if not AI_ENABLED:
        return jsonify({
            'error': 'AI features not available. Please install dependencies: pip install PyMuPDF sentence-transformers chromadb openai python-dotenv'
        }), 503
    
    try:
        data = request.json
        paper_id = data.get('paper_id')
        textbook_id = data.get('textbook_id')
        
        if not paper_id or not textbook_id:
            return jsonify({'error': 'paper_id and textbook_id required'}), 400
        
        # Get paper and textbook paths
        conn = get_db_connection()
        
        paper = conn.execute(
            'SELECT * FROM uploaded_papers WHERE id = %s',
            (paper_id,)
        ).fetchone()
        
        textbook = conn.execute(
            'SELECT * FROM textbooks WHERE id = %s',
            (textbook_id,)
        ).fetchone()
        
        conn.close()
        
        if not paper or not textbook:
            return jsonify({'error': 'Paper or textbook not found'}), 404
        
        # Perform analysis
        result = analyze_question_paper(
            paper_id,
            paper['file_path'],
            textbook_id,
            textbook['file_path']
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-solution', methods=['POST'])
def get_solution():
    """Generate solution for a question"""
    if not AI_ENABLED:
        return jsonify({
            'error': 'AI features not available. Please install dependencies first.'
        }), 503
    
    try:
        data = request.json
        question_text = data.get('question_text')
        textbook_id = data.get('textbook_id')
        subject = data.get('subject', '')
        
        if not question_text:
            return jsonify({'error': 'question_text required'}), 400
        
        # Load textbook index if available
        textbook_index = None
        if textbook_id:
            index_path = f"vector_indices/{textbook_id}/index.pkl"
            if os.path.exists(index_path):
                textbook_index = TextbookIndex.load(index_path)
                print(f"✓ Loaded textbook index for solution generation")
        
        # Generate solution using new AI service
        solution = generate_solution(question_text, textbook_index=textbook_index, subject=subject)
        
        return jsonify({
            'success': True,
            'solution': solution,
            'question': question_text
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/index-textbook/<textbook_id>', methods=['POST'])
def index_textbook(textbook_id):
    """Index a textbook for semantic search"""
    if not AI_ENABLED:
        return jsonify({
            'error': 'AI features not available. Please install dependencies first.'
        }), 503
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM textbooks WHERE id = %s',
            (textbook_id,)
        )
        textbook = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not textbook:
            return jsonify({'error': 'Textbook not found'}), 404
        
        # Index the textbook using new AI service
        file_path = textbook['file_path']
        index = extract_chapters_from_textbook(file_path, textbook_id, chapter_detection='auto')
        
        # Save the index to disk
        index_dir = f"vector_indices/{textbook_id}"
        os.makedirs(index_dir, exist_ok=True)
        index_path = f"{index_dir}/index.pkl"
        index.save(index_path)
        
        result = {
            'success': True,
            'textbook_id': textbook_id,
            'chapters': len(index.chapters),
            'message': f'Successfully indexed {len(index.chapters)} sections'
        }
        
        # If extraction was successful, mark textbook as indexed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE textbooks SET chapters_extracted = 1 WHERE id = %s',
            (textbook_id,)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✓ Marked textbook {textbook_id} as indexed")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/textbook-chapters/<textbook_id>', methods=['GET'])
def get_textbook_chapters(textbook_id):
    """Get chapters for a textbook (supports both UUID and integer IDs)"""
    if not AI_ENABLED:
        return jsonify({
            'error': 'AI features not available. Please install dependencies first.'
        }), 503
    
    try:
        # Try to get textbook from Cosmos DB first
        textbook = None
        if COSMOS_DB_ENABLED:
            try:
                textbook = get_textbook_by_id(textbook_id)
                if textbook:
                    print(f"✓ Found textbook in Cosmos DB: {textbook.get('title')}")
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed: {e}")
        
        # Fallback to MySQL if needed
        if not textbook:
            try:
                # Try as integer first
                try:
                    textbook_id_int = int(textbook_id)
                    conn = get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute('SELECT * FROM textbooks WHERE id = %s', (textbook_id_int,))
                    textbook = cursor.fetchone()
                    cursor.close()
                    conn.close()
                except ValueError:
                    # Not an integer, skip MySQL
                    pass
            except Exception as mysql_error:
                print(f"⚠️ MySQL not available: {mysql_error}")
        
        if not textbook:
            return jsonify({'error': 'Textbook not found'}), 404
        
        # Check if textbook has been indexed
        file_path = textbook.get('file_path')
        if not file_path:
            return jsonify({'error': 'Textbook file path not found'}), 404
        
        # Try to load chapters from vector index
        try:
            index_path = f"vector_indices/{textbook_id}/index.pkl"
            if os.path.exists(index_path):
                index = TextbookIndex.load(index_path)
                chapters = [
                    {
                        'name': ch['name'],
                        'preview': ch['text'][:200] + '...' if len(ch['text']) > 200 else ch['text']
                    }
                    for ch in index.chapters
                ]
                
                return jsonify({
                    'success': True,
                    'chapters': chapters,
                    'textbook_id': textbook_id,
                    'title': textbook.get('title'),
                    'total_chapters': len(chapters)
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Textbook not indexed yet. Please index it first.',
                    'textbook_id': textbook_id
                }), 404
        except Exception as e:
            print(f"Error loading chapters: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Failed to load chapters. Textbook may not be indexed.'
            }), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/index-textbook/<textbook_id>', methods=['POST'])
def index_textbook_uuid(textbook_id):
    """Index a textbook for semantic search (supports both UUID and integer IDs)"""
    if not AI_ENABLED:
        return jsonify({
            'error': 'AI features not available. Please install dependencies first.'
        }), 503
    
    try:
        # Try to get textbook from Cosmos DB first
        textbook = None
        if COSMOS_DB_ENABLED:
            try:
                textbook = get_textbook_by_id(textbook_id)
                if textbook:
                    print(f"✓ Found textbook in Cosmos DB: {textbook.get('title')}")
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed: {e}")
        
        # Fallback to MySQL if needed
        if not textbook:
            try:
                # Try as integer first
                try:
                    textbook_id_int = int(textbook_id)
                    conn = get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute('SELECT * FROM textbooks WHERE id = %s', (textbook_id_int,))
                    textbook = cursor.fetchone()
                    cursor.close()
                    conn.close()
                except ValueError:
                    # Not an integer, skip MySQL
                    pass
            except Exception as mysql_error:
                print(f"⚠️ MySQL not available: {mysql_error}")
        
        if not textbook:
            return jsonify({'error': 'Textbook not found'}), 404
        
        file_path = textbook.get('file_path')
        if not file_path:
            return jsonify({'error': 'Textbook file path not found'}), 404
        
        # Check if file exists
        if not os.path.exists(file_path):
            # Try with backend prefix
            backend_path = os.path.join('backend', file_path)
            if os.path.exists(backend_path):
                file_path = backend_path
            else:
                return jsonify({
                    'error': f'Textbook file not found: {file_path}',
                    'message': 'The PDF file needs to be uploaded before indexing.',
                    'file_path': file_path
                }), 404
        
        # Index the textbook using new AI service
        index = extract_chapters_from_textbook(file_path, textbook_id, chapter_detection='auto')
        
        # Save the index to disk
        index_dir = f"vector_indices/{textbook_id}"
        os.makedirs(index_dir, exist_ok=True)
        index_path = f"{index_dir}/index.pkl"
        index.save(index_path)
        
        result = {
            'success': True,
            'textbook_id': textbook_id,
            'chapters': len(index.chapters),
            'message': f'Successfully indexed {len(index.chapters)} sections'
        }
        
        # Mark textbook as indexed
        if result and 'error' not in result:
            if COSMOS_DB_ENABLED:
                try:
                    # Update in Cosmos DB
                    textbook['chapters_extracted'] = True
                    # Note: You may need to implement update_textbook in cosmos_db.py
                    print(f"✓ Marked textbook {textbook_id} as indexed in Cosmos DB")
                except Exception as e:
                    print(f"⚠️ Failed to update Cosmos DB: {e}")
            
            # Also try MySQL if available
            try:
                textbook_id_int = int(textbook_id)
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE textbooks SET chapters_extracted = 1 WHERE id = %s',
                    (textbook_id_int,)
                )
                conn.commit()
                cursor.close()
                conn.close()
                print(f"✓ Marked textbook {textbook_id} as indexed in MySQL")
            except (ValueError, Exception) as e:
                # Not an integer or MySQL not available
                pass
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parse-questions/<paper_id>', methods=['POST'])
def parse_questions(paper_id):
    """Parse questions from a paper using OCR + Groq AI"""
    try:
        from question_parser import parse_question_paper_fixed as parse_question_paper
        import json
        import faiss
        import numpy as np
        
        # Get paper details - Try Cosmos DB first
        paper = None
        file_path = None
        
        if COSMOS_DB_ENABLED:
            try:
                paper = get_paper_by_id(paper_id)
                if paper:
                    file_path = paper.get('file_path')
                    print(f"✓ Found paper in Cosmos DB: {paper.get('title')}")
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed: {e}")
        
        # Fallback to MySQL
        if not paper:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    'SELECT * FROM uploaded_papers WHERE id = %s',
                    (paper_id,)
                )
                paper = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if paper:
                    file_path = paper['file_path']
                    print(f"✓ Found paper in MySQL")
            except Exception as mysql_error:
                print(f"⚠️ MySQL query failed: {mysql_error}")
        
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Delete old FAISS index if exists
        faiss_index_path = f"./vector_db/paper_{paper_id}_questions.index"
        if os.path.exists(faiss_index_path):
            os.remove(faiss_index_path)
            print(f"✓ Deleted old FAISS index")
        
        # Parse the question paper
        print(f"📄 Parsing question paper: {file_path}")
        result = parse_question_paper(file_path)
        
        if not result or result is None:
            return jsonify({'error': 'Failed to parse question paper'}), 500
        
        questions = result.get('questions', [])
        print(f"✓ Parsed {len(questions)} questions from paper")
        
        # Store in FAISS vector database
        if AI_ENABLED:
            try:
                from ai_service import get_embedding_model
                model = get_embedding_model()
                
                # Create embeddings for questions
                question_texts = [q['question_text'] for q in questions]
                embeddings = model.encode(question_texts, show_progress_bar=False)
                embeddings_np = np.array(embeddings).astype('float32')
                
                # Create FAISS index
                dimension = embeddings_np.shape[1]
                index = faiss.IndexFlatL2(dimension)
                index.add(embeddings_np)
                
                # Save FAISS index
                index_path = f"./vector_db/paper_{paper_id}_questions.index"
                os.makedirs("./vector_db", exist_ok=True)
                faiss.write_index(index, index_path)
                
                print(f"✓ Stored {len(questions)} questions in FAISS")
            except Exception as e:
                print(f"⚠ FAISS storage failed: {e}")
        
        # Store in database - Try Cosmos DB first, fallback to MySQL
        saved = False
        
        if COSMOS_DB_ENABLED:
            try:
                # Clean up existing questions for this paper
                print(f"\n🧹 Cleaning existing parsed questions from Cosmos DB for paper {paper_id}...")
                delete_parsed_questions_by_paper(paper_id)
                
                print(f"💾 Storing {len(questions)} questions in Cosmos DB...")
                for idx, q in enumerate(questions):
                    q_num = q.get('question_number', str(idx + 1))
                    
                    # Debug: Show first 5 questions
                    if idx < 5:
                        q_text_preview = q.get('question_text', '')[:80]
                        print(f"  Q{q_num}: {q_text_preview}...")
                    
                    save_parsed_question(
                        paper_id=paper_id,
                        question_number=q_num,
                        question_text=q.get('question_text', ''),
                        question_type=q.get('question_type', 'unknown'),
                        sub_parts=q.get('sub_parts', []),
                        has_diagram=q.get('has_diagram', False),
                        marks=q.get('marks'),
                        embedding_id=idx,
                        parsed_data=q  # Store full question data
                    )
                
                # Verify storage
                stored_questions = get_parsed_questions_by_paper(paper_id)
                print(f"✅ Stored {len(stored_questions)} questions in Cosmos DB")
                saved = True
                
            except Exception as cosmos_error:
                print(f"⚠️ Cosmos DB storage failed: {cosmos_error}")
        
        # Fallback to MySQL if Cosmos DB failed or not enabled
        if not saved:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Clean up existing questions for this paper
                print(f"\n🧹 Cleaning existing parsed questions for paper {paper_id}...")
                cursor.execute('DELETE FROM parsed_questions WHERE paper_id = %s', (paper_id,))
                conn.commit()
                
                print(f"💾 Storing {len(questions)} NEW questions in MySQL...")
                for idx, q in enumerate(questions):
                    q_num = q.get('question_number', str(idx + 1))
                    
                    # Debug: Show first 5 questions
                    if idx < 5:
                        q_text_preview = q.get('question_text', '')[:80]
                        print(f"  Q{q_num}: {q_text_preview}...")
                    
                    cursor.execute('''
                        INSERT INTO parsed_questions 
                        (paper_id, question_number, question_text, question_type, 
                         sub_parts, has_diagram, marks, embedding_id, parsed_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        paper_id,
                        q_num,
                        q.get('question_text', ''),
                        q.get('question_type', 'unknown'),
                        json.dumps(q.get('sub_parts', [])),
                        1 if q.get('has_diagram', False) else 0,
                        q.get('marks'),
                        idx,
                        json.dumps(q)  # This includes diagram_files
                    ))
                
                conn.commit()
                
                # Final verification
                cursor.execute('SELECT COUNT(*) FROM parsed_questions WHERE paper_id = %s', (paper_id,))
                final_count = cursor.fetchone()[0]
                print(f"✅ Stored {final_count} questions in MySQL")
                
                cursor.close()
                conn.close()
                saved = True
            except Exception as db_error:
                print(f"⚠️ MySQL storage failed: {db_error}")
        
        if not saved:
            print(f"⚠️ WARNING: Questions stored in FAISS only, not in database!")
        
        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'questions': questions,
            'diagrams_extracted': len(result.get('diagrams', []))
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/parsed-questions', methods=['GET'])
def get_parsed_questions():
    """Get all parsed questions - Uses Cosmos DB if enabled, falls back to MySQL"""
    paper_id = request.args.get('paper_id')
    questions = []
    
    # Try Cosmos DB first
    if COSMOS_DB_ENABLED:
        try:
            if paper_id:
                print(f"📖 Fetching parsed questions from Cosmos DB for paper_id={paper_id}")
                questions = get_parsed_questions_by_paper(paper_id)
                print(f"  Found {len(questions)} questions in Cosmos DB")
            else:
                print(f"📖 Fetching all parsed questions from Cosmos DB")
                questions = get_all_parsed_questions()
                print(f"  Found {len(questions)} questions in Cosmos DB")
        except Exception as e:
            print(f"⚠️ Cosmos DB query failed: {e}")
    
    # Fallback to MySQL if no questions found
    if not questions:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            if paper_id:
                print(f"📖 Fetching parsed questions from MySQL for paper_id={paper_id}")
                cursor.execute('''
                    SELECT pq.*, up.title as paper_title, up.subject
                    FROM parsed_questions pq
                    JOIN uploaded_papers up ON pq.paper_id = up.id
                    WHERE pq.paper_id = %s
                    ORDER BY CAST(pq.question_number AS UNSIGNED)
                ''', (paper_id,))
                questions = cursor.fetchall()
                print(f"  Found {len(questions)} questions in MySQL")
            else:
                cursor.execute('''
                    SELECT pq.*, up.title as paper_title, up.subject
                    FROM parsed_questions pq
                    JOIN uploaded_papers up ON pq.paper_id = up.id
                    ORDER BY pq.created_at DESC
                    LIMIT 100
                ''')
                questions = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ MySQL not available for parsed questions: {e}")
    
    print(f"📖 Returning {len(questions)} parsed questions for paper_id={paper_id if paper_id else 'all'}")
    return jsonify(questions)

@app.route('/api/diagram/<paper_id>/<filename>', methods=['GET'])
def get_diagram(paper_id, filename):
    """Serve diagram file"""
    try:
        # Get paper to find its directory - Try Cosmos DB first
        paper = None
        file_path = None
        
        if COSMOS_DB_ENABLED:
            try:
                paper = get_paper_by_id(paper_id)
                if paper:
                    file_path = paper.get('file_path')
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed: {e}")
        
        # Fallback to MySQL
        if not paper:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    'SELECT file_path FROM uploaded_papers WHERE id = %s',
                    (paper_id,)
                )
                paper = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if paper:
                    file_path = paper['file_path']
            except Exception as mysql_error:
                print(f"⚠️ MySQL query failed: {mysql_error}")
        
        if not paper or not file_path:
            return jsonify({'error': 'Paper not found'}), 404
        
        # Construct diagram path
        paper_dir = os.path.dirname(file_path)
        diagram_path = os.path.join(paper_dir, 'diagrams', filename)
        
        if not os.path.exists(diagram_path):
            return jsonify({'error': f'Diagram not found: {diagram_path}'}), 404
        
        # Serve the diagram file
        return send_file(diagram_path, mimetype='image/jpeg')
        
    except Exception as e:
        print(f"❌ Error serving diagram: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/clean-duplicates', methods=['POST'])
def clean_duplicates():
    """Remove duplicate parsed questions from database"""
    try:
        conn = get_db_connection()
        
        # Find duplicates (same paper_id and question_number)
        duplicates = conn.execute('''
            SELECT paper_id, question_number, COUNT(*) as count
            FROM parsed_questions
            GROUP BY paper_id, question_number
            HAVING count > 1
        ''').fetchall()
        
        total_removed = 0
        
        for dup in duplicates:
            paper_id = dup['paper_id']
            question_number = dup['question_number']
            
            # Keep only the most recent one, delete others
            conn.execute('''
                DELETE FROM parsed_questions
                WHERE id NOT IN (
                    SELECT MAX(id)
                    FROM parsed_questions
                    WHERE paper_id = ? AND question_number = ?
                )
                AND paper_id = ? AND question_number = ?
            ''', (paper_id, question_number, paper_id, question_number))
            
            total_removed += dup['count'] - 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'duplicates_found': len(duplicates),
            'questions_removed': total_removed,
            'message': f'Removed {total_removed} duplicate questions'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parse-single-question', methods=['POST'])
def parse_single_question():
    """Parse a single question from text, image, or document"""
    try:
        import question_parser
        
        # Import with error handling
        try:
            import pytesseract
        except ImportError:
            return jsonify({'error': 'pytesseract not installed. Run: pip install pytesseract'}), 500
        
        try:
            from PIL import Image
        except ImportError:
            return jsonify({'error': 'Pillow not installed. Run: pip install Pillow'}), 500
        
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return jsonify({'error': 'PyMuPDF not installed. Run: pip install PyMuPDF'}), 500
        
        try:
            from docx import Document
        except ImportError:
            return jsonify({'error': 'python-docx not installed. Run: pip install python-docx'}), 500
        
        input_type = request.form.get('input_type')
        question_text = None
        
        if input_type == 'text':
            # Direct text input
            question_text = request.form.get('question_text', '').strip()
            if not question_text:
                return jsonify({'error': 'No question text provided'}), 400
                
        elif input_type == 'file':
            # File upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            file_type = request.form.get('file_type', '').lower()
            
            # Save file temporarily
            temp_filename = secure_filename(f"temp_question_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_type}")
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            file.save(temp_path)
            
            try:
                # Extract text based on file type
                if file_type in ['jpg', 'jpeg', 'png']:
                    # OCR for images
                    try:
                        image = Image.open(temp_path)
                        question_text = pytesseract.image_to_string(image)
                    except pytesseract.TesseractNotFoundError:
                        return jsonify({
                            'error': 'OCR not available on Azure. Please use text input or PDF/DOCX files instead.',
                            'suggestion': 'Copy and paste the question text, or upload a PDF/DOCX file.'
                        }), 503
                    except Exception as ocr_error:
                        return jsonify({
                            'error': f'OCR failed: {str(ocr_error)}',
                            'suggestion': 'Please use text input or PDF/DOCX files instead.'
                        }), 500
                    
                elif file_type == 'pdf':
                    # Extract from PDF
                    doc = fitz.open(temp_path)
                    question_text = ""
                    for page in doc:
                        question_text += page.get_text()
                    doc.close()
                    
                elif file_type == 'docx':
                    # Extract from DOCX
                    doc = Document(temp_path)
                    question_text = "\n".join([para.text for para in doc.paragraphs])
                    
                elif file_type == 'txt':
                    # Read text file
                    with open(temp_path, 'r', encoding='utf-8') as f:
                        question_text = f.read()
                        
                else:
                    return jsonify({'error': f'Unsupported file type: {file_type}'}), 400
                    
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        else:
            return jsonify({'error': 'Invalid input type'}), 400
        
        if not question_text or not question_text.strip():
            return jsonify({'error': 'Could not extract text from input'}), 400
        
        # Parse the question using Groq AI
        print(f"Parsing single question: {question_text[:100]}...")
        
        # Create a simple question block
        question_block = {
            'block_number': 1,
            'raw_text': question_text.strip(),
            'instruction': None
        }
        
        # Use the existing Groq parser
        parsed_questions = question_parser.parse_with_groq_fixed([question_block])
        
        if parsed_questions and len(parsed_questions) > 0:
            parsed_question = parsed_questions[0]
            
            return jsonify({
                'success': True,
                'question': parsed_question,
                'extracted_text': question_text[:500]  # First 500 chars for reference
            })
        else:
            return jsonify({'error': 'Failed to parse question'}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-ai-search-results', methods=['POST'])
def save_ai_search_results_endpoint():
    """Save AI search results to database"""
    import json  # Explicit import to avoid scope issues
    try:
        data = request.get_json()
        paper_id = data.get('paper_id')
        textbook_id = data.get('textbook_id')
        search_results = data.get('search_results')
        
        if not paper_id or not textbook_id or not search_results:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Calculate stats
        total_chapters = len(search_results)
        total_questions = sum(len(data['questions']) for data in search_results.values())
        unmatched_count = len(search_results.get('Unmatched Questions', {}).get('questions', []))
        
        saved = False
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                result = save_ai_search_results(
                    paper_id=paper_id,
                    textbook_id=textbook_id,
                    search_results=search_results,
                    total_chapters=total_chapters,
                    total_questions=total_questions,
                    unmatched_count=unmatched_count
                )
                if result:
                    saved = True
                    return jsonify({
                        'success': True,
                        'message': 'Search results saved to Cosmos DB successfully'
                    })
            except Exception as cosmos_error:
                print(f"⚠️ Cosmos DB save failed: {cosmos_error}")
        
        # Fallback to MySQL
        if not saved:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Delete old results for this paper-textbook combination
                cursor.execute('''
                    DELETE FROM ai_search_results 
                    WHERE paper_id = %s AND textbook_id = %s
                ''', (paper_id, textbook_id))
                
                # Insert new results
                cursor.execute('''
                    INSERT INTO ai_search_results 
                    (paper_id, textbook_id, search_results, total_chapters, total_questions, unmatched_count)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    paper_id,
                    textbook_id,
                    json.dumps(search_results),
                    total_chapters,
                    total_questions,
                    unmatched_count
                ))
                
                conn.commit()
                cursor.close()
                conn.close()
                saved = True
                
                return jsonify({
                    'success': True,
                    'message': 'Search results saved to MySQL successfully'
                })
            except Exception as mysql_error:
                print(f"⚠️ MySQL save failed: {mysql_error}")
        
        if not saved:
            return jsonify({
                'error': 'Failed to save search results - no database available'
            }), 503
        
        return jsonify({
            'success': True,
            'message': 'Search results saved successfully'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-last-ai-search', methods=['GET'])
def get_last_ai_search():
    """Get last AI search results for a paper-textbook combination"""
    import json  # Explicit import to avoid scope issues
    try:
        paper_id = request.args.get('paper_id')
        textbook_id = request.args.get('textbook_id')
        
        if not paper_id or not textbook_id:
            return jsonify({'error': 'Missing paper_id or textbook_id'}), 400
        
        result = None
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                result = get_last_ai_search_result(paper_id, textbook_id)
                if result:
                    return jsonify({
                        'success': True,
                        'search_results': result.get('search_results'),  # Already an object in Cosmos DB
                        'total_chapters': result.get('total_chapters'),
                        'total_questions': result.get('total_questions'),
                        'unmatched_count': result.get('unmatched_count'),
                        'created_at': result.get('created_at')
                    })
            except Exception as cosmos_error:
                print(f"⚠️ Cosmos DB query failed: {cosmos_error}")
        
        # Fallback to MySQL
        if not result:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('''
                    SELECT search_results, total_chapters, total_questions, unmatched_count, created_at
                    FROM ai_search_results
                    WHERE paper_id = %s AND textbook_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (paper_id, textbook_id))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    return jsonify({
                        'success': True,
                        'search_results': json.loads(result['search_results']),  # JSON string in MySQL
                        'total_chapters': result['total_chapters'],
                        'total_questions': result['total_questions'],
                        'unmatched_count': result['unmatched_count'],
                        'created_at': result['created_at']
                    })
            except Exception as db_error:
                print(f"⚠️ MySQL not available for AI search results: {db_error}")
        
        # No results found in either database
        return jsonify({
            'success': False,
            'message': 'No previous search results found'
        }), 404
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/solve-question', methods=['POST'])
def solve_question():
    """Solve a question using LLM with detailed step-by-step solution"""
    if not AI_ENABLED:
        return jsonify({'error': 'AI features are not enabled'}), 503
    
    try:
        data = request.json
        question_text = data.get('question_text')
        question_type = data.get('question_type', 'unknown')
        subject = data.get('subject')
        chapter_context = data.get('chapter_context')
        
        if not question_text:
            return jsonify({'error': 'question_text is required'}), 400
        
        print(f"🎓 Solving question: {question_text[:60]}...")
        
        # Use the new AI service to generate solution
        context = chapter_context if chapter_context else ""
        solution = generate_solution(
            question_text=question_text,
            context=context,
            subject=subject or ""
        )
        
        result = {
            'success': True,
            'solution': solution,
            'question_text': question_text,
            'subject': subject,
            'question_type': question_type
        }
        
        # Log token usage
        if result.get('tokens_used'):
            user_id = session.get('user_id')
            if user_id:
                try:
                    conn = get_db_connection()
                    conn.execute('''
                        INSERT INTO usage_logs (user_id, action_type, tokens_used, model_name, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, 'solve_question', result.get('tokens_used'), result.get('model'), datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                    print(f"📊 Logged {result.get('tokens_used')} tokens for user {user_id}")
                except Exception as log_err:
                    print(f"Warning: Failed to log token usage: {log_err}")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-solved-question', methods=['POST'])
def save_solved_question():
    """Save a solved question to the Question Bank - Uses Cosmos DB if enabled"""
    try:
        data = request.json
        question_text = data.get('question_text')
        solution = data.get('solution')
        source = data.get('source', 'unknown')
        subject = data.get('subject')  # Subject from Solve One Question
        timestamp = data.get('timestamp')
        paper_id = data.get('paper_id')  # Optional: from Answer Chapterwise
        textbook_id = data.get('textbook_id')  # Optional: from Answer Chapterwise
        chapter_name = data.get('chapter_name')  # Optional: from Answer Chapterwise
        
        if not question_text or not solution:
            return jsonify({'error': 'question_text and solution are required'}), 400
        
        # Get current user from session
        user_id = session.get('user_id')
        username = session.get('username')
        print(f"🔍 Save question request - Session: user_id={user_id}, username={username}")
        
        if not user_id:
            print(f"❌ No user_id in session - returning 401")
            return jsonify({'error': 'User not authenticated'}), 401
        
        question_id = None
        saved = False
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                question_id = save_question_to_bank(
                    user_id=str(user_id),
                    question_text=question_text,
                    solution=solution,
                    source=source,
                    subject=subject,
                    paper_id=paper_id,
                    textbook_id=textbook_id,
                    chapter_name=chapter_name
                )
                if question_id:
                    saved = True
                    print(f"✅ Saved question to Cosmos DB: {question_id}")
            except Exception as e:
                print(f"⚠️ Cosmos DB save failed, falling back to MySQL: {e}")
        
        # Fallback to MySQL
        if not saved:
            try:
                # Convert timestamp to MySQL datetime format
                if timestamp:
                    # Handle ISO 8601 format with 'Z' timezone
                    timestamp = timestamp.replace('Z', '+00:00')
                    from dateutil import parser
                    created_at = parser.parse(timestamp)
                else:
                    created_at = datetime.now()
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO question_bank (question_text, solution, source, subject, paper_id, textbook_id, chapter_name, user_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (question_text, solution, source, subject, paper_id, textbook_id, chapter_name, user_id, created_at))
                
                conn.commit()
                question_id = cursor.lastrowid
                cursor.close()
                conn.close()
                saved = True
                print(f"✅ Saved question to MySQL: {question_id}")
            except Exception as mysql_error:
                print(f"❌ MySQL save failed: {mysql_error}")
                return jsonify({'error': 'Failed to save question - database unavailable'}), 500
        
        log_msg = f"✅ Saved question {question_id} to Question Bank from {source}"
        if subject:
            log_msg += f" (Subject: {subject})"
        if paper_id:
            log_msg += f" (Paper ID: {paper_id})"
        if textbook_id:
            log_msg += f" (Textbook ID: {textbook_id})"
        if chapter_name:
            log_msg += f" (Chapter: {chapter_name})"
        print(log_msg)
        
        return jsonify({
            'success': True,
            'question_id': question_id,
            'message': 'Question saved to Question Bank'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/question-bank', methods=['GET'])
def get_question_bank():
    """Get all questions from Question Bank for current user - Uses Cosmos DB if enabled"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        print(f"🔍 Question Bank request - Session: user_id={user_id}, username={username}")
        
        if not user_id:
            print(f"❌ No user_id in session - returning 401")
            return jsonify({'error': 'User not authenticated'}), 401
        
        questions = []
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                cosmos_questions = get_user_questions(str(user_id))
                if cosmos_questions:
                    questions = cosmos_questions
                    print(f"✓ Fetched {len(questions)} questions from Cosmos DB")
            except Exception as e:
                print(f"⚠️ Cosmos DB query failed, falling back to MySQL: {e}")
        
        # Fallback to MySQL if no questions found in Cosmos DB
        if not questions:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute('''
                    SELECT qb.id, qb.question_text, qb.solution, qb.source, qb.subject, qb.created_at,
                           qb.paper_id, qb.textbook_id, qb.chapter_name,
                           up.title as paper_title, tb.title as textbook_title
                    FROM question_bank qb
                    LEFT JOIN uploaded_papers up ON qb.paper_id = up.id
                    LEFT JOIN textbooks tb ON qb.textbook_id = tb.id
                    WHERE qb.user_id = %s
                    ORDER BY qb.created_at DESC
                ''', (user_id,))
                
                questions = cursor.fetchall()
                cursor.close()
                conn.close()
                print(f"✓ Fetched {len(questions)} questions from MySQL")
            except Exception as mysql_error:
                print(f"⚠️ MySQL not available: {mysql_error}")
                print(f"✓ Returning empty question bank (no questions in Cosmos DB, MySQL unavailable)")
                questions = []
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/question-bank/<question_id>', methods=['DELETE'])
def delete_question_from_bank(question_id):
    """Delete a question from Question Bank - Uses Cosmos DB if enabled"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401
        
        deleted = False
        
        # Try Cosmos DB first
        if COSMOS_DB_ENABLED:
            try:
                deleted = delete_question(question_id, str(user_id))
                if deleted:
                    print(f"✓ Deleted question from Cosmos DB: {question_id}")
            except Exception as e:
                print(f"⚠️ Cosmos DB delete failed, trying MySQL: {e}")
        
        # Fallback to MySQL
        if not deleted:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verify ownership before deleting
            cursor.execute('''
                SELECT id FROM question_bank
                WHERE id = %s AND user_id = %s
            ''', (question_id, user_id))
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'error': 'Question not found or unauthorized'}), 404
            
            cursor.execute('DELETE FROM question_bank WHERE id = %s', (question_id,))
            conn.commit()
            cursor.close()
            conn.close()
            deleted = True
            print(f"✓ Deleted question from MySQL: {question_id}")
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Question deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete question'}), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

# ============================================
# ADMIN USER MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all users (admin only)"""
    # TODO: Add proper admin authentication check
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            '''SELECT id, username, full_name, email, phone, is_active, is_admin, created_at 
               FROM users ORDER BY created_at DESC'''
        )
        users = cursor.fetchall()
        
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'email': user['email'],
                'phone': user['phone'],
                'is_active': bool(user['is_active']),
                'is_admin': bool(user['is_admin']),
                'created_at': user['created_at']
            })
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'users': users_list})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/toggle-active', methods=['POST'])
def toggle_user_active(user_id):
    """Activate or deactivate a user (admin only)"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get current status
        cursor.execute(
            'SELECT id, username, is_active FROM users WHERE id = %s',
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Toggle status
        new_status = 0 if user['is_active'] else 1
        
        cursor.execute(
            'UPDATE users SET is_active = %s WHERE id = %s',
            (new_status, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        status_text = "activated" if new_status else "deactivated"
        print(f"✅ Admin {status_text} user: {user['username']}")
        
        return jsonify({
            'success': True,
            'message': f'User {status_text} successfully',
            'is_active': bool(new_status)
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user account (admin only)"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check if user exists
        cursor.execute(
            'SELECT id, username, is_admin FROM users WHERE id = %s',
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting admin accounts
        if user['is_admin']:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot delete admin accounts'}), 403
        
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"🗑️ Admin deleted user: {user['username']}")
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/usage-analytics', methods=['GET'])
def get_usage_analytics():
    """Get usage analytics including token usage and questions solved by each user (admin only)"""
    conn = get_db_connection()
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get questions solved by each user from question_bank
        cursor.execute('''
            SELECT 
                u.id as user_id,
                u.username,
                u.full_name,
                COUNT(qb.id) as questions_solved,
                COUNT(CASE WHEN qb.source = 'solve_one' THEN 1 END) as solve_one_count,
                COUNT(CASE WHEN qb.source = 'answer_chapterwise' THEN 1 END) as chapterwise_count,
                COUNT(CASE WHEN qb.source = 'all_questions' THEN 1 END) as all_questions_count,
                COUNT(DISTINCT qb.subject) as subjects_covered,
                MIN(qb.created_at) as first_question_date,
                MAX(qb.created_at) as last_question_date
            FROM users u
            LEFT JOIN question_bank qb ON u.id = qb.user_id
            GROUP BY u.id, u.username, u.full_name
            ORDER BY questions_solved DESC
        ''')
        questions_by_user = cursor.fetchall()
        
        # Get token usage by user from usage_logs (if any logs exist)
        cursor.execute('''
            SELECT 
                u.id as user_id,
                u.username,
                u.full_name,
                COALESCE(SUM(ul.tokens_used), 0) as total_tokens,
                COUNT(ul.id) as api_calls,
                ul.model_name
            FROM users u
            LEFT JOIN usage_logs ul ON u.id = ul.user_id
            GROUP BY u.id, u.username, u.full_name, ul.model_name
            HAVING total_tokens > 0
            ORDER BY total_tokens DESC
        ''')
        token_usage = cursor.fetchall()
        
        # Get overall statistics
        cursor.execute('''
            SELECT 
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as total_questions_solved,
                COUNT(DISTINCT subject) as total_subjects
            FROM question_bank
        ''')
        overall_stats = cursor.fetchone()
        
        # Format user analytics
        user_analytics = []
        for row in questions_by_user:
            user_analytics.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'full_name': row['full_name'],
                'questions_solved': row['questions_solved'],
                'solve_one_count': row['solve_one_count'],
                'chapterwise_count': row['chapterwise_count'],
                'all_questions_count': row['all_questions_count'],
                'subjects_covered': row['subjects_covered'],
                'first_question_date': row['first_question_date'],
                'last_question_date': row['last_question_date']
            })
        
        # Format token usage
        token_analytics = []
        for row in token_usage:
            token_analytics.append({
                'user_id': row['user_id'],
                'username': row['username'],
                'full_name': row['full_name'],
                'total_tokens': row['total_tokens'],
                'api_calls': row['api_calls'],
                'model_name': row['model_name'] or 'N/A'
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'user_analytics': user_analytics,
            'token_analytics': token_analytics,
            'overall_stats': {
                'active_users': overall_stats['active_users'] if overall_stats else 0,
                'total_questions_solved': overall_stats['total_questions_solved'] if overall_stats else 0,
                'total_subjects': overall_stats['total_subjects'] if overall_stats else 0
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
