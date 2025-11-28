import os
import time
from datetime import datetime
from flask import Flask, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# =========================================================
# ⚙️ CARGAR VARIABLES DE ENTORNO
# =========================================================
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HORARIOS_OBJETIVO = os.getenv("HORARIOS", "MUS075,MUS069").split(",")

if not USERNAME or not PASSWORD:
    raise ValueError("USERNAME o PASSWORD no definidos en variables de entorno")

# =========================================================
# 🔹 FLASK APP
# =========================================================
app = Flask(__name__)

@app.route("/reservar", methods=["GET"])
def reservar():
    resultados = []
    
    # =========================================================
    # 🧩 CONFIGURACIÓN SELENIUM (Chrome Headless)
    # =========================================================
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    # Ruta Chrome preinstalado en la imagen base
    options.binary_location = "/opt/bin/google-chrome"  # selenium/standalone-chrome
    driver = uc.Chrome(options=options, driver_executable_path="/opt/bin/chromedriver")
    wait = WebDriverWait(driver, 15)
    
    try:
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

        # =========================================================
        # 📅 Página de horarios
        # =========================================================
        url_horarios = (
            "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?"
            "p_campus=V&p_tipoact=6846&p_codacti=21809&p_vista=intranet&p_idioma=c"
        )
        driver.get(url_horarios)
        time.sleep(2)

        # =========================================================
        # 🔍 Construir matriz de horarios disponibles
        # =========================================================
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        matriz_horarios = {}
        for e in enlaces:
            texto = e.text.split("\n")[0].strip()  # Primer línea: código MUSXXX
            href = e.get_attribute("href")
            if texto and href:
                matriz_horarios[texto] = href

        print("🔹 Horarios disponibles:")
        for k, v in matriz_horarios.items():
            print(f"{k} -> {v}")

        # =========================================================
        # 🖱️ Reservar cada horario solicitado
        # =========================================================
        for horario in HORARIOS_OBJETIVO:
            horario = horario.strip()
            print(f"🔎 Procesando horario: {horario}...")
            enlace = matriz_horarios.get(horario)
            if not enlace:
                print(f"❌ No se encontró el horario {horario}")
                resultados.append({"horario": horario, "resultado": "NO_ENCONTRADO"})
                continue

            driver.get(enlace)
            time.sleep(2)
            html = driver.page_source.lower()
            if any(p in html for p in ["reserva", "confirmada", "realizada", "correctamente"]):
                print(f"✅ Reserva ejecutada para {horario}")
                resultado = "OK"
            else:
                print(f"⚠️ No se detectó confirmación de reserva para {horario}")
                resultado = "FALLO"

            resultados.append({"horario": horario, "resultado": resultado})

    except Exception as e:
        print("❌ Error en el proceso:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()

    # =========================================================
    # 🧾 Guardar log
    # =========================================================
    with open("log_reservas.txt", "a", encoding="utf-8") as f:
        for r in resultados:
            f.write(f"{datetime.now()} - {r['horario']} -> {r['resultado']}\n")

    return jsonify(resultados)

# =========================================================
# Run Flask solo si se ejecuta directamente
# =========================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
