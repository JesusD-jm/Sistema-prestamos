import os
import sys
from flask import Flask
from flask_login import LoginManager

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from archivos_principales.config import Config
from archivos_principales.models import db, Usuario

from rutas.autenticacion import auth_bp
from rutas.clientes_prestamos import prestamos_bp, clientes_bp
from rutas.pagos import pagos_bp
from rutas.ruta import ruta_bp
from rutas.clientes_prestamos import prestamos_bp, clientes_bp

def create_app():
    # serve templates from project-level folder and static files from project-level `static/`
    app = Flask(__name__, template_folder="../plantillas_HTML", static_folder="../static", static_url_path='/static')
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(prestamos_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(ruta_bp)


    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('prestamos.dashboard'))
        

    return app

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        db.create_all()

    import threading
    import webbrowser

    def abrir_navegador():
        webbrowser.open_new("http://127.0.0.1:5000")

    threading.Timer(2, abrir_navegador).start()

    print("Servidor Flask iniciado. Abriendo navegador...")

    app.run(debug=True, use_reloader=False)