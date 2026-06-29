from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from Backend.admin.login import token_required
from model import Database

akun_bp = Blueprint('akun', __name__)


@akun_bp.route('/akun', methods=['GET'])
@token_required
def get_akun(current_user):
    try:
        db = Database()
        query = "SELECT id, username, role, created_at FROM users WHERE id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)

        if not result:
            return jsonify({'error': 'Akun tidak ditemukan'}), 404

        return jsonify({'success': True, 'data': result[0]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@akun_bp.route('/akun', methods=['PUT'])
@token_required
def update_akun(current_user):
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()

        if not username:
            return jsonify({'error': 'Username wajib diisi'}), 400

        db = Database()
        duplicate_query = "SELECT id FROM users WHERE username = %s AND id != %s"
        duplicate = db.execute_query(duplicate_query, (username, current_user), fetch=True)
        if duplicate:
            return jsonify({'error': 'Username sudah digunakan'}), 409

        db.execute_query("UPDATE users SET username = %s WHERE id = %s", (username, current_user))
        return jsonify({'success': True, 'message': 'Akun berhasil diperbarui'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@akun_bp.route('/akun/create', methods=['POST'])
@token_required
def create_akun(current_user):
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'admin').strip() or 'admin'

        if not username or not password:
            return jsonify({'error': 'Username dan password wajib diisi'}), 400
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
            (username, password_hash, role)
        )

        return jsonify({
            'success': True,
            'message': 'Akun berhasil dibuat',
            'id': new_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@akun_bp.route('/akun/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        data = request.get_json() or {}
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')

        if not old_password or not new_password:
            return jsonify({'error': 'Password lama dan baru wajib diisi'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'Password baru minimal 6 karakter'}), 400

        db = Database()
        result = db.execute_query(
            "SELECT password_hash FROM users WHERE id = %s",
            (current_user,),
            fetch=True
        )

        if not result:
            return jsonify({'error': 'Akun tidak ditemukan'}), 404

        stored_hash = result[0]['password_hash']
        if not check_password_hash(stored_hash, old_password) and stored_hash != old_password:
            return jsonify({'error': 'Password lama salah'}), 401

        new_hash = generate_password_hash(new_password)
        db.execute_query("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, current_user))
        return jsonify({'success': True, 'message': 'Password berhasil diganti'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
