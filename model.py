import logging
import os
import sqlite3
import time

import mysql.connector
from mysql.connector import pooling

from config import Config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Database:
    _instance = None
    _pool = None
    _sqlite_ready = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if Config.DB_DRIVER not in ('sqlite', 'mysql'):
            raise ValueError("DB_DRIVER harus 'sqlite' atau 'mysql'")

        if Config.DB_DRIVER == 'mysql' and self._pool is None:
            missing = [
                name for name, value in {
                    'DB_HOST': Config.DB_HOST,
                    'DB_USER': Config.DB_USER,
                    'DB_PASSWORD': Config.DB_PASSWORD,
                    'DB_NAME': Config.DB_NAME,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"Konfigurasi MySQL belum lengkap: {', '.join(missing)}")

            self._pool = pooling.MySQLConnectionPool(
                pool_name="portfolio_pool",
                pool_size=5,
                pool_reset_session=True,
                **Config.MYSQL_CONFIG
            )
            self._init_mysql()
        elif Config.DB_DRIVER == 'sqlite' and not self._sqlite_ready:
            self._init_sqlite()
            Database._sqlite_ready = True

    def get_connection(self):
        if Config.DB_DRIVER == 'mysql':
            return self._pool.get_connection()

        os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, query, params=None, fetch=False):
        """Menjalankan query untuk MySQL atau SQLite."""
        start_time = time.time()
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True) if Config.DB_DRIVER == 'mysql' else conn.cursor()
        query_to_run = self._normalize_query(query)

        try:
            cursor.execute(query_to_run, params or ())
            if fetch:
                rows = cursor.fetchall()
                result = [dict(row) for row in rows]
            else:
                conn.commit()
                result = cursor.lastrowid if cursor.lastrowid else True

            elapsed = time.time() - start_time
            logger.debug("Query executed in %.3fs: %s...", elapsed, query.strip()[:50])
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def _normalize_query(self, query):
        if Config.DB_DRIVER == 'sqlite':
            return query.replace('%s', '?')
        return query

    def _init_sqlite(self):
        os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nama_lengkap TEXT,
                    nama_panggilan TEXT,
                    tempat_lahir TEXT,
                    tanggal_lahir TEXT,
                    email TEXT,
                    telepon TEXT,
                    universitas TEXT,
                    fakultas TEXT,
                    prodi TEXT,
                    semester TEXT,
                    alamat TEXT,
                    foto_url TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    posisi TEXT NOT NULL,
                    perusahaan TEXT NOT NULL,
                    durasi TEXT NOT NULL,
                    deskripsi TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    judul TEXT NOT NULL,
                    deskripsi TEXT NOT NULL,
                    gambar_url TEXT,
                    link_project TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    nama_skill TEXT NOT NULL,
                    icon_class TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                INSERT INTO users (username, password_hash, role)
                VALUES ('admin', 'admin', 'admin')
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    role = excluded.role;

                INSERT INTO users (username, password_hash, role)
                VALUES ('Evert', 'admin', 'admin')
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    role = excluded.role;

                INSERT INTO profiles (
                    user_id, nama_lengkap, nama_panggilan, email, telepon,
                    universitas, fakultas, prodi, semester, alamat, foto_url
                )
                SELECT 1, 'Nama Lengkap Anda', 'Admin', 'admin@example.com',
                    '08xxxxxxxxxx', 'Nama Universitas', 'Nama Fakultas',
                    'Program Studi', '1', 'Alamat Anda', ''
                WHERE NOT EXISTS (SELECT 1 FROM profiles WHERE user_id = 1);

                INSERT INTO skills (user_id, nama_skill, icon_class)
                SELECT 1, 'Python', 'fab fa-python'
                WHERE NOT EXISTS (SELECT 1 FROM skills WHERE nama_skill = 'Python');

                INSERT INTO skills (user_id, nama_skill, icon_class)
                SELECT 1, 'Flask', 'fas fa-server'
                WHERE NOT EXISTS (SELECT 1 FROM skills WHERE nama_skill = 'Flask');

                INSERT INTO skills (user_id, nama_skill, icon_class)
                SELECT 1, 'MySQL', 'fas fa-database'
                WHERE NOT EXISTS (SELECT 1 FROM skills WHERE nama_skill = 'MySQL');

                INSERT INTO projects (user_id, judul, deskripsi, gambar_url, link_project)
                SELECT 1, 'Website Portofolio',
                    'Project portofolio yang bisa dikelola dari halaman admin.',
                    '', ''
                WHERE NOT EXISTS (SELECT 1 FROM projects WHERE judul = 'Website Portofolio');

                INSERT INTO experiences (user_id, posisi, perusahaan, durasi, deskripsi)
                SELECT 1, 'Mahasiswa', 'Nama Kampus', '2024 - Sekarang',
                    'Contoh pengalaman awal. Silakan ubah dari halaman admin.'
                WHERE NOT EXISTS (SELECT 1 FROM experiences WHERE posisi = 'Mahasiswa');
            """)
            conn.commit()
        finally:
            conn.close()

    def _init_mysql(self):
        statements = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(30) NOT NULL DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                nama_lengkap VARCHAR(150),
                nama_panggilan VARCHAR(100),
                tempat_lahir VARCHAR(100),
                tanggal_lahir DATE,
                email VARCHAR(150),
                telepon VARCHAR(50),
                universitas VARCHAR(150),
                fakultas VARCHAR(150),
                prodi VARCHAR(150),
                semester VARCHAR(20),
                alamat TEXT,
                foto_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_profiles_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS experiences (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                posisi VARCHAR(150) NOT NULL,
                perusahaan VARCHAR(150) NOT NULL,
                durasi VARCHAR(100) NOT NULL,
                deskripsi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_experiences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                judul VARCHAR(150) NOT NULL,
                deskripsi TEXT NOT NULL,
                gambar_url TEXT,
                link_project TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_projects_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS skills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                nama_skill VARCHAR(120) NOT NULL,
                icon_class VARCHAR(120),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_skills_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            """
            INSERT INTO users (username, password_hash, role)
            VALUES ('admin', 'admin', 'admin')
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                role = VALUES(role)
            """,
            """
            INSERT INTO users (username, password_hash, role)
            VALUES ('Evert', 'admin', 'admin')
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                role = VALUES(role)
            """,
            """
            INSERT INTO profiles (
                user_id, nama_lengkap, nama_panggilan, email, telepon,
                universitas, fakultas, prodi, semester, alamat, foto_url
            )
            SELECT 1, 'Nama Lengkap Anda', 'Admin', 'admin@example.com',
                '08xxxxxxxxxx', 'Nama Universitas', 'Nama Fakultas',
                'Program Studi', '1', 'Alamat Anda', ''
            WHERE NOT EXISTS (SELECT 1 FROM profiles WHERE user_id = 1)
            """,
            """
            INSERT INTO skills (user_id, nama_skill, icon_class)
            SELECT 1, 'Python', 'fab fa-python'
            WHERE NOT EXISTS (SELECT 1 FROM skills WHERE user_id = 1 AND nama_skill = 'Python')
            """,
            """
            INSERT INTO skills (user_id, nama_skill, icon_class)
            SELECT 1, 'Flask', 'fas fa-server'
            WHERE NOT EXISTS (SELECT 1 FROM skills WHERE user_id = 1 AND nama_skill = 'Flask')
            """,
            """
            INSERT INTO skills (user_id, nama_skill, icon_class)
            SELECT 1, 'MySQL', 'fas fa-database'
            WHERE NOT EXISTS (SELECT 1 FROM skills WHERE user_id = 1 AND nama_skill = 'MySQL')
            """,
            """
            INSERT INTO projects (user_id, judul, deskripsi, gambar_url, link_project)
            SELECT 1, 'Website Portofolio',
                'Project portofolio yang bisa dikelola dari halaman admin.',
                '', ''
            WHERE NOT EXISTS (SELECT 1 FROM projects WHERE user_id = 1 AND judul = 'Website Portofolio')
            """,
            """
            INSERT INTO experiences (user_id, posisi, perusahaan, durasi, deskripsi)
            SELECT 1, 'Mahasiswa', 'Nama Kampus', '2024 - Sekarang',
                'Contoh pengalaman awal. Silakan ubah dari halaman admin.'
            WHERE NOT EXISTS (SELECT 1 FROM experiences WHERE user_id = 1 AND posisi = 'Mahasiswa')
            """
        ]

        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            for statement in statements:
                cursor.execute(statement)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
