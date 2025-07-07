import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
import time
import smtplib
from email.message import EmailMessage

# Cargar variables de entorno
load_dotenv()
USUARIO = os.getenv("USUARIO_CONSULADO")
PASSWORD = os.getenv("PASSWORD_CONSULADO")
EMAILS = os.getenv("EMAILS_DESTINO").split(",")
EMAIL_ORIGEN = os.getenv("EMAIL_ORIGEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

LOGIN_URL = "https://www.cgeonline.com.ar/usuarios/login.html"
TURNOS_URL = "https://www.cgeonline.com.ar/tramites/citas/modificar/seleccionar-nueva-fecha.html"

def iniciar_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = uc.Chrome(options=options)
    return driver

def loguearse(driver):
    driver.get(LOGIN_URL)
    time.sleep(2)
    driver.find_element(By.NAME, "email").send_keys(USUARIO)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, '//button[contains(text(),"Ingresar")]').click()
    time.sleep(3)

def revisar_turnos(driver):
    driver.get(TURNOS_URL)
    time.sleep(2)
    pagina = driver.page_source
    if "En este momento no hay fechas disponibles" not in pagina:
        return True
    return False

def enviar_alerta():
    msg = EmailMessage()
    msg.set_content("🚨 ¡Hay turnos disponibles en el consulado español!\n\nIngresá ahora a:\n" + TURNOS_URL)
    msg["Subject"] = "🛂 Turno disponible - Consulado Español"
    msg["From"] = EMAIL_ORIGEN
    msg["To"] = EMAILS

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
        smtp.send_message(msg)

def main():
    driver = iniciar_driver()
    try:
        loguearse(driver)
        if revisar_turnos(driver):
            enviar_alerta()
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
