# bot.py
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

USUARIO = os.getenv("USUARIO_CONSULADO")
PASSWORD = os.getenv("PASSWORD_CONSULADO")
EMAILS = [e.strip() for e in os.getenv("EMAILS_DESTINO", "").split(",") if e.strip()]
EMAIL_ORIGEN = os.getenv("EMAIL_ORIGEN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

LOGIN_URL = "https://www.cgeonline.com.ar/usuarios/login.html"
TURNOS_URL = "https://www.cgeonline.com.ar/tramites/citas/modificar/seleccionar-nueva-fecha.html"
STATUS_FILE = "status.txt"

def enviar_alerta():
    msg = EmailMessage()
    msg.set_content("🚨 ¡Hay turnos disponibles en el consulado español!\n\nIngresá ahora:\n" + TURNOS_URL)
    msg["Subject"] = "🛂 Turno disponible - Consulado Español"
    msg["From"] = EMAIL_ORIGEN
    msg["To"] = EMAILS

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
        smtp.send_message(msg)

def turnos_ya_notificados():
    return os.path.exists(STATUS_FILE)

def marcar_turnos_notificados():
    with open(STATUS_FILE, "w") as f:
        f.write("notificado")

def main():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(LOGIN_URL)
            page.fill('input[name="email"]', USUARIO)
            page.fill('input[name="password"]', PASSWORD)
            page.click('button:has-text("Ingresar")')
            page.wait_for_timeout(3000)

            page.goto(TURNOS_URL)
            page.wait_for_timeout(3000)

            contenido = page.content()

            if "En este momento no hay fechas disponibles" not in contenido:
                if not turnos_ya_notificados():
                    enviar_alerta()
                    marcar_turnos_notificados()
                    print("✅ Turnos detectados. Correo enviado.")
                else:
                    print("⚠️ Turnos ya notificados. No se reenvía.")
            else:
                print("❌ No hay turnos disponibles.")
                if os.path.exists(STATUS_FILE):
                    os.remove(STATUS_FILE)

            browser.close()

    except Exception as e:
        print(f"❌ Error al ejecutar el bot: {e}")

if __name__ == "__main__":
    main()
