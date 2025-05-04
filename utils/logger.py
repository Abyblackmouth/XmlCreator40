import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import colorama
from colorama import Fore, Back, Style
import atexit
from pathlib import Path

# Inicialización de colorama
colorama.init()


def get_app_path():
    """Obtiene la ruta correcta para los archivos según si es ejecutable o desarrollo"""
    try:
        # PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return Path(base_path)


def get_appdata_path():
    """Obtiene la ruta en AppData para almacenamiento persistente"""
    appdata = os.getenv('APPDATA')
    if not appdata:
        appdata = os.path.expanduser('~')  # Fallback para sistemas sin APPDATA
    return Path(appdata) / "XmlCreator40"


class ColoredFormatter(logging.Formatter):
    """Formateador personalizado para logs con colores"""
    FORMATS = {
        logging.DEBUG: Fore.CYAN + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Back.WHITE + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def close_handlers():
    """Cierra todos los handlers de logging al salir"""
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def setup_logger():
    """Configura el sistema de logging completo"""
    try:
        # Ruta para logs (AppData para persistencia entre ejecuciones)
        log_dir = get_appdata_path() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'uif_generator.log'

        # Ruta alternativa temporal si falla AppData
        if not log_dir.exists():
            temp_dir = Path(os.getenv('TEMP', '.')) / "XmlCreator40_logs"
            temp_dir.mkdir(exist_ok=True)
            log_file = temp_dir / 'uif_generator.log'

        logger = logging.getLogger('UIF_Generator')
        logger.setLevel(logging.INFO)

        # Configuración para archivo con rotación
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Configuración para consola con colores
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter())

        # Limpiar handlers existentes
        if logger.hasHandlers():
            logger.handlers.clear()

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Registrar cierre de handlers al terminar
        atexit.register(close_handlers)

        logger.info(f"Directorio de logs: {log_file.parent}")
        return logger

    except Exception as e:
        # Fallback básico si todo falla
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('UIF_Generator_Fallback')
        logger.error(f"Error configurando logger: {str(e)}. Usando configuración básica.")
        return logger


# Logger global
logger = setup_logger()