import os
import logging
from logging.handlers import RotatingFileHandler
import colorama
from colorama import Fore, Back, Style
import atexit

colorama.init()

class ColoredFormatter(logging.Formatter):
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
    LOG_FOLDER = os.path.join(os.path.abspath("."), 'logs')
    os.makedirs(LOG_FOLDER, exist_ok=True)
    LOG_FILE = os.path.join(LOG_FOLDER, 'uif_generator.log')

    logger = logging.getLogger('UIF_Generator')
    logger.setLevel(logging.INFO)

    # Configuración para archivo con rotación
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5*1024*1024,  # 5MB
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

    return logger

logger = setup_logger()