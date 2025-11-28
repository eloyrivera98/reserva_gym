import time
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, jsonify
from threading import Thread

# =========================================================
# ⚙️ CONFIGURACIÓN PERSONAL
# =========================================================
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HORARIOS = os.getenv("HORARIOS", "MUS075,MUS069").split(",")

if not USERNAME or not PASSWORD:
    raise ValueError("❌ ERROR: No se han definido USERNAME o PASSWORD.")

# =========================================================
# 🧩 FUNCIÓN PRINCIPAL PARA HACER RESERVAS
# =========================================================
def hacer_reserva():
    print("🚀 Iniciando reservas...")

    # Configuración Selenium
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

    # Login
    print("🔐 Iniciando sesión en la intranet UPV...")
    login_url = (
        "https://cas.upv.es/cas/login?service="
        "https%3A%2F%2Fwww.upv.es%2Fpls%2Fsoalu%2Fsic_intracas.app_intranet%3FP_CUA%3Dmiupv"
    )
    driver.get(login_url)

    try:
        wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "submitBtn").click()
        print("✅ Login correcto")
    except Exception as e:
        print("❌ Error al iniciar sesión:", e)
        driver.quit()
        return {"status": "error", "message": str(e)}

    # Página de horarios
    url_horarios = (
        "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?"
        "p_campus=V&p_tipoact=6846&p_codacti=21809&p_vista=intranet&p_idioma=c"
    )
    driver.get(url_horarios)

    # Extraer todos los enlaces
    enlaces_horarios = {}
    links = driver.find_elements(By.TAG_NAME, "a")
    for a in links:
        text = a.text.split("\n")[0].strip()
        href = a.get_attribute("href")
        if text:
            enlaces_horarios[text] = href
            print(f"{text} -> {href}")

    resultados = {}
    for horario in HORARIOS:
        print(f"🔎 Procesando horario: {horario}...")
        if horario not in enlaces_horarios:
            print(f"❌ No se encontró el horario {horario}")
            resultados[horario] = "NO_ENCONTRADO"
            continue

        link = enlaces_horarios[horario]
        print(f"✅ Enlace a reservar encontrado: {link}")

        driver.get(link)
        time.sleep(3)

        html = driver.page_source.lower()
        if any(palabra in html for palabra in ["reserva", "confirmada", "realizada", "correctamente"]):
            resultado = "OK"
            print(f"🚀 Reserva ejecutada para {horario}")
        else:
            resultado = "FALLO"
            print(f"⚠️ No se detectó confirmación para {horario}")

        # Guardar log
        with open("log_reservas.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {horario} -> {resultado}\n")

        resultados[horario] = resultado

    driver.quit()
    print("🟢 Script finalizado.")
    return {"status": "ok", "resultados": resultados}

# =========================================================
# 🔹 FLASK PARA CLOUD RUN
# =========================================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Servicio activo. Endpoint /reservar disponible."

@app.route("/reservar")
def reservar():
    # Ejecutar reservas en un thread para no bloquear Flask
    thread = Thread(target=hacer_reserva)
    thread.start()
    return jsonify({"status": "started", "message": "Reservas en ejecución"}), 200

# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
