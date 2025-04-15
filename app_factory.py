import os
from flask import Flask
from config.settings import configure_app


def create_app():
    """Factory principal para crear la aplicación Flask"""
    app = Flask(__name__)

    # Configuración básica
    configure_app(app)

    # Configuración de carpetas
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # Asegurar que las carpetas existan
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app