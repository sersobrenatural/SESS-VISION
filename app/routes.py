from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from app.models import (
    guardar_solicitud, obtener_solicitudes, obtener_estadisticas,
    marcar_como_leido, actualizar_estado, eliminar_solicitud, 
    verificar_admin, registrar_admin, obtener_administradores, actualizar_estado_admin, log_sistema
)
from app.auth import admin_required
import json
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

# ===== RUTAS PÚBLICAS =====
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/admin')
def admin_redirect():
    """Redirige /admin al dashboard o login según autenticación"""
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin_dashboard'))
    else:
        return redirect(url_for('main.admin_login'))

@main_bp.route('/servicios/video-vigilancia')
def video_vigilancia():
    return render_template('services/video_vigilancia.html')

@main_bp.route('/servicios/controles-acceso')
def controles_acceso():
    return render_template('services/controles_acceso.html')

@main_bp.route('/servicios/alarmas-intrusion')
def alarmas_intrusion():
    return render_template('services/alarmas_intrusion.html')

@main_bp.route('/servicios/sistemas-anti-incendios')
def sistemas_anti_incendios():
    return render_template('services/sistemas_anti_incendios.html')

@main_bp.route('/api/solicitud', methods=['POST'])
def crear_solicitud():
    try:
        data = request.get_json()
        
        required_fields = ['nombre', 'email', 'telefono', 'servicio', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Validar email
        if '@' not in data['email']:
            return jsonify({'error': 'El email no es válido'}), 400
        
        solicitud_id = guardar_solicitud(
            data['nombre'],
            data['email'],
            data['telefono'],
            data['servicio'],
            data['mensaje']
        )
        
        return jsonify({
            'success': True,
            'message': '¡Solicitud enviada exitosamente! Nos pondremos en contacto pronto.',
            'id': solicitud_id
        }), 200
        
    except Exception as e:
        log_sistema('error', f'Error al crear solicitud: {str(e)}')
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

# ===== RUTAS DE AUTENTICACIÓN MEJORADAS =====
@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Si ya está logueado, redirigir al dashboard
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = verificar_admin(username, password)
        if admin:
            session['admin_logged_in'] = True
            session['admin_id'] = admin['id']
            session['admin_nombre'] = admin['nombre']
            session['admin_username'] = admin['username']
            session['admin_rol'] = admin['rol']
            
            log_sistema('login', f'Inicio de sesión exitoso: {admin["nombre"]}', admin['username'])
            flash('Inicio de sesión exitoso', 'success')
            
            # Redirigir al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.admin_dashboard'))
        else:
            log_sistema('login', f'Intento de inicio de sesión fallido: {username}', 'sistema')
            flash('Credenciales incorrectas', 'error')
    
    return render_template('admin/login.html')

@main_bp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    # Si ya está logueado, redirigir al dashboard
    if session.get('admin_logged_in'):
        return redirect(url_for('main.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        
        # Validaciones básicas
        if not all([username, password, confirm_password, nombre, email]):
            flash('Todos los campos son obligatorios', 'error')
            return render_template('admin/register.html')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('admin/register.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
            return render_template('admin/register.html')
        
        # Registrar nuevo administrador
        success, result = registrar_admin(username, password, nombre, email)
        
        if success:
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('main.admin_login'))
        else:
            flash(result, 'error')  # result contiene el mensaje de error
    
    return render_template('admin/register.html')

@main_bp.route('/admin/logout')
def admin_logout():
    if session.get('admin_logged_in'):
        log_sistema('logout', f'Cierre de sesión: {session.get("admin_nombre")}', session.get('admin_username'))
    
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('main.admin_login'))

# ===== RUTAS DE ADMINISTRACIÓN =====
@main_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    estadisticas = obtener_estadisticas()
    
    # Obtener solicitudes recientes (últimas 5)
    solicitudes_recientes = obtener_solicitudes(orden='fecha_desc')[:5]
    
    return render_template('admin/dashboard.html',
                         estadisticas=estadisticas,
                         solicitudes_recientes=solicitudes_recientes,
                         admin_nombre=session.get('admin_nombre'))

@main_bp.route('/admin/solicitudes')
@admin_required
def admin_solicitudes():
    # Filtros
    filtro_estado = request.args.get('estado', 'todos')
    filtro_servicio = request.args.get('servicio', 'todos')
    orden = request.args.get('orden', 'fecha_desc')
    
    solicitudes = obtener_solicitudes(filtro_estado, filtro_servicio, orden)
    
    return render_template('admin/solicitudes.html',
                         solicitudes=solicitudes,
                         filtro_estado=filtro_estado,
                         filtro_servicio=filtro_servicio,
                         orden=orden,
                         admin_nombre=session.get('admin_nombre'))

# ===== GESTIÓN DE ADMINISTRADORES =====
@main_bp.route('/admin/administradores')
@admin_required
def admin_administradores():
    """Panel de gestión de administradores"""
    if session.get('admin_rol') != 'superadmin':
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    administradores = obtener_administradores()
    return render_template('admin/administradores.html',
                         administradores=administradores,
                         admin_nombre=session.get('admin_nombre'))

@main_bp.route('/api/admin/toggle_admin/<int:admin_id>', methods=['POST'])
@admin_required
def api_toggle_admin(admin_id):
    """Activa/desactiva un administrador"""
    if session.get('admin_rol') != 'superadmin':
        return jsonify({'error': 'No autorizado'}), 403
    
    try:
        data = request.get_json()
        activo = data.get('activo', False)
        
        success = actualizar_estado_admin(admin_id, activo)
        if success:
            estado = "activado" if activo else "desactivado"
            return jsonify({'success': True, 'message': f'Administrador {estado} correctamente'})
        else:
            return jsonify({'error': 'Administrador no encontrado'}), 404
    except Exception as e:
        log_sistema('error', f'Error al cambiar estado de administrador: {str(e)}', session.get('admin_username'))
        return jsonify({'error': 'Error interno del servidor'}), 500

# ===== API DEL PANEL DE ADMINISTRACIÓN =====
@main_bp.route('/api/admin/marcar_leido/<int:solicitud_id>', methods=['POST'])
@admin_required
def api_marcar_leido(solicitud_id):
    try:
        success = marcar_como_leido(solicitud_id)
        if success:
            return jsonify({'success': True, 'message': 'Solicitud marcada como leída'})
        else:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
    except Exception as e:
        log_sistema('error', f'Error al marcar como leído: {str(e)}', session.get('admin_username'))
        return jsonify({'error': 'Error interno del servidor'}), 500

@main_bp.route('/api/admin/actualizar_estado/<int:solicitud_id>', methods=['POST'])
@admin_required
def api_actualizar_estado(solicitud_id):
    try:
        data = request.get_json()
        estado = data.get('estado')
        notas = data.get('notas', '')
        
        if estado not in ['pendiente', 'contactado', 'cerrado']:
            return jsonify({'error': 'Estado no válido'}), 400
        
        success = actualizar_estado(solicitud_id, estado, notas)
        if success:
            return jsonify({'success': True, 'message': f'Estado actualizado a {estado}'})
        else:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
    except Exception as e:
        log_sistema('error', f'Error al actualizar estado: {str(e)}', session.get('admin_username'))
        return jsonify({'error': 'Error interno del servidor'}), 500

@main_bp.route('/api/admin/eliminar/<int:solicitud_id>', methods=['POST'])
@admin_required
def api_eliminar_solicitud(solicitud_id):
    try:
        success = eliminar_solicitud(solicitud_id)
        if success:
            return jsonify({'success': True, 'message': 'Solicitud eliminada'})
        else:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
    except Exception as e:
        log_sistema('error', f'Error al eliminar solicitud: {str(e)}', session.get('admin_username'))
        return jsonify({'error': 'Error interno del servidor'}), 500

@main_bp.route('/api/admin/estadisticas')
@admin_required
def api_estadisticas():
    try:
        estadisticas = obtener_estadisticas()
        return jsonify(estadisticas)
    except Exception as e:
        log_sistema('error', f'Error al obtener estadísticas: {str(e)}', session.get('admin_username'))
        return jsonify({'error': 'Error interno del servidor'}), 500

@main_bp.route('/health-check')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'SESS-Vision',
        'timestamp': datetime.utcnow().isoformat()
    })