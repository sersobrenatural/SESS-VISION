from flask import Flask
from flask_compress import Compress
import os

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Determinar configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    # Cargar configuración
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    compress = Compress()
    compress.init_app(app)
    
    # Configurar manejo de errores
    if not app.debug and not app.testing:
        configure_production_logging(app)
    
    # Inicializar base de datos
    with app.app_context():
        from app.models import init_db
        init_db()
    
    # Registrar blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Headers de seguridad
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if app.config['PREFERRED_URL_SCHEME'] == 'https':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    return app

def configure_production_logging(app):
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/sessvision.log', 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SESS-Vision startup')