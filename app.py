



import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

# -------------------------------------
# 1️⃣ Rutas de archivos
# -------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "datos.db")

# -------------------------------------
# 2️⃣ Crear app Flask
# -------------------------------------
app = Flask(__name__)

# -------------------------------------
# 3️⃣ Funciones de DB
# -------------------------------------
def get_conn():
    """Devuelve la conexión a SQLite con filas como diccionarios"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # <-- filas como diccionarios
    return conn

def crear_tabla():
    """Crea tabla si no existe"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Crear la tabla al iniciar
crear_tabla()

# -------------------------------------
# 4️⃣ Rutas de Flask
# -------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = request.form.get("edad", "").strip()
        email = request.form.get("email", "").strip()

        # Validación back-end
        if not nombre or not edad.isdigit() or not email:
            error = "Todos los campos son obligatorios y la edad debe ser un número."
        else:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO personas (nombre, edad, email) VALUES (?, ?, ?)",
                (nombre, int(edad), email)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("lista"))

    return render_template("index.html", titulo="Nuevo Registro", activo="inicio", error=error)

# -------------------------------------
@app.route("/lista")
def lista():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas")
    filas = cursor.fetchall()
    conn.close()

    # Convertir filas en diccionarios
    datos = [dict(f) for f in filas]

    return render_template("lista.html", titulo="Lista de Personas", activo="lista", datos=datos)

# -------------------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personas WHERE id = ?", (id,))
    fila = cursor.fetchone()

    if fila is None:
        conn.close()
        return "Registro no encontrado", 404

    persona = dict(fila)
    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = request.form.get("edad", "").strip()
        email = request.form.get("email", "").strip()

        if not nombre or not edad.isdigit() or not email:
            error = "Todos los campos son obligatorios y la edad debe ser un número."
        else:
            cursor.execute(
                "UPDATE personas SET nombre=?, edad=?, email=? WHERE id=?",
                (nombre, int(edad), email, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("lista"))

    conn.close()
    return render_template("editar.html", titulo="Editar Registro", activo="editar", persona=persona, error=error)

# -------------------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personas WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("lista"))

# -------------------------------------
if __name__ == "__main__":
    app.run(debug=True)