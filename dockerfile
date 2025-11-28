# =========================================
# Dockerfile para Render – Reservas UPV
# =========================================
FROM python:3.11

# -------------------------------
# Variables de entorno
# -------------------------------
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# -------------------------------
# Instalar dependencias básicas y librerías para Chrome
# -------------------------------
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
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
        procps \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Instalar Google Chrome estable
# -------------------------------
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------
# Instalar ChromeDriver compatible automáticamente
# -------------------------------
RUN CHROME_VERSION=$(google-chrome --version | sed 's/Google Chrome //; s/ .*//') && \
    CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION) && \
    curl -Lo /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/*

# -------------------------------
# Instalar dependencias Python
# -------------------------------
WORKDIR /app
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
# Comando por defecto para ejecutar Flask
# -------------------------------
CMD ["python", "main.py"]
