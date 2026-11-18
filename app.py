"""Backend de Eco Consumo: sirve las páginas y guarda usuarios en MySQL.

Uso:
    pip install -r requirements.txt
    (copiar .env.example a .env y completar la contraseña de MySQL)
    python app.py
    abrir http://localhost:5000
"""
import os
import re
from datetime import date, datetime

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request, send_from_directory, session
from mysql.connector import errorcode
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)  # carpeta donde están los .html y .css
EXTENSIONES_PERMITIDAS = {".html", ".css"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambiame-por-una-clave-larga")


def conectar():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "eco_consumo"),
    )


def parsear_fecha(texto):
    """Convierte DD/MM/AA en una fecha. Devuelve None si no es válida."""
    try:
        fecha = datetime.strptime(texto, "%d/%m/%y").date()
        if fecha > date.today():  # "50" => 1950, no 2050
            fecha = fecha.replace(year=fecha.year - 100)
        return fecha
    except ValueError:
        return None


def error(mensaje, codigo=400):
    return jsonify(ok=False, error=mensaje), codigo


@app.post("/registro")
def registro():
    f = request.form
    nombre = f.get("nombre", "").strip()
    apellido = f.get("apellido", "").strip()
    nacimiento = f.get("nacimiento", "").strip()
    mail = f.get("mail", "").strip()
    usuario = f.get("usuario", "").strip()
    clave = f.get("clave", "")
    direccion = f.get("direccion", "").strip()

    if not all([nombre, apellido, nacimiento, mail, usuario, clave, direccion]):
        return error("Completá todos los campos.")

    fecha = parsear_fecha(nacimiento)
    if fecha is None:
        return error("La fecha de nacimiento debe tener el formato DD/MM/AA.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail):
        return error("El mail no es válido.")

    if not re.search(r"\d", clave) or not re.search(r"[A-Z]", clave):
        return error("La contraseña necesita al menos 1 número y 1 mayúscula.")

    con = None
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO usuarios "
            "(nombre, apellido, fecha_nacimiento, mail, usuario, clave_hash, direccion) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nombre, apellido, fecha, mail, usuario,
             generate_password_hash(clave), direccion),
        )
        con.commit()
        session["usuario_id"] = cur.lastrowid
    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            if "uq_usuarios_mail" in str(e.msg):
                return error("Ya existe una cuenta con ese mail.", 409)
            return error("Ese nombre de usuario ya está en uso.", 409)
        app.logger.exception("Error de MySQL en /registro")
        return error("No se pudo guardar la cuenta. Probá de nuevo.", 500)
    finally:
        if con is not None and con.is_connected():
            con.close()

    return jsonify(ok=True, redirigir="bienvenida.html")


@app.post("/login")
def login():
    datos = request.get_json(silent=True) or request.form
    identificador = (datos.get("identificador") or "").strip()
    clave = datos.get("clave") or ""

    if not identificador or not clave:
        return error("Completá tu mail o usuario y tu contraseña.")

    con = None
    try:
        con = conectar()
        cur = con.cursor()
        cur.execute(
            "SELECT id, clave_hash FROM usuarios WHERE mail = %s OR usuario = %s LIMIT 1",
            (identificador, identificador),
        )
        fila = cur.fetchone()
    except mysql.connector.Error:
        app.logger.exception("Error de MySQL en /login")
        return error("No se pudo iniciar sesión. Probá de nuevo.", 500)
    finally:
        if con is not None and con.is_connected():
            con.close()

    # Mismo mensaje si el usuario no existe o la clave está mal (no revela cuál falló)
    if fila is None or not check_password_hash(fila[1], clave):
        return error("Usuario o contraseña incorrectos.", 401)

    session["usuario_id"] = fila[0]
    return jsonify(ok=True, redirigir="bienvenida.html")


@app.get("/")
def inicio():
    return send_from_directory(RAIZ, "index.html")


@app.get("/<path:nombre>")
def paginas(nombre):
    # Solo se sirven .html y .css de la carpeta raíz (nunca backend/ ni el .env)
    if os.path.dirname(nombre) or os.path.splitext(nombre)[1] not in EXTENSIONES_PERMITIDAS:
        abort(404)
    return send_from_directory(RAIZ, nombre)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
