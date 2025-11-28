# Imagen base ligera con Python
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# ============================
# Instalar dependencias y Chrome
# ============================
RUN apt-get update && apt-get install -y \
    wget gnupg unzip xvfb \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# ============================
# Instalar ChromeDriver compatible
# ============================
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
    DRIVER_VERSION=$(wget -qO- "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION") && \
    wget "https://storage.googleapis.com/chrome-for-testing-public/$DRIVER_VERSION/linux64/chromedriver-linux64.zip" \
        -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver

# ============================
# Copiar proyecto
# ============================
WORKDIR /app
COPY . .

# ============================
# Instalar Python
# ============================
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ============================
# Comando de ejecución
# ============================
CMD ["python", "reserva_upv.py"]
