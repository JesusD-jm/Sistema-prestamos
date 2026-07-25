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


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(255))
    referencia = db.Column(db.String(255))
    foto = db.Column(db.String(255))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    notas = db.Column(db.Text)

    prestamos = db.relationship("Prestamo", backref="cliente", lazy=True)


class Prestamo(db.Model):
    __tablename__ = "prestamos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    monto_prestado = db.Column(db.Numeric(12, 2), nullable=False)
    tasa_interes = db.Column(db.Numeric(5, 2), nullable=False)
    tipo_interes = db.Column(db.Enum("fijo", "sobre_saldo"), default="fijo")
    frecuencia_pago = db.Column(
        db.Enum("diario", "semanal", "quincenal", "mensual"), default="diario"
    )
    numero_cuotas = db.Column(db.Integer, nullable=False)
    cuota_esperada = db.Column(db.Numeric(12, 2), nullable=False)
    monto_total_pagar = db.Column(db.Numeric(12, 2), nullable=False)
    saldo_actual = db.Column(db.Numeric(12, 2), nullable=False)

    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin_estimada = db.Column(db.Date)
    estado = db.Column(
        db.Enum("activo", "atrasado", "pagado", "cancelado"), default="activo"
    )
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    pagos = db.relationship("Pago", backref="prestamo", lazy=True)

    @staticmethod
    def calcular_montos(monto_prestado, tasa_interes, numero_cuotas):
        interes_total = float(monto_prestado) * (float(tasa_interes) / 100)
        monto_total_sin_redondear = float(monto_prestado) + interes_total
        cuota = round(monto_total_sin_redondear / numero_cuotas)
        monto_total = cuota * numero_cuotas
        return monto_total, cuota

    @property
    def total_pagado(self):
        """Suma de todos los abonos hechos a este préstamo, sin importar el monto de cada uno."""
        return sum(float(p.monto_pagado) for p in self.pagos)

    @property
    def cuotas_completadas(self):
        """
        Cuántas cuotas están realmente cubiertas por el monto acumulado.
        Un abono parcial (menor a la cuota) NO cuenta como cuota completa.
        """
        if not self.cuota_esperada or float(self.cuota_esperada) == 0:
            return 0
        return int(self.total_pagado // float(self.cuota_esperada))

    @property
    def proxima_fecha_pago(self):
        """
        Calcula cuándo debería ser el próximo pago, usando el monto
        acumulado (no el número de pagos) para saber cuántas cuotas
        están realmente cubiertas. Así, un abono parcial no adelanta
        la fecha del siguiente cobro.
        """
        dias = DIAS_POR_FRECUENCIA.get(self.frecuencia_pago, 1)
        return self.fecha_inicio + timedelta(days=dias * (self.cuotas_completadas + 1))

    @property
    def dias_atraso(self):
        """Cuántos días lleva vencida la cuota (0 si no está vencida o ya se pagó)."""
        if self.estado == "pagado":
            return 0
        diferencia = (date.today() - self.proxima_fecha_pago).days
        return max(diferencia, 0)

    @property
    def debe_cobrarse_hoy(self):
        """True si hoy le toca cobrar a este cliente (a tiempo o atrasado)."""
        if self.estado in ("pagado", "cancelado"):
            return False
        return self.proxima_fecha_pago <= date.today()


class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True)
    prestamo_id = db.Column(db.Integer, db.ForeignKey("prestamos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    monto_pagado = db.Column(db.Numeric(12, 2), nullable=False)
    redito = db.Column(db.Numeric(12, 2), nullable=True)
    saldo_despues = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    metodo_pago = db.Column(
        db.Enum("efectivo", "transferencia", "otro"), default="efectivo"
    )
    notas = db.Column(db.String(255))


class RutaCobro(db.Model):
    __tablename__ = "ruta_cobro"

    id = db.Column(db.Integer, primary_key=True)
    prestamo_id = db.Column(db.Integer, db.ForeignKey("prestamos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    visitado = db.Column(db.Boolean, default=False)
    pago_id = db.Column(db.Integer, db.ForeignKey("pagos.id"))