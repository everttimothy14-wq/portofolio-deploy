from flask import Blueprint, request, jsonify
from model import Database
from Backend.admin.login import get_current_user_id, token_required

# Inisialisasi Blueprint
experience_bp = Blueprint('experience', __name__)

# ✅ PERBAIKAN: Hapus '/api' di depan route
@experience_bp.route('/experiences', methods=['GET'])
def get_experiences():
    """Mengambil semua experiences (publik)"""
    try:
        db = Database()
        current_user = get_current_user_id(optional=True)

        if current_user:
            query = """
                SELECT e.*, u.username
                FROM experiences e
                JOIN users u ON e.user_id = u.id
                WHERE e.user_id = %s
                ORDER BY e.created_at DESC
            """
            result = db.execute_query(query, (current_user,), fetch=True)
        else:
            query = """
                SELECT e.*, u.username
                FROM experiences e
                JOIN users u ON e.user_id = u.id
                WHERE u.role = 'admin'
                ORDER BY e.created_at DESC
            """
            result = db.execute_query(query, fetch=True)
        
        return jsonify({
            'success': True,
            'data': result if result else []
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@experience_bp.route('/experiences/<int:id>', methods=['GET'])
def get_experience_by_id(id):
    """Mengambil satu experience berdasarkan ID"""
    try:
        db = Database()
        
        query = "SELECT * FROM experiences WHERE id = %s"
        result = db.execute_query(query, (id,), fetch=True)
        
        if not result:
            return jsonify({'error': 'Experience tidak ditemukan'}), 404
        
        return jsonify({
            'success': True,
            'data': result[0]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@experience_bp.route('/experiences', methods=['POST'])
@token_required
def create_experience(current_user):
    """Create experience baru (Admin Only)"""
    try:
        data = request.get_json()
        
        required_fields = ['posisi', 'perusahaan', 'durasi']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} wajib diisi'}), 400
        
        db = Database()
        
        query = """
            INSERT INTO experiences (user_id, posisi, perusahaan, durasi, deskripsi)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            current_user,
            data.get('posisi'),
            data.get('perusahaan'),
            data.get('durasi'),
            data.get('deskripsi')
        )
        
        new_id = db.execute_query(query, values)
        
        return jsonify({
            'success': True,
            'message': 'Experience berhasil dibuat',
            'id': new_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@experience_bp.route('/experiences/<int:id>', methods=['PUT'])
@token_required
def update_experience(current_user, id):
    """Update experience (Admin Only)"""
    try:
        data = request.get_json()
        
        db = Database()
        
        # Keamanan: Pastikan user hanya bisa edit miliknya sendiri
        check_query = "SELECT id FROM experiences WHERE id = %s AND user_id = %s"
        existing = db.execute_query(check_query, (id, current_user), fetch=True)
        
        if not existing:
            return jsonify({'error': 'Experience tidak ditemukan atau bukan milik Anda'}), 404
        
        allowed_fields = ['posisi', 'perusahaan', 'durasi', 'deskripsi']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])
        
        if not updates:
            return jsonify({'error': 'Tidak ada data yang diupdate'}), 400
        
        values.append(id)
        query = f"UPDATE experiences SET {', '.join(updates)} WHERE id = %s"
        db.execute_query(query, tuple(values))
        
        return jsonify({
            'success': True,
            'message': 'Experience berhasil diupdate'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@experience_bp.route('/experiences/<int:id>', methods=['DELETE'])
@token_required
def delete_experience(current_user, id):
    """Delete experience (Admin Only)"""
    try:
        db = Database()
        
        # Keamanan: Pastikan user hanya bisa hapus miliknya sendiri
        check_query = "SELECT id FROM experiences WHERE id = %s AND user_id = %s"
        existing = db.execute_query(check_query, (id, current_user), fetch=True)
        
        if not existing:
            return jsonify({'error': 'Experience tidak ditemukan atau bukan milik Anda'}), 404
        
        query = "DELETE FROM experiences WHERE id = %s"
        db.execute_query(query, (id,))
        
        return jsonify({
            'success': True,
            'message': 'Experience berhasil dihapus'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
