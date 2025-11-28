FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# ============================
# Instalar dependencias básicas
# ============================
RUN apt-get update && apt-get install -y \
    wget curl unzip xvfb gnupg --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# ============================
# Instalar Chrome for Testing (incluye ChromeDriver compatible)
# ============================
RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) && \
    wget -O /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chrome-linux64.zip && \
    wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chrome.zip -d /opt && \
    unzip /tmp/chromedriver.zip -d /opt && \
    ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome && \
    ln -s /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver /usr/bin/google-chrome

# ============================
# Copiar proyecto
# ============================
WORKDIR /app
COPY . .

# ============================
# Instalar Python
# ============================
RUN pip install -r requirements.txt

CMD ["python", "reserva_upv.py"]
