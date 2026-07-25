from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from archivos_principales.models import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_input = request.form["usuario"]
        password_input = request.form["password"]

        usuario = Usuario.query.filter_by(usuario=usuario_input, activo=True).first()

        if usuario and check_password_hash(usuario.password_hash, password_input):
            login_user(usuario)
            return redirect(url_for("prestamos.dashboard"))

        flash("Usuario o contraseña incorrectos", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))