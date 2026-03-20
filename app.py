from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# Carpeta donde está este archivo app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "datos.db")

# Inicializar la base de datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            edad INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Ruta principal: formulario
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form["nombre"]
        edad = request.form["edad"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personas (nombre, edad) VALUES (?, ?)", (nombre, edad))
        conn.commit()
        conn.close()

        return redirect("/lista")
    return render_template("index.html")

# Ruta lista: muestra tabla
@app.route("/lista")
def lista():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, edad FROM personas")
    datos = cursor.fetchall()
    conn.close()

    datos_dict = [{"nombre": d[0], "edad": d[1]} for d in datos]
    return render_template("lista.html", datos=datos_dict)

# Ruta eliminar
@app.route("/eliminar/<nombre>")
def eliminar(nombre):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personas WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()
    return redirect("/lista")

# Ruta editar: muestra formulario para editar
@app.route("/editar/<nombre>", methods=["GET", "POST"])
def editar(nombre):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        nuevo_nombre = request.form["nombre"]
        nueva_edad = request.form["edad"]
        cursor.execute("UPDATE personas SET nombre = ?, edad = ? WHERE nombre = ?", (nuevo_nombre, nueva_edad, nombre))
        conn.commit()
        conn.close()
        return redirect("/lista")
    
    cursor.execute("SELECT nombre, edad FROM personas WHERE nombre = ?", (nombre,))
    persona = cursor.fetchone()
    conn.close()
    if persona:
        return render_template("editar.html", persona={"nombre": persona[0], "edad": persona[1]})
    else:
        return redirect("/lista")

app.run(debug=True)
