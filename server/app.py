from flask import Flask
from config import Config
from models import db, SystemStatus
from routes import main_bp, admin_bp, api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar banco de dados
    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Criar tabelas
    with app.app_context():
        db.create_all()
        # Inicializar SystemStatus se não existir
        if not SystemStatus.query.first():
            status = SystemStatus()
            db.session.add(status)
            db.session.commit()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=app.config["PORT"])
