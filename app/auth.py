from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import jwt
from functools import wraps
from werkzeug.security import check_password_hash
from app.models import Message
import bleach

auth_bp = Blueprint('auth', __name__)

# Almacenar tokens inválidos
invalid_tokens = set()

def verify_token(token):
    """Verifica si un token JWT es válido"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        if token in invalid_tokens:
            return False
        return payload
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def token_required(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token de autorización requerido'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def sanitize_input(data):
    """Sanitiza los datos de entrada para prevenir XSS"""
    if isinstance(data, str):
        return bleach.clean(data, tags=[], strip=True)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Maneja el inicio de sesión del administrador"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        # Verificar credenciales
        admin_username = current_app.config['ADMIN_USERNAME']
        admin_password_hash = current_app.config['ADMIN_PASSWORD_HASH']
        
        # Siempre usar check_password_hash
        is_valid = check_password_hash(admin_password_hash, password)
        
        if username == admin_username and is_valid:
            # Generar token JWT
            token = jwt.encode({
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({
                'message': 'Login exitoso',
                'token': token,
                'username': username
            }), 200
        else:
            return jsonify({'error': 'Credenciales incorrectas'}), 401
            
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({'error': 'Error en el servidor'}), 500

@auth_bp.route('/admin/verify', methods=['GET'])
@token_required
def verify_auth():
    """Verifica si el token es válido"""
    return jsonify({'message': 'Token válido', 'valid': True}), 200

@auth_bp.route('/admin/logout', methods=['POST'])
@token_required
def logout():
    """Invalida el token del usuario"""
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            invalid_tokens.add(token)
            return jsonify({'message': 'Sesión cerrada exitosamente'}), 200
        else:
            return jsonify({'error': 'Token no proporcionado'}), 400
            
    except Exception as e:
        print(f"Error en logout: {e}")
        return jsonify({'error': 'Error al cerrar sesión'}), 500

@auth_bp.route('/admin/messages', methods=['GET'])
@token_required
def get_messages():
    """Obtiene todos los mensajes (solo administradores)"""
    try:
        messages = Message.get_all()
        
        # Sanitizar los mensajes antes de enviarlos
        sanitized_messages = []
        for message in messages:
            sanitized_message = {
                'id': message['id'],
                'nombre': sanitize_input(message['nombre']),
                'email': sanitize_input(message['email']),
                'telefono': sanitize_input(message['telefono']),
                'servicio': sanitize_input(message['servicio']),
                'mensaje': sanitize_input(message['mensaje']),
                'fecha': message['fecha'],
                'leido': message['leido']
            }
            sanitized_messages.append(sanitized_message)
        
        return jsonify({'messages': sanitized_messages}), 200
        
    except Exception as e:
        print(f"Error al obtener mensajes: {e}")
        return jsonify({'error': 'Error al obtener mensajes'}), 500

@auth_bp.route('/admin/messages/<int:message_id>/read', methods=['PUT'])
@token_required
def mark_as_read(message_id):
    """Marca un mensaje como leído"""
    try:
        success = Message.mark_as_read(message_id)
        
        if success:
            return jsonify({'message': 'Mensaje marcado como leído'}), 200
        else:
            return jsonify({'error': 'Mensaje no encontrado'}), 404
            
    except Exception as e:
        print(f"Error al actualizar mensaje: {e}")
        return jsonify({'error': 'Error al actualizar mensaje'}), 500

@auth_bp.route('/admin/messages/<int:message_id>', methods=['DELETE'])
@token_required
def delete_message(message_id):
    """Elimina un mensaje"""
    try:
        success = Message.delete(message_id)
        
        if success:
            return jsonify({'message': 'Mensaje eliminado'}), 200
        else:
            return jsonify({'error': 'Mensaje no encontrado'}), 404
            
    except Exception as e:
        print(f"Error al eliminar mensaje: {e}")
        return jsonify({'error': 'Error al eliminar mensaje'}), 500

@auth_bp.route('/admin/stats', methods=['GET'])
@token_required
def get_stats():
    """Obtiene estadísticas de los mensajes"""
    try:
        messages = Message.get_all()
        
        total_messages = len(messages)
        unread_messages = len([m for m in messages if not m['leido']])
        read_messages = total_messages - unread_messages
        
        # Estadísticas por servicio
        service_stats = {}
        for message in messages:
            service = message['servicio']
            if service in service_stats:
                service_stats[service] += 1
            else:
                service_stats[service] = 1
        
        return jsonify({
            'stats': {
                'total': total_messages,
                'unread': unread_messages,
                'read': read_messages,
                'services': service_stats
            }
        }), 200
        
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        return jsonify({'error': 'Error al obtener estadísticas'}), 500