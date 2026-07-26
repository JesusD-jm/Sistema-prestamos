"""
Script para crear el primer usuario administrador.
Ejecutar una sola vez: python CSS_y_Script/crearAdmin.py
"""
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.insert(0, project_root)

from werkzeug.security import generate_password_hash
from archivos_principales.app import create_app
from archivos_principales.models import db, Usuario

app = create_app()

with app.app_context():
    db.create_all()

    if Usuario.query.first():
        print("Ya existe un usuario en la base de datos. No se creará otro.")
    else:
        nombre = input("Nombre completo: ")
        usuario = input("Usuario (para iniciar sesión): ")
        password = input("Contraseña: ")

        nuevo_usuario = Usuario(
            nombre=nombre,
            usuario=usuario,
            password_hash=generate_password_hash(password),
            activo=True,
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(f"Usuario '{usuario}' creado correctamente.")
