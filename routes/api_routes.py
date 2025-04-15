from flask import render_template, request, flash, redirect, url_for, send_from_directory, current_app, make_response
from werkzeug.utils import secure_filename
import os
from utils.logger import logger
from services.xml_generator import generar_xml_uif
from flask import request, jsonify


def configure_routes(app):
    """Configura todas las rutas de la aplicación Flask"""

    @app.route('/')
    def index():
        logger.info("Acceso a página principal")
        # Usar make_response para crear un objeto Response configurable
        response = make_response(render_template('upload.html', show_template_button=True))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        """Endpoint para apagar el servidor de forma controlada"""
        if not app.config.get('SHUTDOWN_ENABLED', False):
            return jsonify({'status': 'error', 'message': 'Shutdown not allowed'}), 403

        logger.info("Recibida solicitud de apagado del servidor")
        shutdown_func = request.environ.get('werkzeug.server.shutdown')
        if shutdown_func is None:
            logger.error("No se puede apagar el servidor: no está en modo desarrollo")
            return jsonify({'status': 'error', 'message': 'Server cannot be shut down'}), 500

        shutdown_func()
        return jsonify({'status': 'success', 'message': 'Server shutting down...'})

    @app.route('/download-template')
    def download_template():
        try:
            logger.info("Solicitud de descarga de plantilla")
            template_path = os.path.join(app.root_path, 'resources', 'datos.xlsx')

            if not os.path.exists(template_path):
                logger.error("Plantilla no encontrada en: " + template_path)
                flash('Plantilla no disponible', 'error')
                return redirect(url_for('index'))

            logger.info("Enviando plantilla al cliente")
            return send_from_directory(
                directory=os.path.join(app.root_path, 'resources'),
                path='datos.xlsx',
                as_attachment=True,
                download_name='plantilla_UIF.xlsx'
            )
        except Exception as e:
            logger.error(f"Error al descargar plantilla: {str(e)}", exc_info=True)
            flash('Error al descargar la plantilla', 'error')
            return redirect(url_for('index'))

    @app.route('/', methods=['POST'])
    def upload_file():
        try:
            if 'file' not in request.files:
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(request.url)

            file = request.files['file']
            if file.filename == '':
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(request.url)

            if file and file.filename.lower().endswith('.xlsx'):
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                filepath = os.path.join(upload_folder, filename)

                os.makedirs(upload_folder, exist_ok=True)
                file.save(filepath)

                logger.info(f"Procesando archivo: {filename}")
                xml_path, error = generar_xml_uif(filepath, upload_folder)

                if error:
                    flash(error, 'error')  # Muestra el mensaje de error específico
                    logger.error(error)
                else:
                    logger.info(f"XML generado exitosamente: {xml_path}")
                    return render_template('result.html', xml_file=os.path.basename(xml_path))

            flash('Solo se permiten archivos Excel (.xlsx)', 'error')
            return redirect(url_for('index'))

        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            flash('Ocurrió un error al procesar el archivo', 'error')
            return redirect(url_for('index'))

    @app.route('/download/<filename>')
    def download(filename):
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            filepath = os.path.join(upload_folder, filename)

            if not os.path.exists(filepath):
                logger.error(f"Archivo no encontrado: {filename}")
                flash('El archivo solicitado no existe', 'error')
                return redirect(url_for('index'))

            return send_from_directory(
                directory=upload_folder,
                path=filename,
                as_attachment=True,
                download_name=filename
            )
        except Exception as e:
            logger.error(f"Error al descargar: {str(e)}", exc_info=True)
            flash('Error al descargar el archivo', 'error')
            return redirect(url_for('index'))