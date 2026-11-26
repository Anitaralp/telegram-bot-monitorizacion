#!/usr/bin/env python3
"""
Bot de Telegram para monitorización de un servidor Linux
y clasificación automática de documentos mediante OCR.

Comandos:
  /start   - Mensaje de bienvenida
  /status  - Hostname, uptime y memoria
  /disk    - Espacio en disco
  /uptime  - Tiempo encendido y carga

Si se envía una foto o un PDF, el bot extrae el texto con Tesseract,
clasifica el documento por palabras clave y lo guarda en su carpeta.
"""

import os
import shutil
import subprocess
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# ============================================
# CONFIGURACIÓN
# ============================================
# El token NUNCA se escribe en el código: se lee de una variable de entorno.
#   export TELEGRAM_TOKEN="tu_token_de_BotFather"
TOKEN = os.environ.get("TELEGRAM_TOKEN")

CARPETA_BASE = os.environ.get("CARPETA_DOCUMENTOS", os.path.expanduser("~/documentos"))

CATEGORIAS = {
    "facturas": ["factura", "importe", "total", "iva", "precio", "pago"],
    "contratos": ["contrato", "clausula", "firmante", "partes", "acuerdo"],
    "informes": ["informe", "resumen", "analisis", "conclusion", "resultado"],
}


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def ejecutar(comando):
    """Ejecuta un comando del sistema y devuelve su salida."""
    return subprocess.run(comando, capture_output=True, text=True).stdout.strip()


def clasificar_documento(texto):
    """Clasifica el documento según las palabras clave de CATEGORIAS."""
    texto_lower = texto.lower()
    for categoria, palabras in CATEGORIAS.items():
        for palabra in palabras:
            if palabra in texto_lower:
                return categoria
    return "otros"


def extraer_texto_imagen(ruta_imagen):
    """Extrae el texto de una imagen con OCR (Tesseract, español)."""
    imagen = Image.open(ruta_imagen)
    return pytesseract.image_to_string(imagen, lang="spa")


def extraer_texto_pdf(ruta_pdf):
    """Convierte cada página del PDF en imagen y extrae su texto con OCR."""
    paginas = convert_from_path(ruta_pdf)
    texto_completo = ""
    for pagina in paginas:
        texto_completo += pytesseract.image_to_string(pagina, lang="spa")
    return texto_completo


# ============================================
# COMANDOS DEL BOT
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start - Mensaje de bienvenida."""
    mensaje = (
        "¡Hola! Soy tu bot de monitorización.\n\n"
        "Comandos disponibles:\n"
        "/status - Estado general del sistema\n"
        "/disk - Espacio en disco\n"
        "/uptime - Tiempo encendido\n\n"
        "También puedes enviarme imágenes o PDFs y los clasificaré automáticamente."
    )
    await update.message.reply_text(mensaje)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status - Información general del sistema."""
    mensaje = (
        "Estado del servidor\n"
        "===================\n"
        f"Hostname: {ejecutar(['hostname'])}\n"
        f"Uptime: {ejecutar(['uptime', '-p'])}\n\n"
        f"Memoria:\n{ejecutar(['free', '-h'])}"
    )
    await update.message.reply_text(mensaje)


async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/disk - Espacio en disco."""
    await update.message.reply_text(f"Espacio en disco:\n\n{ejecutar(['df', '-h'])}")


async def uptime_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/uptime - Tiempo que lleva encendido el servidor y carga media."""
    await update.message.reply_text(f"Uptime del servidor:\n\n{ejecutar(['uptime'])}")


async def procesar_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa imágenes y PDFs enviados al bot: OCR, clasificación y archivado."""
    await update.message.reply_text("¡Recibido! Procesando documento...")

    try:
        if update.message.photo:
            foto = update.message.photo[-1]  # la de mayor resolución
            archivo = await foto.get_file()
            ruta_temp = f"/tmp/{foto.file_id}.jpg"
            await archivo.download_to_drive(ruta_temp)
            texto = extraer_texto_imagen(ruta_temp)

        elif update.message.document:
            doc = update.message.document
            archivo = await doc.get_file()
            nombre = os.path.basename(doc.file_name)
            ruta_temp = f"/tmp/{nombre}"
            await archivo.download_to_drive(ruta_temp)

            if nombre.lower().endswith(".pdf"):
                texto = extraer_texto_pdf(ruta_temp)
            else:
                texto = extraer_texto_imagen(ruta_temp)

        else:
            await update.message.reply_text("Formato no soportado.")
            return

        categoria = clasificar_documento(texto)
        carpeta_destino = os.path.join(CARPETA_BASE, categoria)
        os.makedirs(carpeta_destino, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_final = f"{timestamp}_{os.path.basename(ruta_temp)}"
        ruta_destino = os.path.join(carpeta_destino, nombre_final)
        shutil.move(ruta_temp, ruta_destino)

        await update.message.reply_text(
            f"¡Documento procesado!\n\nCategoría: {categoria}\nGuardado en: {ruta_destino}"
        )

    except Exception as e:
        await update.message.reply_text(f"Error al procesar: {e}")


# ============================================
# FUNCIÓN PRINCIPAL
# ============================================

def main():
    if not TOKEN:
        raise SystemExit("Falta la variable de entorno TELEGRAM_TOKEN.")

    print("Iniciando bot...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("disk", disk))
    app.add_handler(CommandHandler("uptime", uptime_cmd))
    app.add_handler(MessageHandler(filters.PHOTO, procesar_documento))
    app.add_handler(MessageHandler(filters.Document.ALL, procesar_documento))

    print("Bot iniciado correctamente. Pulsa Ctrl+C para detenerlo.")
    app.run_polling()


if __name__ == "__main__":
    main()
