import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from Backend.admin.akun import akun_bp
from Backend.admin.dashboard import dashboard_bp
from Backend.admin.experience import experience_bp
from Backend.admin.login import login_bp
from Backend.admin.profiles import profiles_bp
from Backend.admin.projects import projects_bp
from Backend.admin.skills import skills_bp
from Backend.admin.upload import upload_bp
from Backend.profil.profil import profil_bp
from config import Config


API_PREFIX = '/api'


def create_app():
    app = Flask(
        __name__,
        static_folder='Frontend',
        template_folder='.'
    )
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    register_blueprints(app)
    register_frontend_routes(app)
    register_error_handlers(app)

    return app


def register_blueprints(app):
    blueprints = (
        akun_bp,
        dashboard_bp,
        experience_bp,
        login_bp,
        profiles_bp,
        profil_bp,
        projects_bp,
        skills_bp,
        upload_bp,
    )

    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix=API_PREFIX)


def register_frontend_routes(app):
    def send_index():
        root_index = os.path.join(app.root_path, 'index.html')
        frontend_index = os.path.join(app.root_path, 'Frontend', 'index.html')

        if os.path.exists(root_index):
            return send_from_directory(app.root_path, 'index.html')
        if os.path.exists(frontend_index):
            return send_from_directory(os.path.join(app.root_path, 'Frontend'), 'index.html')

        return 'Error: index.html tidak ditemukan', 404

    @app.route('/')
    @app.route('/index.html')
    def index():
        return send_index()

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        return send_from_directory(os.path.join(app.root_path, 'Frontend', 'admin'), filename)

    @app.route('/profil/<path:filename>')
    def profil_pages(filename):
        return send_from_directory(os.path.join(app.root_path, 'Frontend', 'profil'), filename)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            app.root_path,
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith(f'{API_PREFIX}/'):
            return jsonify({'error': 'Route tidak ditemukan'}), 404

        if request.accept_mimetypes.best == 'text/html':
            index_path = os.path.join(app.root_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(app.root_path, 'index.html')

        return jsonify({'error': 'Route tidak ditemukan'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500


if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
