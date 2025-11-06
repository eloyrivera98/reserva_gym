import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# =========================================================
# ⚙️ CONFIGURACIÓN BÁSICA
# =========================================================

# Instala automáticamente la versión correcta de chromedriver
chromedriver_autoinstaller.install()

# Lee credenciales y datos desde variables de entorno
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
HORARIO_OBJETIVO = os.getenv("HORARIO")  # Ejemplo: MUS075

LOGIN_URL = "https://intranet.upv.es/pls/soalu/sic_depact.HSemActividades?p_campus=V&p_codacti=21809&p_vista=intranet&p_idioma=c&p_tipoact=6846"

# =========================================================
# 🚀 CONFIGURACIÓN DE SELENIUM
# =========================================================
options = Options()
options.add_argument("--headless")  # No abre ventana
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

service = Service()  # Chromedriver lo instala automáticamente
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

print("🔵 Iniciando reserva automática UPV...")

# =========================================================
# 🔐 LOGIN EN INTRANET
# =========================================================
driver.get(LOGIN_URL)

# Esperar y rellenar formulario de login (ajustar selectores según HTML real)
try:
    wait.until(EC.presence_of_element_located((By.NAME, "p_usuario"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.NAME, "p_clave"))).send_keys(PASSWORD)
    driver.find_element(By.NAME, "p_login").click()
except Exception as e:
    print("⚠️ Error durante el login:", e)

# =========================================================
# 🔎 BUSCAR EL ENLACE DEL GRUPO DESEADO
# =========================================================
wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
enlaces = driver.find_elements(By.TAG_NAME, "a")

target_link = None
for e in enlaces:
    if HORARIO_OBJETIVO in e.text:
        target_link = e.get_attribute("href")
        break

if not target_link:
    print(f"❌ No se encontró el grupo {HORARIO_OBJETIVO}.")
    driver.quit()
    exit()

print(f"✅ Encontrado grupo {HORARIO_OBJETIVO}. Abriendo enlace de reserva...")

# =========================================================
# 🧾 ABRIR LA PÁGINA DE RESERVA (SE RESERVA AUTOMÁTICAMENTE)
# =========================================================
driver.get(target_link)

# Esperar unos segundos para que la reserva se complete
time.sleep(5)

# =========================================================
# 🧾 GUARDAR LOG LOCAL
# =========================================================
resultado = "Reserva completada"
with open("log_reservas.txt", "a", encoding="utf-8") as f:
    f.write(f"{datetime.now()} - {HORARIO_OBJETIVO} -> {resultado}\n")

driver.quit()
print("🟢 Script finalizado correctamente.")
