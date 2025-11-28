import os
import time
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from dotenv import load_dotenv

# =========================================================
# ⚙️ CONFIGURACIÓN
# =========================================================
load_dotenv()  # Carga variables del entorno

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HORARIOS_OBJETIVO = os.getenv("HORARIOS", "MUS075,MUS069").split(",")

if not USERNAME or not PASSWORD:
    print("❌ ERROR: USERNAME o PASSWORD no definidos")
    exit(1)

# =========================================================
# FLASK
# =========================================================
app = Flask(__name__)

@app.route("/reservar")
def reservar_endpoint():
    # Ejecutar la reserva en un thread separado
    thread = Thread(target=hacer_reservas)
    thread.start()
    return jsonify({"status": "started", "message": "Reservas en ejecución"}), 200

# =========================================================
# FUNCIONES DE RESERVA
# =========================================================
def hacer_reservas():
    try:
        # =========================
        # Configurar Selenium / Chrome
        # =========================
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.binary_location = "/usr/bin/google-chrome"

        driver = uc.Chrome(
            options=options,
            driver_executable_path="/usr/local/bin/chromedriver"
        )
        wait = WebDriverWait(driver, 15)

        # =========================
        # Login
        # =========================
        print("🚀 Iniciando sesión en la intranet UPV...")
        login_url = (
            "https://cas.upv.es/cas/login?service="
            "https%3A%2F%2Fwww.upv.es%2Fpls%2Fsoalu%2Fsic_intracas.app_intranet%3FP_CUA%3Dmiupv"
        )
        driver.get(login_url)
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "submitBtn").click()
        print("✅ Login correcto")

        # =========================
        # Página de horarios
        # =========================
        url_horarios = (
            "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?"
            "p_campus=V&p_tipoact=6846&p_codacti=21809&p_vista=intranet&p_idioma=c"
        )
        driver.get(url_horarios)
        time.sleep(2)  # esperar que cargue

        # =========================
        # Extraer todos los enlaces de horarios
        # =========================
        print("🔹 Horarios disponibles:")
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        matriz_horarios = {}  # {'MUS075': 'url', ...}

        for a in enlaces:
            text = a.text.split("\n")[0].strip()  # coger solo MUSxxx
            href = a.get_attribute("href")
            if text and href:
                matriz_horarios[text] = href
                print(f"{text} -> {href}")

        # =========================
        # Procesar cada horario solicitado
        # =========================
        for horario in HORARIOS_OBJETIVO:
            print(f"\n🔎 Procesando horario: {horario}...")
            if horario in matriz_horarios:
                url_reserva = matriz_horarios[horario]
                print(f"✅ Enlace a reservar encontrado: {url_reserva}")
                driver.get(url_reserva)
                time.sleep(2)  # esperar que cargue
                html = driver.page_source.lower()
                resultado = "FALLO"
                if any(palabra in html for palabra in ["reserva", "confirmada", "realizada", "correctamente"]):
                    print(f"✅ Reserva ejecutada para {horario}")
                    resultado = "OK"
                else:
                    print(f"⚠️ No se detectó confirmación de reserva para {horario}")
                # Guardar log
                with open("log_reservas.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now()} - {horario} -> {resultado}\n")
            else:
                print(f"❌ No se encontró el horario {horario}")

        driver.quit()
        print("🟢 Script finalizado.")

    except Exception as e:
        print("❌ Error en hacer_reservas:", e)

# =========================================================
# Ejecutar Flask en Render
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
