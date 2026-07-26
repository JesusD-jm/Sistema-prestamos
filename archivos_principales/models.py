from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


DIAS_POR_FRECUENCIA = {
    "diario": 1,
    "semanal": 7,
    "quincenal": 15,
    "mensual": 30,
}


db = SQLAlchemy()


# =========================================================
# USUARIO
# =========================================================

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100),
        nullable=False
    )

    usuario = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# CLIENTE
# =========================================================

class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre_completo = db.Column(
        db.String(150),
        nullable=False
    )

    cedula = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    telefono = db.Column(
        db.String(20),
        nullable=False
    )

    direccion = db.Column(
        db.String(255)
    )

    referencia = db.Column(
        db.String(255)
    )

    foto = db.Column(
        db.String(255)
    )

    fecha_registro = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    notas = db.Column(
        db.Text
    )

    prestamos = db.relationship(
        "Prestamo",
        backref="cliente",
        lazy=True
    )


# =========================================================
# PRÉSTAMO
# =========================================================

class Prestamo(db.Model):
    __tablename__ = "prestamos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    monto_prestado = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    tasa_interes = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )

    tipo_interes = db.Column(
        db.Enum(
            "fijo",
            "sobre_saldo"
        ),
        default="fijo"
    )

    frecuencia_pago = db.Column(
        db.Enum(
            "diario",
            "semanal",
            "quincenal",
            "mensual"
        ),
        default="diario"
    )

    numero_cuotas = db.Column(
        db.Integer,
        nullable=False
    )

    # =====================================================
    # FECHA QUE SELECCIONA EL USUARIO
    # =====================================================

    fecha_prestamo = db.Column(
        db.Date,
        nullable=False
    )

    cuota_esperada = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    monto_total_pagar = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    saldo_actual = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    # Se mantiene esta columna porque ya existe
    # en tu base de datos.
    # Debe guardar la misma fecha que fecha_prestamo.
    fecha_inicio = db.Column(
        db.Date,
        nullable=False
    )

    fecha_fin_estimada = db.Column(
        db.Date
    )

    estado = db.Column(
        db.Enum(
            "activo",
            "atrasado",
            "pagado",
            "cancelado"
        ),
        default="activo"
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    pagos = db.relationship(
        "Pago",
        backref="prestamo",
        lazy=True
    )


    # =====================================================
    # CALCULAR MONTOS
    # =====================================================

    @staticmethod
    def calcular_montos(
        monto_prestado,
        tasa_interes,
        numero_cuotas
    ):

        interes_total = (
            float(monto_prestado)
            * (
                float(tasa_interes)
                / 100
            )
        )

        monto_total_sin_redondear = (
            float(monto_prestado)
            + interes_total
        )

        cuota = round(
            monto_total_sin_redondear
            / numero_cuotas
        )

        monto_total = (
            cuota
            * numero_cuotas
        )

        return monto_total, cuota


    # =====================================================
    # TOTAL PAGADO
    # =====================================================

    @property
    def total_pagado(self):

        return sum(
            float(p.monto_pagado)
            for p in self.pagos
        )


    # =====================================================
    # CUOTAS COMPLETADAS
    # =====================================================

    @property
    def cuotas_completadas(self):

        if (
            not self.cuota_esperada
            or float(self.cuota_esperada) == 0
        ):
            return 0

        return int(
            self.total_pagado
            // float(self.cuota_esperada)
        )


    # =====================================================
    # PRÓXIMA FECHA DE PAGO
    # =====================================================

    @property
    def proxima_fecha_pago(self):

        dias = DIAS_POR_FRECUENCIA.get(self.frecuencia_pago, 1)
        fecha_base = self.fecha_prestamo or self.fecha_inicio

        if isinstance(fecha_base, str):
            fecha_base = datetime.strftime(fecha_base, "%Y-%m-%d").date()

        # Usamos la fecha seleccionada
        # por el usuario.
        fecha_base = (
            self.fecha_prestamo
            or self.fecha_inicio
        )

        return (
            fecha_base + timedelta(
                days=(dias * (self.cuotas_completadas+ 1))
            )
        )


    # =====================================================
    # DÍAS DE ATRASO
    # =====================================================

    @property
    def dias_atraso(self):

        if self.estado == "pagado":
            return 0

        diferencia = (
            date.today()
            - self.proxima_fecha_pago
        ).days

        return max(
            diferencia,
            0
        )


    # =====================================================
    # DEBE COBRARSE HOY
    # =====================================================

    @property
    def debe_cobrarse_hoy(self):

        if self.estado in (
            "pagado",
            "cancelado"
        ):
            return False

        return (
            self.proxima_fecha_pago
            <= date.today()
        )


# =========================================================
# PAGO
# =========================================================

class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    prestamo_id = db.Column(
        db.Integer,
        db.ForeignKey("prestamos.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    monto_pagado = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    redito = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    saldo_despues = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    fecha_pago = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Fecha/hora REAL en que se registró el pago en el sistema.
    # Distinta de fecha_pago, que ahora la escribe la persona
    # manualmente y puede ser una fecha antigua (clientes viejos).
    creado_en = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    metodo_pago = db.Column(
        db.Enum(
            "efectivo",
            "transferencia",
            "otro"
        ),
        default="efectivo"
    )

    notas = db.Column(
        db.String(255)
    )


# =========================================================
# RUTA DE COBRO
# =========================================================

class RutaCobro(db.Model):
    __tablename__ = "ruta_cobro"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    prestamo_id = db.Column(
        db.Integer,
        db.ForeignKey("prestamos.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    fecha = db.Column(
        db.Date,
        nullable=False
    )

    visitado = db.Column(
        db.Boolean,
        default=False
    )

    pago_id = db.Column(
        db.Integer,
        db.ForeignKey("pagos.id")
    )
