import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from utils.logger import logger


def generar_xml_uif(archivo_excel, upload_folder):
    hojas_requeridas = ['encabezado', 'persona_moral', 'operaciones']


    try:
        # Validación básica del archivo
        if not os.path.isfile(archivo_excel):
            error_msg = "El archivo no existe o no es válido"
            logger.error(f"XML no generado - {error_msg}")
            return None, error_msg

        # Validación de hojas
        xls = pd.ExcelFile(archivo_excel)
        hojas_faltantes = [h for h in hojas_requeridas if h not in xls.sheet_names]
        if hojas_faltantes:
            error_msg = f"Faltan hojas requeridas: {', '.join(hojas_faltantes)}"
            logger.error(f"XML no generado - {error_msg}")
            logger.info("_" * 120)
            return None, error_msg

        # Lectura de datos
        logger.info("Leyendo hoja 'encabezado'")
        encabezado_df = pd.read_excel(xls, 'encabezado')
        logger.info("Leyendo hoja 'persona_moral'")
        persona_df = pd.read_excel(xls, 'persona_moral')
        logger.info("Leyendo hoja 'operaciones'")
        operaciones_df = pd.read_excel(xls, 'operaciones')

        # Preparación de nombre de archivo de salida
        denominacion = persona_df.iloc[0]['denominacion_razon'].replace(' ', '_').replace('.', '')[:30]
        mes_reportado = str(encabezado_df.iloc[0]['mes_reportado'])
        xml_salida = f"informe1.0_{denominacion}_{mes_reportado}.xml"
        xml_salida = os.path.join(upload_folder, xml_salida)

        logger.info(f"Archivo de salida generado: {xml_salida}")
        logger.info("Creando estructura XML base")

        # Creación de estructura XML
        ET.register_namespace('', "http://www.uif.shcp.gob.mx/recepcion/tcv")
        root = ET.Element("{http://www.uif.shcp.gob.mx/recepcion/tcv}archivo")
        root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                 "http://www.uif.shcp.gob.mx/recepcion/tcv tcv.xsd")

        # Sección de informe
        informe = ET.SubElement(root, "informe")
        ET.SubElement(informe, "mes_reportado").text = mes_reportado
        logger.info(f"Mes reportado: {mes_reportado}")

        # Sección de sujeto obligado
        sujeto = ET.SubElement(informe, "sujeto_obligado")
        clave_sujeto = str(encabezado_df.iloc[0]['clave_sujeto_obligado'])
        clave_actividad = str(encabezado_df.iloc[0]['clave_actividad'])
        ET.SubElement(sujeto, "clave_sujeto_obligado").text = clave_sujeto
        ET.SubElement(sujeto, "clave_actividad").text = clave_actividad
        logger.info(f"Clave sujeto: {clave_sujeto}, Actividad: {clave_actividad}")

        # Sección de aviso
        aviso = ET.SubElement(informe, "aviso")
        referencia = str(encabezado_df.iloc[0]['referencia_aviso'])
        prioridad = str(encabezado_df.iloc[0]['prioridad'])
        ET.SubElement(aviso, "referencia_aviso").text = referencia
        ET.SubElement(aviso, "prioridad").text = prioridad
        logger.info(f"Referencia aviso: {referencia}, Prioridad: {prioridad}")

        # Sección de alerta
        alerta = ET.SubElement(aviso, "alerta")
        tipo_alerta = str(encabezado_df.iloc[0]['tipo_alerta'])
        ET.SubElement(alerta, "tipo_alerta").text = tipo_alerta
        logger.info(f"Tipo alerta: {tipo_alerta}")

        # Sección de persona aviso
        persona_aviso = ET.SubElement(aviso, "persona_aviso")
        tipo_persona = ET.SubElement(persona_aviso, "tipo_persona")
        persona_moral = ET.SubElement(tipo_persona, "persona_moral")

        # Datos de persona moral
        datos_persona = {
            'denominacion_razon': persona_df.iloc[0]['denominacion_razon'],
            'fecha_constitucion': persona_df.iloc[0]['fecha_constitucion'],
            'rfc': persona_df.iloc[0]['rfc'],
            'pais_nacionalidad': persona_df.iloc[0]['pais_nacionalidad'],
            'giro_mercantil': persona_df.iloc[0]['giro_mercantil']
        }

        for tag, valor in datos_persona.items():
            ET.SubElement(persona_moral, tag).text = str(valor)
        logger.info("Datos de persona moral agregados")

        # Representante/apoderado
        representante = ET.SubElement(persona_moral, "representante_apoderado")
        datos_representante = {
            'nombre': persona_df.iloc[0]['nombre_representante'],
            'apellido_paterno': persona_df.iloc[0]['apellido_paterno_representante'],
            'apellido_materno': persona_df.iloc[0]['apellido_materno_representante'],
            'fecha_nacimiento': persona_df.iloc[0]['fecha_nacimiento_representante'],
            'rfc': persona_df.iloc[0]['rfc_representante'],
            'curp': persona_df.iloc[0]['curp_representante']
        }

        for tag, valor in datos_representante.items():
            ET.SubElement(representante, tag).text = str(valor)
        logger.info("Datos de representante agregados")

        # Domicilio
        tipo_domicilio = ET.SubElement(persona_aviso, "tipo_domicilio")
        nacional = ET.SubElement(tipo_domicilio, "nacional")

        datos_domicilio = {
            'colonia': persona_df.iloc[0]['colonia'],
            'calle': persona_df.iloc[0]['calle'],
            'numero_exterior': persona_df.iloc[0]['numero_exterior'],
            'codigo_postal': str(persona_df.iloc[0]['codigo_postal']).zfill(5)
        }

        for tag, valor in datos_domicilio.items():
            ET.SubElement(nacional, tag).text = str(valor)
        logger.info("Datos de domicilio agregados")

        # Contacto
        telefono = ET.SubElement(persona_aviso, "telefono")
        ET.SubElement(telefono, "clave_pais").text = str(persona_df.iloc[0]['clave_pais'])
        ET.SubElement(telefono, "numero_telefono").text = str(persona_df.iloc[0]['numero_telefono'])
        ET.SubElement(telefono, "correo_electronico").text = persona_df.iloc[0]['correo_electronico']
        logger.info("Datos de contacto agregados")

        # Procesamiento de operaciones
        total_operaciones = len(operaciones_df)
        logger.info(f"Iniciando procesamiento de {total_operaciones} operaciones")

        detalle_operaciones = ET.SubElement(aviso, "detalle_operaciones")

        for idx, operacion in operaciones_df.iterrows():
            datos_op = ET.SubElement(detalle_operaciones, "datos_operacion")

            # Fecha y tipo de operación
            fecha_op = str(operacion['fecha_operacion']).split('.')[0]
            ET.SubElement(datos_op, "fecha_operacion").text = fecha_op

            tipo_operacion = str(operacion['tipo_operacion']).split('.')[0]
            ET.SubElement(datos_op, "tipo_operacion").text = tipo_operacion

            # Datos del bien/instrumento monetario
            tipo_bien = ET.SubElement(datos_op, "tipo_bien")
            datos_efectivo = ET.SubElement(tipo_bien, "datos_efectivo_instrumentos")
            ET.SubElement(datos_efectivo, "instrumento_monetario").text = \
                str(operacion['instrumento_monetario']).split('.')[0]
            ET.SubElement(datos_efectivo, "moneda").text = str(operacion['moneda']).split('.')[0]

            try:
                monto = f"{float(operacion['monto_operacion']):.2f}"
                ET.SubElement(datos_efectivo, "monto_operacion").text = monto
            except (ValueError, TypeError):
                ET.SubElement(datos_efectivo, "monto_operacion").text = "0.00"

            # Recepción
            recepcion = ET.SubElement(datos_op, "recepcion")
            ET.SubElement(recepcion, "tipo_servicio").text = str(operacion['tipo_servicio']).split('.')[0]
            fecha_recep = str(operacion['fecha_recepcion']).split('.')[0]
            ET.SubElement(recepcion, "fecha_recepcion").text = fecha_recep
            cp_recep = str(operacion['codigo_postal_recepcion']).split('.')[0]
            ET.SubElement(recepcion, "codigo_postal").text = cp_recep

            # Custodia (solo para tipo_operacion 1003)
            if tipo_operacion == "1003":
                logger.debug(f"Operación {idx + 1}: Agregando nodo de custodia")
                custodia = ET.SubElement(datos_op, "custodia")
                fecha_ini = str(operacion.get('fecha_inicio_custodia', '')).split('.')[0]
                fecha_fin = str(operacion.get('fecha_fin_custodia', '')).split('.')[0]
                ET.SubElement(custodia, "fecha_inicio").text = fecha_ini if fecha_ini else ''
                ET.SubElement(custodia, "fecha_fin").text = fecha_fin if fecha_fin else ''
                tipo_custodia_node = ET.SubElement(custodia, "tipo_custodia")
                datos_sucursal = ET.SubElement(tipo_custodia_node, "datos_sucursal")
                cp_sucursal = str(operacion.get('codigo_postal_sucursal', '')).split('.')[0]
                ET.SubElement(datos_sucursal, "codigo_postal").text = cp_sucursal if cp_sucursal else ''

            # Entrega
            entrega = ET.SubElement(datos_op, "entrega")
            fecha_ent = str(operacion['fecha_entrega']).split('.')[0]
            ET.SubElement(entrega, "fecha_entrega").text = fecha_ent
            tipo_entrega = ET.SubElement(entrega, "tipo_entrega")
            nacional_entrega = ET.SubElement(tipo_entrega, "nacional")
            cp_entrega = str(operacion['codigo_postal_entrega']).split('.')[0]
            ET.SubElement(nacional_entrega, "codigo_postal").text = cp_entrega

            # Destinatario
            destinatario = ET.SubElement(datos_op, "destinatario")
            dest_persona = str(operacion['destinatario_persona_aviso']).upper()
            ET.SubElement(destinatario, "destinatario_persona_aviso").text = dest_persona

            if (idx + 1) % 50 == 0 or (idx + 1) == total_operaciones:
                logger.info(f"Procesadas {idx + 1}/{total_operaciones} operaciones")

        # Generación del archivo XML final
        logger.info("Generando XML final")
        xml_str = ET.tostring(root, encoding='utf-8')
        xml_formateado = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8")

        with open(xml_salida, "wb") as f:
            f.write(xml_formateado)

        logger.info(f"Archivo XML generado exitosamente: {xml_salida}")
        logger.info("_" * 120)
        return xml_salida, None

    except Exception as e:
        logger.error(f"XML no generado - Error inesperado: {str(e)}", exc_info=True)
        return None, str(e)
