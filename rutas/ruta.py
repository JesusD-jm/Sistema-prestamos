from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required
from archivos_principales.models import Prestamo

ruta_bp = Blueprint("ruta", __name__, url_prefix="/ruta")


@ruta_bp.route("/hoy")
@login_required
def hoy():
    """
    Muestra solo los préstamos a los que hoy les toca cobrar
    (a tiempo o atrasados), ordenados con los más atrasados primero.
    """
    candidatos = Prestamo.query.filter(
        Prestamo.estado.in_(["activo", "atrasado"])
    ).all()

    prestamos = [p for p in candidatos if p.debe_cobrarse_hoy]
    prestamos.sort(key=lambda p: p.dias_atraso, reverse=True)

    total_a_cobrar = sum(float(p.cuota_esperada) for p in prestamos)

    return render_template(
        "ruta_hoy.html", prestamos=prestamos, hoy=date.today(), total_a_cobrar=total_a_cobrar
    )