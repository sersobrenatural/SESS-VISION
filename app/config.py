import os
from datetime import datetime
from werkzeug.security import generate_password_hash

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-change-this')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_VERSION = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Configuración de administrador
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = generate_password_hash(
        os.environ.get('ADMIN_PASSWORD', 'secure-admin-password-123')
    )

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    PREFERRED_URL_SCHEME = 'https'
    
    # Base de datos para producción
    DATABASE_PATH = os.environ.get('DATABASE_URL', 'sqlite:///sessvision_prod.db')

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    DATABASE_PATH = 'sqlite:///sessvision_dev.db'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_PATH = 'sqlite:///:memory:'

# Configuración por defecto
config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}