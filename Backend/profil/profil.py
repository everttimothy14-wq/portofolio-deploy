import datetime
import os
import logging
from flask import Blueprint, jsonify, request

from Backend.admin.login import token_required
from config import Config
from model import Database

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
logger = logging.getLogger(__name__)

profil_bp = Blueprint('profil', __name__)

PROFILE_FIELDS = [
    'nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'tanggal_lahir',
    'email', 'telepon', 'universitas', 'fakultas', 'prodi',
    'semester', 'alamat', 'foto_url'
]

FALLBACK_PROFILE = {
    'nama_lengkap': 'Evert Tito Timothy Tomasoa',
    'nama_panggilan': 'Evert',
    'tempat_lahir': 'Ambon',
    'tanggal_lahir': '14/05/2007',
    'email': 'everttimothy14@gmail.com',
    'telepon': '08xxxxxxxxxx',
    'universitas': 'Universitas Kristen Satya Wacana',
    'fakultas': 'Fakultas Teknologi Informasi',
    'prodi': 'Sistem Informasi',
    'semester': '4',
    'alamat': 'Jln. Kh Isom No, 185, RT 02/RW 05, Sidorejo Lor.',
    'foto_url': 'https://res.cloudinary.com/dhikaandhika/image/upload/v1696461870/portfolio/placeholder-profile.png',
    'skills': [
        {'nama_skill': 'Python', 'icon_class': 'fab fa-python'},
        {'nama_skill': 'Flask', 'icon_class': 'fas fa-server'},
        {'nama_skill': 'MySQL', 'icon_class': 'fas fa-database'}
    ],
    'experiences': [
        {
            'posisi': 'Mahasiswa',
            'perusahaan': 'Nama Kampus',
            'durasi': '2024 - Sekarang',
            'deskripsi': 'Contoh pengalaman akan diganti setelah database berhasil terhubung.'
        }
    ],
    'projects': [
        {
            'judul': 'Website Portofolio',
            'deskripsi': 'Contoh project portofolio. Data asli akan muncul setelah database terhubung.',
            'gambar_url': '',
            'link_project': ''
        }
    ]
}


def _clean_text(value):
    if value is None:
        return ''
    return str(value).strip()


def _profile_payload(data):
    return {field: _clean_text(data.get(field)) for field in PROFILE_FIELDS}


def _merge_with_fallback(profile):
    merged = FALLBACK_PROFILE.copy()
    for field in PROFILE_FIELDS:
        value = profile.get(field)
        if value is not None and value != '':
            merged[field] = value
    if profile.get('id') is not None:
        merged['id'] = profile['id']
    if profile.get('user_id') is not None:
        merged['user_id'] = profile['user_id']
    return merged


def _get_portfolio_user_id(db):
    if Config.PORTFOLIO_USER_ID:
        result = db.execute_query(
            "SELECT id FROM users WHERE id = %s LIMIT 1",
            (Config.PORTFOLIO_USER_ID,),
            fetch=True
        )
        if result:
            return result[0]['id']

    if Config.PORTFOLIO_USERNAME:
        result = db.execute_query(
            "SELECT id FROM users WHERE username = %s LIMIT 1",
            (Config.PORTFOLIO_USERNAME,),
            fetch=True
        )
        if result:
            return result[0]['id']

    query = """
        SELECT u.id
        FROM users u
        LEFT JOIN profiles p ON p.user_id = u.id
        LEFT JOIN (
            SELECT user_id, MAX(created_at) AS latest_at
            FROM projects
            GROUP BY user_id
        ) pr ON pr.user_id = u.id
        LEFT JOIN (
            SELECT user_id, MAX(created_at) AS latest_at
            FROM experiences
            GROUP BY user_id
        ) ex ON ex.user_id = u.id
        LEFT JOIN (
            SELECT user_id, MAX(created_at) AS latest_at
            FROM skills
            GROUP BY user_id
        ) sk ON sk.user_id = u.id
        WHERE u.role = 'admin'
        ORDER BY
            CASE
                WHEN p.id IS NOT NULL OR pr.latest_at IS NOT NULL OR ex.latest_at IS NOT NULL OR sk.latest_at IS NOT NULL
                THEN 1
                ELSE 0
            END DESC,
            COALESCE(p.updated_at, p.created_at, pr.latest_at, ex.latest_at, sk.latest_at, u.created_at) DESC,
            u.id DESC
        LIMIT 1
    """
    result = db.execute_query(query, fetch=True)
    return result[0]['id'] if result else None


def _get_public_profile(db, user_id):
    if not user_id:
        return FALLBACK_PROFILE.copy()

    result = db.execute_query(
        "SELECT * FROM profiles WHERE user_id = %s LIMIT 1",
        (user_id,),
        fetch=True
    )
    if result:
        return _merge_with_fallback(result[0])

    user = db.execute_query(
        """
        SELECT id AS user_id, username AS nama_lengkap, username AS nama_panggilan
        FROM users
        WHERE id = %s
        LIMIT 1
        """,
        (user_id,),
        fetch=True
    )
    return _merge_with_fallback(user[0]) if user else FALLBACK_PROFILE.copy()


def _get_user_items(db, table, user_id, order_by):
    if not user_id:
        return []

    return db.execute_query(
        f"SELECT * FROM {table} WHERE user_id = %s ORDER BY {order_by}",
        (user_id,),
        fetch=True
    ) or []


@profil_bp.route('/profil', methods=['GET'])
def get_profil_public():
    try:
        db = Database()
        user_id = _get_portfolio_user_id(db)
        return jsonify({
            'success': True,
            'data': _get_public_profile(db, user_id)
        }), 200
    except Exception as e:
        return jsonify({
            'success': True,
            'data': FALLBACK_PROFILE.copy(),
            'warning': f'Database belum terhubung: {str(e)}'
        }), 200


@profil_bp.route('/main-profile', methods=['GET'])
def get_main_profile():
    try:
        db = Database()
        user_id = _get_portfolio_user_id(db)
        profile = _get_public_profile(db, user_id)

        profile['skills'] = _get_user_items(db, 'skills', user_id, 'id DESC')
        profile['experiences'] = _get_user_items(db, 'experiences', user_id, 'created_at DESC')
        profile['projects'] = _get_user_items(db, 'projects', user_id, 'created_at DESC')

        if not profile['skills']:
            profile['skills'] = FALLBACK_PROFILE['skills']
        if not profile['experiences']:
            profile['experiences'] = FALLBACK_PROFILE['experiences']
        if not profile['projects']:
            profile['projects'] = FALLBACK_PROFILE['projects']

        return jsonify({'success': True, 'data': profile}), 200
    except Exception as e:
        return jsonify({
            'success': True,
            'data': FALLBACK_PROFILE.copy(),
            'warning': f'Database belum terhubung: {str(e)}'
        }), 200


@profil_bp.route('/contact', methods=['POST'])
def contact():
    data = request.get_json() or {}
    name = _clean_text(data.get('name'))
    email = _clean_text(data.get('email'))
    message = _clean_text(data.get('message'))

    if not name or not email or not message:
        return jsonify({'error': 'Nama, email, dan pesan wajib diisi'}), 400

    if not Config.RESEND_API_KEY:
        try:
            log_path = os.path.join(ROOT_DIR, 'contact_messages.log')
            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(
                    f"[{datetime.datetime.utcnow().isoformat()}] {name} <{email}>\n{message}\n---\n"
                )
            logger.warning('Resend API key tidak dikonfigurasi. Pesan kontak disimpan ke %s', log_path)
        except Exception as exc:
            logger.error('Tidak dapat menyimpan pesan kontak: %s', exc)

        return jsonify({
            'success': True,
            'message': 'Pesan berhasil diterima, tetapi email belum dikirim karena Resend API key belum dikonfigurasi.'
        }), 200

    try:
        import resend
        from resend import Emails
    except Exception as exc:
        logger.error('Library email tidak tersedia: %s', exc)
        return jsonify({'error': f'Library email tidak tersedia: {str(exc)}'}), 500

    resend.api_key = Config.RESEND_API_KEY

    recipient = Config.CONTACT_RECIPIENT_EMAIL
    if not recipient:
        return jsonify({'error': 'Alamat email penerima belum dikonfigurasi'}), 500

    sender = Config.RESEND_FROM_EMAIL
    if not sender or '@' not in sender:
        sender = f'noreply@{recipient.split("@")[-1]}'

    subject = f'Pesan Portofolio dari {name}'
    text_body = (
        f'Nama: {name}\n'
        f'Email: {email}\n\n'
        f'Pesan:\n{message}\n'
    )
    html_body = (
        f'<p><strong>Nama:</strong> {name}</p>'
        f'<p><strong>Email:</strong> {email}</p>'
        f'<p><strong>Pesan:</strong></p>'
        f'<p>{message.replace("\n", "<br />")}</p>'
    )

    try:
        Emails.send({
            'from': sender,
            'to': recipient,
            'subject': subject,
            'text': text_body,
            'html': html_body,
        })
    except Exception as exc:
        logger.error('Gagal mengirim email Resend: %s', exc)
        try:
            log_path = os.path.join(ROOT_DIR, 'contact_messages.log')
            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(
                    f"[{datetime.datetime.utcnow().isoformat()}] {name} <{email}>\n{message}\n---\n"
                )
            logger.warning('Email gagal dikirim; pesan kontak disimpan ke %s', log_path)
        except Exception as log_exc:
            logger.error('Tidak dapat menyimpan pesan kontak setelah kegagalan email: %s', log_exc)

        return jsonify({'error': f'Gagal mengirim email: {str(exc)}'}), 500

    return jsonify({
        'success': True,
        'message': 'Pesan berhasil dikirim via email'
    }), 200
