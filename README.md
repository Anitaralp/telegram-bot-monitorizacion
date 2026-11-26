# 🤖 Bot de Telegram para monitorización de servidores y clasificación de documentos (OCR)

Bot en **Python** que permite consultar desde Telegram el estado de un servidor **Linux (Ubuntu Server)** y que **clasifica automáticamente documentos** (fotos y PDFs) usando **OCR con Tesseract**.

Lo desarrollé en mis prácticas de Técnica en Sistemas (FCT, 2025-2026) y lo desplegué en una máquina virtual con Ubuntu Server.

## ✨ Funcionalidades

**1. Monitorización del servidor**

| Comando | Qué devuelve |
|---|---|
| `/start` | Mensaje de bienvenida y ayuda |
| `/status` | Hostname, tiempo encendido y uso de memoria (`free -h`) |
| `/disk` | Espacio en disco (`df -h`) |
| `/uptime` | Tiempo encendido y carga media |

**2. Clasificación automática de documentos**

1. Envías una **foto** o un **PDF** al bot.
2. El bot extrae el texto con **Tesseract OCR** (en español). Los PDFs se convierten antes en imágenes con `pdf2image`.
3. Busca palabras clave y clasifica el documento como **facturas**, **contratos**, **informes** u **otros**.
4. Lo guarda en `~/documentos/<categoría>/`, con fecha y hora en el nombre, y te confirma dónde lo ha guardado.

## 🧰 Tecnologías

Python 3 · python-telegram-bot · Tesseract OCR · pytesseract · pdf2image / Poppler · Pillow · Ubuntu Server · VirtualBox

## 🚀 Instalación (Ubuntu / Debian)

```bash
# 1. Dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip tesseract-ocr tesseract-ocr-spa poppler-utils -y

# 2. Librerías de Python
pip3 install -r requirements.txt

# 3. Token del bot (créalo con @BotFather en Telegram)
export TELEGRAM_TOKEN="tu_token"

# 4. Arrancar el bot
python3 bot.py
```

> 🔐 **Seguridad:** el token nunca se escribe en el código. Se lee de la variable de entorno `TELEGRAM_TOKEN`.

## ⚙️ Configuración

- `CATEGORIAS` en `bot.py`: palabras clave de cada tipo de documento. Puedes añadir categorías nuevas.
- `CARPETA_DOCUMENTOS` (variable de entorno, opcional): dónde se guardan los documentos. Por defecto, `~/documentos`.

## 📈 Posibles mejoras

- Restringir el bot a usuarios autorizados (lista de IDs de Telegram).
- Ejecutarlo como servicio con **systemd** para que arranque solo.
- Alertas proactivas cuando el disco o la CPU superen un umbral.

---

**Autora:** Ana Rodríguez Aguilar · [LinkedIn](https://www.linkedin.com/in/ana-rodriguez-aguilar-211496269)
