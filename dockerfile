# Usa una imagen ligera con Python y soporte para Chrome
FROM python:3.10-slim

# Evita mensajes interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema y Google Chrome
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Ejecutar el script principal
CMD ["python", "reserva_upv.py"]
