from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from archivos_principales.models import db, Prestamo, Cliente
from sqlalchemy import or_

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")
prestamos_bp = Blueprint("prestamos", __name__, url_prefix="/prestamos")

@clientes_bp.route("/", endpoint="listar")
@login_required
def clientes_listar():
    busqueda = request.args.get("q", "")
    query = Cliente.query.filter_by(activo=True)

    if busqueda:
        query = query.filter(
            or_(
                Cliente.nombre_completo.ilike(f"%{busqueda}%"),
                Cliente.cedula.ilike(f"%{busqueda}%"),
            )
        )

    clientes = query.order_by(Cliente.nombre_completo).all()
    return render_template("lista_clientes.html", clientes=clientes, busqueda=busqueda)


@clientes_bp.route("/nuevo", methods=["GET", "POST"], endpoint="nuevo")
@login_required
def clientes_nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre_completo", "").strip()
        cedula = request.form.get("cedula", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        referencia = request.form.get("referencia", "").strip()
        notas = request.form.get("notas", "").strip()

        if not cedula.isdigit():
            flash("La cédula sólo debe contener números.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)
        if len(cedula) > 10:
            flash("La cédula no puede tener más de 10 dígitos.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)
        if telefono and not telefono.isdigit():
            flash("El teléfono sólo debe contener números.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)
        if telefono and len(telefono) > 10:
            flash("El teléfono no puede tener más de 10 dígitos.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        missing = []
        if not nombre:
            missing.append("Nombre completo")
        if not cedula:
            missing.append("Cédula")
        if not telefono:
            missing.append("Teléfono")

        if missing:
            flash(f"Faltan campos requeridos: {', '.join(missing)}", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        errors = []
        if cedula and (not cedula.isdigit() or len(cedula) > 10):
            errors.append("Cédula inválida: sólo números, máximo 10 dígitos")
        if telefono and (not telefono.isdigit() or len(telefono) > 10):
            errors.append("Teléfono inválido: sólo números, máximo 10 dígitos")
        if errors:
            flash("; ".join(errors), "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        existente = Cliente.query.filter_by(cedula=cedula).first()
        if existente:
            flash("La cédula ya está registrada para otro cliente.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        cliente = Cliente(
            nombre_completo=nombre,
            cedula=cedula,
            telefono=telefono or None,
            direccion=direccion,
            referencia=referencia or None,
            notas=notas or None,
        )
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente registrado correctamente", "success")
        return redirect(url_for("clientes.listar"))

    return render_template("form_clientes.html", cliente=None)


@clientes_bp.route("/<int:cliente_id>", endpoint="detalle")
@login_required
def clientes_detalle(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return render_template("detalles_clientes.html", cliente=cliente)


@clientes_bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"], endpoint="editar")
@login_required
def clientes_editar(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    if request.method == "POST":
        nombre = request.form.get("nombre_completo", "").strip()
        cedula = request.form.get("cedula", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        referencia = request.form.get("referencia", "").strip()
        notas = request.form.get("notas", "").strip()

        if not cedula.isdigit():
            flash("La cédula sólo debe contener números.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)
        if len(cedula) > 10:
            flash("La cédula no puede tener más de 10 dígitos.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)
        if not telefono.isdigit():
            flash("El teléfono sólo debe contener números.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)
        if len(telefono) > 10:
            flash("El teléfono no puede tener más de 10 dígitos.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        missing = []
        if not nombre:
            missing.append("Nombre completo")
        if not cedula:
            missing.append("Cédula")
        if not telefono:
            missing.append("Teléfono")

        if missing:
            flash(f"Faltan campos requeridos: {', '.join(missing)}", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        errors = []
        if cedula and (not cedula.isdigit() or len(cedula) > 10):
            errors.append("Cédula inválida: sólo números, máximo 10 dígitos")
        if telefono and (not telefono.isdigit() or len(telefono) > 10):
            errors.append("Teléfono inválido: sólo números, máximo 10 dígitos")
        if errors:
            flash("; ".join(errors), "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        existente = Cliente.query.filter(Cliente.cedula == cedula, Cliente.id != cliente.id).first()
        if existente:
            flash("La cédula ya está registrada para otro cliente.", "danger")
            cliente_data = {
                'nombre_completo': nombre,
                'cedula': cedula,
                'telefono': telefono,
                'direccion': direccion,
                'referencia': referencia,
                'notas': notas,
            }
            return render_template("form_clientes.html", cliente=cliente_data)

        cliente.nombre_completo = nombre
        cliente.cedula = cedula
        cliente.telefono = telefono or None
        cliente.direccion = direccion
        cliente.referencia = referencia or None
        cliente.notas = notas or None
        db.session.commit()
        flash("Cliente actualizado", "success")
        return redirect(url_for("clientes.detalle", cliente_id=cliente.id))

    cliente_data = {
        'nombre_completo': cliente.nombre_completo,
        'cedula': cliente.cedula,
        'telefono': cliente.telefono or '',
        'direccion': cliente.direccion,
        'referencia': cliente.referencia or '',
        'notas': cliente.notas or '',
    }
    return render_template("form_clientes.html", cliente=cliente_data)




@prestamos_bp.route("/dashboard")
@login_required
def dashboard():
    activos = Prestamo.query.filter_by(estado="activo").count()
    candidatos = Prestamo.query.filter(
    Prestamo.estado.in_(["activo", "atrasado"])
    ).all()
    atrasados = sum(1 for p in candidatos if p.dias_atraso > 0)
    pagados = Prestamo.query.filter_by(estado="pagado").count()

    cartera_total = db.session.query(
        db.func.coalesce(db.func.sum(Prestamo.saldo_actual), 0)
    ).filter(Prestamo.estado.in_(["activo", "atrasado"])).scalar()

    # Aviso del día: quiénes le toca cobrar hoy y cuánto debería recoger
    candidatos = Prestamo.query.filter(
        Prestamo.estado.in_(["activo", "atrasado"])
    ).all()
    pendientes_hoy = [p for p in candidatos if p.debe_cobrarse_hoy]
    monto_esperado_hoy = sum(float(p.cuota_esperada) for p in pendientes_hoy)
    atrasados_hoy = sum(1 for p in pendientes_hoy if p.dias_atraso > 0)

    return render_template(
        "dashboard.html",
        activos=activos,
        atrasados=atrasados,
        pagados=pagados,
        cartera_total=cartera_total,
        clientes_hoy=len(pendientes_hoy),
        monto_esperado_hoy=monto_esperado_hoy,
        atrasados_hoy=atrasados_hoy,
    )


@prestamos_bp.route("/")
@login_required
def listar():
    estado = request.args.get("estado", "")
    q = request.args.get("q", "").strip()
    query = Prestamo.query.join(Prestamo.cliente).options(db.joinedload(Prestamo.cliente))

    if estado:
        query = query.filter_by(estado=estado)

    if q:
        query = query.filter(
            or_(
                Cliente.nombre_completo.ilike(f"%{q}%"),
                Cliente.cedula.ilike(f"%{q}%"),
            )
        )

    prestamos = query.order_by(Prestamo.fecha_creacion.desc()).all()
    return render_template("lista_clientes_prestamos.html", prestamos=prestamos, estado=estado, q=q)


@prestamos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    clientes_db = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre_completo).all()
    clientes = [
        {
            "id": cliente.id,
            "nombre": cliente.nombre_completo,
            "cedula": cliente.cedula,
            "telefono": cliente.telefono or "",
            "direccion": cliente.direccion or "",
            "referencia": cliente.referencia or "",
            "notas": cliente.notas or "",
        }
        for cliente in clientes_db
    ]

    if request.method == "POST":
        current_app.logger.debug("form_prestamo_cliente POST: %s", request.form.to_dict())

        cliente_id = request.form.get("cliente_id")
        nombre = request.form.get("nombre_completo", "").strip()
        cedula = request.form.get("cedula", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        referencia = request.form.get("referencia", "").strip()
        cliente_notas = request.form.get("notas", "").strip()

        monto_prestado = request.form.get("monto_prestado", "").strip()
        valor_cuota = request.form.get("valor_cuota", "").strip()
        numero_cuotas = request.form.get("numero_cuotas", "").strip()
        frecuencia_pago = request.form.get("frecuencia_pago", "diario")

        errors = []
        cliente = None

        if cliente_id:
            cliente = Cliente.query.get(int(cliente_id)) if cliente_id.isdigit() else None
            if not cliente:
                errors.append("Cliente seleccionado inválido. Vuelve a buscar.")
        else:
            if cedula and cedula.isdigit():
                posible = Cliente.query.filter_by(cedula=cedula).first()
                if posible:
                    cliente = posible
                    flash("Se usará el cliente existente con la cédula proporcionada.", "info")
            if not cliente:
                if not nombre:
                    errors.append("Nombre completo del cliente es obligatorio")
                if not cedula:
                    errors.append("Cédula del cliente es obligatoria")
                elif not cedula.isdigit() or len(cedula) > 10:
                    errors.append("Cédula inválida: sólo números, máximo 10 dígitos")
                if not telefono:
                    errors.append("Teléfono del cliente es obligatorio")
                elif not telefono.isdigit() or len(telefono) > 10:
                    errors.append("Teléfono inválido: sólo números, máximo 10 dígitos")

        try:
            monto_prestado = float(monto_prestado)
            if monto_prestado <= 0:
                raise ValueError
        except ValueError:
            errors.append("Monto prestado inválido")

        try:
            valor_cuota = float(valor_cuota)
            if valor_cuota <= 0:
                raise ValueError
        except ValueError:
            errors.append("Valor de la cuota inválido")

        try:
            numero_cuotas = int(numero_cuotas)
            if numero_cuotas < 1:
                raise ValueError
        except ValueError:
            errors.append("Número de cuotas inválido")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("form_prestamo_cliente.html", form_data=request.form, clientes=clientes)

        if not cliente:
            cliente = Cliente.query.filter_by(cedula=cedula).first()
            if not cliente:
                cliente = Cliente(
                    nombre_completo=nombre,
                    cedula=cedula,
                    telefono=telefono,
                    direccion=direccion or None,
                    referencia=referencia or None,
                    notas=cliente_notas or None,
                )
                db.session.add(cliente)
                db.session.flush()
            else:
                flash("Se usará el cliente existente con la cédula proporcionada.", "info")

        # El valor de la cuota lo escribe la persona directamente,
        # ya no se calcula a partir de una tasa de interés.
        cuota = valor_cuota
        monto_total = cuota * numero_cuotas

        hace_10_segundos = datetime.utcnow() - timedelta(seconds=10)
        duplicado = Prestamo.query.filter(
            Prestamo.cliente_id == cliente.id,
            Prestamo.monto_prestado == monto_prestado,
            Prestamo.cuota_esperada == cuota,
            Prestamo.numero_cuotas == numero_cuotas,
            Prestamo.fecha_creacion >= hace_10_segundos,
        ).first()

        if duplicado:
            flash("Este préstamo ya se había creado (se evitó un duplicado).", "warning")
            return redirect(url_for("prestamos.detalle", prestamo_id=duplicado.id))

        prestamo = Prestamo(
            cliente_id=cliente.id,
            usuario_id=current_user.id,
            monto_prestado=monto_prestado,
            tasa_interes=0,
            tipo_interes="fijo",
            frecuencia_pago=frecuencia_pago,
            numero_cuotas=numero_cuotas,
            cuota_esperada=cuota,
            monto_total_pagar=monto_total,
            saldo_actual=monto_total,
            fecha_inicio=date.today(),
            estado="activo",
        )
        db.session.add(prestamo)
        db.session.commit()

        return render_template("confirmacion_prestamo.html", prestamo=prestamo)

    return render_template("form_prestamo_cliente.html", form_data={}, clientes=clientes)


@prestamos_bp.route("/<int:prestamo_id>")
@login_required
def detalle(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    pagos = sorted(prestamo.pagos, key=lambda p: p.fecha_pago, reverse=True)
    return render_template("detalle_prestamo.html", prestamo=prestamo, pagos=pagos)