import time
import os
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# =========================================================
# ⚙️ CONFIGURACIÓN PERSONAL
# =========================================================
load_dotenv()  # Carga variables del entorno (.env o Render Environment)

USERNAME = os.getenv("USERNAME")  # 🔑 Usuario UPV
PASSWORD = os.getenv("PASSWORD")  # 🔑 Contraseña UPV
HORARIO_OBJETIVO = os.getenv("HORARIO", "MUS075")  # Grupo o código del horario

if not USERNAME or not PASSWORD:
    print("❌ ERROR: No se han definido USERNAME o PASSWORD en Render.")
    exit(1)

# =========================================================
# 🧩 CONFIGURACIÓN SELENIUM (Chrome for Testing en Docker)
# =========================================================
options = uc.ChromeOptions()

# Flags obligatorios para Chrome en Render
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")

# Ruta correcta dentro del contenedor Docker
options.binary_location = "/usr/bin/google-chrome"

# Crear driver apuntando a ChromeDriver instalado en /usr/local/bin/chromedriver
driver = uc.Chrome(
    options=options,
    driver_executable_path="/usr/local/bin/chromedriver"
)

wait = WebDriverWait(driver, 15)

# =========================================================
# 🔐 LOGIN EN INTRANET
# =========================================================
print("🚀 Iniciando sesión en la intranet UPV...")

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
    exit(1)

# =========================================================
# 📅 IR A LA PÁGINA DE HORARIOS
# =========================================================
print("📅 Cargando página de horarios...")

url_horarios = (
    "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?"
    "p_campus=V&p_tipoact=6846&p_codacti=21809&p_vista=intranet&p_idioma=c"
)

driver.get(url_horarios)

# =========================================================
# 🔍 BUSCAR EL HORARIO OBJETIVO
# =========================================================
print(f"🔎 Buscando enlace con el texto: {HORARIO_OBJETIVO}...")

try:
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    enlaces = driver.find_elements(By.TAG_NAME, "a")

    target_link = None
    for e in enlaces:
        if HORARIO_OBJETIVO in e.text:
            target_link = e.get_attribute("href")
            break

    if not target_link:
        print(f"❌ No se encontró el horario {HORARIO_OBJETIVO}")
        driver.quit()
        exit(1)

    print(f"✅ Enlace encontrado: {target_link}")

except Exception as e:
    print("❌ Error buscando el enlace:", e)
    driver.quit()
    exit(1)

# =========================================================
# 🖱️ ACCEDER AL ENLACE DE RESERVA
# =========================================================
print("🚀 Accediendo al enlace para realizar la reserva automáticamente...")
driver.get(target_link)

time.sleep(3)

# =========================================================
# ✅ COMPROBAR SI LA RESERVA SE REALIZÓ
# =========================================================
html = driver.page_source.lower()

if any(palabra in html for palabra in ["reserva", "confirmada", "realizada", "correctamente"]):
    print("✅ Reserva confirmada correctamente.")
    resultado = "OK"
else:
    print("⚠️ No se detectó confirmación de reserva (quizás sin plazas o error).")
    resultado = "FALLO"

# =========================================================
# 🧾 GUARDAR REGISTRO (LOG)
# =========================================================
with open("log_reservas.txt", "a", encoding="utf-8") as f:
    f.write(f"{datetime.now()} - {HORARIO_OBJETIVO} -> {resultado}\n")

driver.quit()
print("🟢 Script finalizado.")
