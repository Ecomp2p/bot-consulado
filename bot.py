import os
import time
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Cargar variables de entorno
load_dotenv()
USUARIO = os.getenv("USUARIO_CONSULADO")
PASSWORD = os.getenv("PASSWORD_CONSULADO")
EMAILS = os.getenv("EMAILS_DESTINO").split(",")
EMAIL_ORIGEN = os.getenv("EMAIL_ORIGEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

LOGIN_URL = "https://www.cgeonline.com.ar/usuarios/login.html"
TURNOS_URL = "https://www.cgeonline.com.ar/tramites/citas/modificar/seleccionar-nueva-fecha.html"

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Paso 1: Ingresar al login
        page.goto(LOGIN_URL)
        page.fill('input[name="email"]', USUARIO)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button:has-text("Ingresar")')

        # Esperar a que cargue la página luego del login
        page.wait_for_timeout(3000)

        # Paso 2: Ir a la página de turnos
        page.goto(TURNOS_URL)
        page.wait_for_timeout(3000)

        # Paso 3: Revisar si hay turnos disponibles
        contenido = page.content()

        if "En este momento no hay fechas disponibles" not in contenido:
            enviar_alerta()

        browser.close()

if __name__ == "__main__":
    main()
