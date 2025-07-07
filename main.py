from flask import Flask, request
from bot import main as ejecutar_bot

app = Flask(__name__)

# Clave de seguridad (opcional, para evitar que cualquier persona ejecute el bot)
CLAVE_SECRETA = "abc123"

@app.route("/")
def home():
    return "✅ Bot del consulado español está en línea."

@app.route("/check")
def check():
    # Verificamos si se pasó la clave correcta
    clave = request.args.get("key")
    if clave != CLAVE_SECRETA:
        return "❌ Clave incorrecta", 403

    ejecutar_bot()
    return "✅ Bot ejecutado correctamente."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
