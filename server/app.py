from flask import Flask, render_template, jsonify, request
from config import Config
from models import db, SystemStatus
from routes import main_bp, admin_bp, api_bp, cliente_bp
import logging
from logging.handlers import RotatingFileHandler
import os
import time


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configurar logging diferenciado por ambiente
    configure_logging(app)

    # Request logging middleware
    @app.before_request
    def log_request():
        """Log de todas as requisições"""
        request.start_time = time.time()
    
    @app.after_request
    def log_response(response):
        """Log de todas as respostas com tempo de processamento"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            app.logger.info(
                f'{request.method} {request.path} - {response.status_code} - {duration:.3f}s - IP: {request.remote_addr}'
            )
        return response

    # Inicializar banco de dados
    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(cliente_bp)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Recurso não encontrado'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Erro interno: {error}', exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Erro interno do servidor'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Acesso negado'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(413)
    def too_large_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Arquivo muito grande'}), 413
        return render_template('errors/413.html'), 413

    # Criar tabelas
    with app.app_context():
        db.create_all()
        # Inicializar SystemStatus se não existir
        if not SystemStatus.query.first():
            status = SystemStatus()
            db.session.add(status)
            db.session.commit()

    return app


def configure_logging(app):
    """Configura logging com níveis diferentes para dev/prod"""
    
    # Criar diretório de logs se não existir
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configuração baseada no ambiente
    is_production = not app.debug
    
    if is_production:
        # Produção: logs mais detalhados
        file_handler = RotatingFileHandler(
            'logs/propaganda.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Log de erros separado
        error_handler = RotatingFileHandler(
            'logs/propaganda_errors.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        error_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s'
        ))
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema de Propaganda iniciado em modo PRODUÇÃO')
    else:
        # Desenvolvimento: logs mais verbosos no console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        
        # Arquivo de debug
        debug_handler = RotatingFileHandler(
            'logs/propaganda_debug.log',
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        debug_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s'
        ))
        debug_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(debug_handler)
        
        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Sistema de Propaganda iniciado em modo DESENVOLVIMENTO')


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=app.config["PORT"])
