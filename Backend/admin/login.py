from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from model import Database
import jwt
import datetime
import logging
from functools import wraps
from config import Config

# Setup logger sederhana untuk debugging login
logger = logging.getLogger(__name__)

# PERBAIKAN 1: Tidak ada url_prefix di sini karena sudah diatur global di app.py
login_bp = Blueprint('login', __name__) 

def _get_token_from_request(include_session=True):
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]

    return session.get('token') if include_session else None


def get_current_user_id(optional=False):
    token = _get_token_from_request(include_session=not optional)

    if not token:
        return None if optional else (jsonify({'error': 'Token tidak ditemukan'}), 401)

    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return data['user_id']
    except jwt.ExpiredSignatureError:
        return None if optional else (jsonify({'error': 'Token telah kadaluarsa'}), 401)
    except jwt.InvalidTokenError:
        return None if optional else (jsonify({'error': 'Token tidak valid'}), 401)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user_id()
        if isinstance(current_user, tuple):
            return current_user

        return f(current_user, *args, **kwargs)
    return decorated


@login_bp.route('/register', methods=['POST'])
def register():
    """Endpoint daftar akun dari halaman login."""
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        if not username or not password or not confirm_password:
            return jsonify({'error': 'Username, password, dan konfirmasi password wajib diisi'}), 400
        if password != confirm_password:
            return jsonify({'error': 'Konfirmasi password tidak sama'}), 400
        if len(password) < 5:
            return jsonify({'error': 'Password minimal 5 karakter'}), 400

        db = Database()
        existing = db.execute_query(
            "SELECT id FROM users WHERE username = %s LIMIT 1",
            (username,),
            fetch=True
        )
        if existing:
            return jsonify({'error': 'Username sudah digunakan'}), 409

        password_hash = generate_password_hash(password)
        new_id = db.execute_query(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, password_hash, 'admin')
        )

        return jsonify({
            'success': True,
            'message': 'Pendaftaran berhasil. Silakan login.',
            'id': new_id
        }), 201
    except Exception as e:
        logger.error(f"[REGISTER ERROR] {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500


@login_bp.route('/login', methods=['POST'])
def login():
    """Endpoint untuk login admin"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body harus JSON'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username dan password wajib diisi'}), 400
        
        db = Database()
        query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
        
        try:
            user = db.execute_query(query, (username,), fetch=True)
        except Exception as db_error:
            logger.error(f"[LOGIN DB ERROR] Query failed: {str(db_error)}")
            return jsonify({'error': 'Database connection error. Hubungi administrator.'}), 500
        
        if not user:
            # Gunakan pesan generik untuk keamanan (mencegah user enumeration)
            logger.warning(f"[LOGIN] User '{username}' not found")
            return jsonify({'error': 'Username atau password salah'}), 401
        
        user = user[0]
        
        # Verifikasi password. Untuk tugas lokal, password teks biasa tetap didukung.
        is_valid = False
        try:
            is_valid = check_password_hash(user['password_hash'], password)
        except Exception as e:
            logger.warning(f"[LOGIN] Werkzeug check failed: {str(e)}. Trying plain comparison.")

        if not is_valid:
            is_valid = (user['password_hash'] == password)
            
        if not is_valid:
            logger.warning(f"[LOGIN] Password mismatch for user: {username}")
            return jsonify({'error': 'Username atau password salah'}), 401
        
        # Generate JWT Token
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(token_payload, Config.SECRET_KEY, algorithm='HS256')
        
        # Set session flags untuk keamanan cookie
        session.permanent = True
        session['token'] = token
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        logger.info(f"[LOGIN SUCCESS] User '{username}' (ID: {user['id']}) logged in")
        
        return jsonify({
            'message': 'Login berhasil',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[LOGIN ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"[LOGIN ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Terjadi kesalahan pada server. Silakan coba lagi.', 'detail': str(e)}), 500
@login_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint untuk logout"""
    # Hapus semua data session di server-side
    session.clear()
    
    response = jsonify({'message': 'Logout berhasil'})
    # Hapus cookie session browser
    response.delete_cookie('session') 
    return response, 200

@login_bp.route('/auth/check', methods=['GET'])
@token_required
def check_auth(current_user):
    """Cek status autentikasi"""
    return jsonify({
        'authenticated': True,
        'user': {
            'id': current_user,
            'username': session.get('username'),
            'role': session.get('role')
        }
    }), 200
