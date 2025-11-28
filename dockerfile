# =============================
# Dockerfile para reservas UPV
# =============================

# 1️⃣ Imagen base oficial de Python
FROM python:3.11-slim

# 2️⃣ Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 3️⃣ Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libgconf-2-4 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Instalar Google Chrome estable
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 5️⃣ Instalar ChromeDriver compatible automáticamente
RUN CHROME_VERSION=$(google-chrome --version | sed 's/Google Chrome //; s/ .*//') \
    && CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION) \
    && curl -Lo /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/*

# 6️⃣ Crear directorio de la app
WORKDIR /app

# 7️⃣ Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 8️⃣ Copiar todo el proyecto
COPY . .

# 9️⃣ Exponer el puerto que usará Cloud Run
ENV PORT 8080
EXPOSE 8080

# 1️⃣0️⃣ Comando por defecto para ejecutar Flask
CMD ["python", "main.py"]
