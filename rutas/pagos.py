from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from archivos_principales.models import db, Pago, Prestamo

pagos_bp = Blueprint("pagos", __name__, url_prefix="/pagos")


@pagos_bp.route("/registrar/<int:prestamo_id>", methods=["GET", "POST"])
@login_required
def registrar(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)

    if request.method == "POST":

        # Caso 1: viene del botón "Marcar como pagado" (no trae monto_pagado)
        if request.form.get("marcar_pagado"):
            prestamo.saldo_actual = 0
            prestamo.estado = "pagado"
            db.session.commit()
            return render_template(
                "confirmacion_pago.html",
                titulo="Préstamo pagado",
                mensaje=f"El préstamo de {prestamo.cliente.nombre_completo} quedó marcado como pagado en su totalidad.",
            )

        # Caso 2: formulario normal de registrar pago

        # Monto pagado: OPCIONAL (antes era obligatorio)
        monto_pagado_raw = request.form.get("monto_pagado", "").strip()
        monto_pagado = float(monto_pagado_raw) if monto_pagado_raw else 0

        # Rédito: opcional, se guarda tal cual lo escribas
        redito_raw = request.form.get("redito", "").strip()
        redito = float(redito_raw) if redito_raw else None

        # Saldo después: OBLIGATORIO y MANUAL. Ya NO se calcula solo,
        # se usa exactamente el número que la persona escribe.
        saldo_despues_raw = request.form.get("saldo_despues", "").strip()
        if not saldo_despues_raw:
            flash("Debes escribir el saldo después del pago.", "danger")
            return render_template("registro_pago.html", prestamo=prestamo)
        saldo_despues = float(saldo_despues_raw)

        metodo_pago = request.form.get("metodo_pago", "efectivo")
        notas = request.form.get("notas")

        # Protección contra doble envío (doble clic / conexión lenta):
        # si el mismo préstamo ya recibió un pago con el mismo monto y
        # el mismo saldo resultante hace menos de 10 segundos, es duplicado.
        hace_10_segundos = datetime.utcnow() - timedelta(seconds=10)
        duplicado = Pago.query.filter(
            Pago.prestamo_id == prestamo.id,
            Pago.monto_pagado == monto_pagado,
            Pago.saldo_despues == saldo_despues,
            Pago.fecha_pago >= hace_10_segundos,
        ).first()

        if duplicado:
            flash("Este pago ya se había registrado (se evitó un duplicado).", "warning")
            return redirect(url_for("prestamos.detalle", prestamo_id=prestamo.id))

        pago = Pago(
            prestamo_id=prestamo.id,
            usuario_id=current_user.id,
            monto_pagado=monto_pagado,
            redito=redito,
            saldo_despues=saldo_despues,
            metodo_pago=metodo_pago,
            notas=notas,
        )
        db.session.add(pago)

        # El saldo del préstamo pasa a ser EXACTAMENTE lo que escribiste
        prestamo.saldo_actual = saldo_despues
        if saldo_despues <= 0:
            prestamo.saldo_actual = 0
            prestamo.estado = "pagado"

        db.session.commit()
        flash("Pago registrado correctamente", "success")
        return redirect(url_for("prestamos.detalle", prestamo_id=prestamo.id))

    return render_template("registro_pago.html", prestamo=prestamo)