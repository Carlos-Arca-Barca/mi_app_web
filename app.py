import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# -------------------------------------
# CONEXIÓN
# -------------------------------------

def get_conn():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT")
    )
# -------------------------------------
# INDEX (INSERT)
# -------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = request.form.get("edad", "").strip()
        email = request.form.get("email", "").strip()
        fecha_nac = request.form.get("fecha_nac", "").strip()

        # Validación
        if not nombre or not edad.isdigit() or not email or not fecha_nac:
            error = "Todos los campos son obligatorios"
        else:
            try:
                # Convertir fecha a formato PostgreSQL
                fecha_obj = datetime.strptime(fecha_nac, "%Y-%m-%d")

                conn = get_conn()
                cursor = conn.cursor()

                cursor.execute(
                    """INSERT INTO contactos (nombre, edad, email, fecha_nac)
                       VALUES (%s, %s, %s, %s)""",
                    (nombre, int(edad), email, fecha_obj)
                )

                conn.commit()
                conn.close()

                return redirect(url_for("lista"))

            except Exception as e:
                error = f"Error: {e}"

    return render_template("index.html", titulo="Nuevo", activo="inicio", error=error)

# -------------------------------------
# LISTA
# -------------------------------------
@app.route("/lista")
def lista():
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT 
            id_contacto,
            nombre,
            edad,
            email,
            TO_CHAR(fecha_nac, 'DD-MM-YYYY') as fecha_nac
        FROM contactos
    """)

    datos = cursor.fetchall()
    conn.close()

    return render_template("lista.html", titulo="Lista", activo="lista", datos=datos)

# -------------------------------------
# EDITAR
# -------------------------------------
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_conn()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("SELECT * FROM contactos WHERE id_contacto = %s", (id,))
    persona = cursor.fetchone()

    if not persona:
        conn.close()
        return "No encontrado", 404

    error = None

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        edad = request.form.get("edad", "").strip()
        email = request.form.get("email", "").strip()
        fecha_nac = request.form.get("fecha_nac", "").strip()

        if not nombre or not edad.isdigit() or not email or not fecha_nac:
            error = "Todos los campos son obligatorios"
        else:
            try:
                fecha_obj = datetime.strptime(fecha_nac, "%Y-%m-%d")

                cursor.execute(
                    """UPDATE contactos 
                       SET nombre=%s, edad=%s, email=%s, fecha_nac=%s 
                       WHERE id_contacto=%s""",
                    (nombre, int(edad), email, fecha_obj, id)
                )

                conn.commit()
                conn.close()

                return redirect(url_for("lista"))

            except Exception as e:
                error = f"Error: {e}"

    conn.close()
    return render_template("editar.html", titulo="Editar", activo="editar", persona=persona, error=error)

# -------------------------------------
# ELIMINAR
# -------------------------------------
@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contactos WHERE id_contacto=%s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("lista"))

# -------------------------------------
if __name__ == "__main__":
    app.run(debug=True)