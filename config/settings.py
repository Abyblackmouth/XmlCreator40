import os


def configure_app(app):
    """Configuración de la aplicación Flask"""
    # Configuración de seguridad
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave-secreta-para-desarrollo')

    # Configuración de sesión
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Configuración adicional
    app.config['TEMPLATES_AUTO_RELOAD'] = True