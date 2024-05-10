from flask import Flask, render_template, request, redirect, url_for
import json

# pylint: disable=undefined-variable
app = Flask(__name__)

# Datos de ejemplo (eventos y usuarios)
eventos = []
usuarios = []

@app.route("/")
def index():
    return render_template("index.html", eventos=eventos)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        usuarios.append({"nombre": nombre, "email": email})
        return redirect(url_for("index"))
    return render_template("registro.html")

@app.route("/evento/<int:evento_id>", methods=["GET", "POST"])
def evento(evento_id):
    evento = eventos[evento_id]
    if request.method == "POST":
        nombre_usuario = request.form["nombre_usuario"]
        email_usuario = request.form["email_usuario"]
        reservacion = {"nombre": nombre_usuario, "email": email_usuario}
        evento["reservaciones"].append(reservacion)
        return redirect(url_for("index"))
    return render_template("evento.html", evento=evento)

if __name__ == "_main_":
    app.run(debug=True)