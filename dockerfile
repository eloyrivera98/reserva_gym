# =========================================
# Dockerfile para Render – Reservas UPV
# =========================================

# Imagen base con Chrome y ChromeDriver ya instalados
FROM selenium/standalone-chrome:latest

# -------------------------------
# Configuración del contenedor
# -------------------------------
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# -------------------------------
# Instalar dependencias Python
# -------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------
# Copiar código de la app
# -------------------------------
COPY . /app

# -------------------------------
# Exponer el puerto que Render asigna
# -------------------------------
EXPOSE 8080

# -------------------------------
# Comando por defecto para ejecutar tu script
# -------------------------------
CMD ["python", "reserva_upv.py"]
