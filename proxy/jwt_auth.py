"""
JWT Authentication Module
Handles token generation and validation for cross-origin authentication
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session

# Secret key for JWT (should be same as Flask SECRET_KEY)
JWT_SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def generate_token(user_id, username, role='student'):
    """
    Generate JWT token for authenticated user
    
    Args:
        user_id: User ID (can be string or int)
        username: Username
        role: User role (student, teacher, admin)
    
    Returns:
        JWT token string
    """
    payload = {
        'user_id': str(user_id),  # Convert to string for consistency
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token):
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        return None

def get_token_from_request():
    """
    Extract JWT token from Authorization header or query parameter
    
    Returns:
        Token string or None
    """
    # Try Authorization header first (Bearer token)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Try query parameter as fallback
    token = request.args.get('token')
    if token:
        return token
    
    return None

def token_required(f):
    """
    Decorator to protect routes with JWT authentication
    Falls back to session authentication for backward compatibility
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Try JWT token first
        token = get_token_from_request()
        
        if token:
            payload = decode_token(token)
            if payload:
                # Set session data from token for compatibility
                session['user_id'] = payload['user_id']
                session['username'] = payload['username']
                session['role'] = payload.get('role', 'student')
                print(f"✅ JWT auth: user_id={payload['user_id']}, username={payload['username']}")
                return f(*args, **kwargs)
            else:
                return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Fall back to session authentication
        user_id = session.get('user_id')
        if user_id:
            print(f"✅ Session auth: user_id={user_id}")
            return f(*args, **kwargs)
        
        # No valid authentication
        print("❌ No valid authentication (no token or session)")
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated

def get_current_user():
    """
    Get current user from JWT token or session
    
    Returns:
        Dict with user_id, username, role or None
    """
    # Try JWT token first
    token = get_token_from_request()
    if token:
        payload = decode_token(token)
        if payload:
            return {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'role': payload.get('role', 'student')
            }
    
    # Fall back to session
    user_id = session.get('user_id')
    if user_id:
        return {
            'user_id': user_id,
            'username': session.get('username'),
            'role': session.get('role', 'student')
        }
    
    return None

def admin_required(f):
    """
    Decorator to protect admin-only routes
    Requires JWT authentication and admin role
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check authentication
        token = get_token_from_request()
        
        if token:
            payload = decode_token(token)
            if payload:
                # Set session data from token for compatibility
                session['user_id'] = payload['user_id']
                session['username'] = payload['username']
                session['role'] = payload.get('role', 'student')
                
                # Check if user is admin
                if payload.get('role') == 'admin':
                    print(f"✅ Admin JWT auth: user_id={payload['user_id']}, username={payload['username']}")
                    return f(*args, **kwargs)
                else:
                    print(f"❌ Access denied: user {payload['username']} is not admin")
                    return jsonify({'error': 'Admin access required'}), 403
            else:
                return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Fall back to session authentication
        user_id = session.get('user_id')
        role = session.get('role', 'student')
        
        if user_id:
            if role == 'admin':
                print(f"✅ Admin session auth: user_id={user_id}")
                return f(*args, **kwargs)
            else:
                print(f"❌ Access denied: user {user_id} is not admin")
                return jsonify({'error': 'Admin access required'}), 403
        
        # No valid authentication
        print("❌ No valid authentication (no token or session)")
        return jsonify({'error': 'Authentication required'}), 401
    
    return decorated
