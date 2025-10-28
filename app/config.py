import os
from datetime import datetime
from werkzeug.security import generate_password_hash

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_VERSION = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Configuración de base de datos
    DATABASE_PATH = os.environ.get('DATABASE_URL', 'sqlite:///sessvision.db')
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

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