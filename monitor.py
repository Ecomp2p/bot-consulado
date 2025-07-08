import requests
from bs4 import BeautifulSoup
import smtplib
import os

# Obtener la última fecha conocida del archivo (si existe)
ULTIMA_FECHA_PATH = "ultima_fecha.txt"

def obtener_fecha_actual():
    url = "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Buscar la fila 13 (índice 12 sin contar encabezado)
    filas = soup.select("table tr")[13]  # Fila 13 incluyendo encabezado
    columnas = filas.find_all("td")
    if len(columnas) >= 3:
        return "simulacion-cambio"
    return None

def enviar_email(asunto, cuerpo):
    remitente = os.environ["EMAIL_ORIGEN"]
    contraseña = os.environ["EMAIL_PASSWORD"]
    destinatarios = os.environ["EMAILS_DESTINO"].split(",")

    mensaje = f"Subject: {asunto}\n\n{cuerpo}"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remitente, contraseña)
        smtp.sendmail(remitente, destinatarios, mensaje)

def main():
    nueva_fecha = obtener_fecha_actual()

    if not nueva_fecha:
        print("❌ No se pudo obtener la nueva fecha.")
        return

    # Leer la última fecha guardada
    try:
        with open(ULTIMA_FECHA_PATH, "r") as f:
            ultima_fecha = f.read().strip()
    except FileNotFoundError:
        ultima_fecha = ""

    # Comparar y actuar
    if nueva_fecha != ultima_fecha:
        asunto = "🛂 Nueva apertura de turnos en el Consulado"
        cuerpo = f"¡Atención! Hay una nueva fecha publicada: {nueva_fecha}\n\nVerifica en: https://www.cgeonline.com.ar/informacion/apertura-de-citas.html"
        enviar_email(asunto, cuerpo)

        with open(ULTIMA_FECHA_PATH, "w") as f:
            f.write(nueva_fecha)

        print("✅ Cambio detectado y correo enviado.")
    else:
        print("🔁 Sin cambios en la fecha de apertura.")

if __name__ == "__main__":
    main()
