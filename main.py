import os
import sys
import threading
import webbrowser
import time
import socket
import signal
import atexit
from app_factory import create_app
from routes.api_routes import configure_routes
from utils.logger import logger


class ServerControl:
    """Clase para controlar el estado del servidor"""
    _instance = None
    server_running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServerControl, cls).__new__(cls)
            cls._instance.server_running = True
        return cls._instance

    @classmethod
    def stop_server(cls):
        if cls._instance is not None:
            cls._instance.server_running = False

    @property
    def instance(self):
        return self._instance


def check_port_available():
    """Verifica si el puerto está disponible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.bind(("127.0.0.1", 5000))
        sock.close()
        return True
    except socket.error as e:
        logger.error(f"Error al verificar el puerto: {str(e)}")
        return False


def open_browser():
    """Abre el navegador después de asegurar que el servidor esté listo"""
    time.sleep(1.5)
    webbrowser.open_new('http://127.0.0.1:5000')


def signal_handler(sig, frame):
    """Manejador de señales para Ctrl+C y terminación del sistema"""
    logger.info("Recibida señal de terminación, apagando servidor...")
    try:
        ServerControl.stop_server()
        import requests
        requests.post('http://127.0.0.1:5000/shutdown', timeout=1)
    except Exception as e:
        logger.warning(f"No se pudo apagar limpiamente: {str(e)}")
    finally:
        sys.exit(0)


def cleanup_resources():
    """Limpia recursos antes de salir"""
    try:
        if ServerControl.instance is not None:
            logger.info("Limpiando recursos antes de salir...")
            ServerControl.stop_server()
    except Exception as e:
        # Ignorar errores durante la terminación
        pass


def main():
    """Función principal de la aplicación"""
    logger.info("Iniciando aplicación XmlCreator40")

    # Verificar disponibilidad del puerto
    if not check_port_available():
        logger.error("¡Error! Ya hay una instancia del servidor en ejecución.")
        sys.exit(1)

    # Crear instancia de control primero
    server_control = ServerControl()

    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_resources)

    # Crear aplicación Flask
    app = create_app()
    configure_routes(app)

    # Modo CLI
    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        logger.info("Modo CLI activado")
        # [Mantener toda la lógica CLI existente]
        pass
    else:
        # Modo GUI
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()

        # Iniciar servidor Flask
        try:
            logger.info("Iniciando servidor Flask...")
            app.run(
                host='127.0.0.1',
                port=5000,
                debug=True,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Error en el servidor: {str(e)}")
            sys.exit(1)
        finally:
            cleanup_resources()
            logger.info("Servidor detenido")


if __name__ == '__main__':
    main()
