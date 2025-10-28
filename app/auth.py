from functools import wraps
from flask import session, redirect, url_for, request, jsonify, flash
from app.models import verificar_admin, log_sistema
import jwt
from datetime import datetime, timedelta

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorador para rutas de administración"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'No autorizado'}), 401
            return redirect(url_for('main.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def generar_token(admin_id):
    """Genera token JWT para el administrador"""
    from app import create_app
    app = create_app()
    
    payload = {
        'admin_id': admin_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verificar_token(token):
    """Verifica un token JWT"""
    from app import create_app
    app = create_app()
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None