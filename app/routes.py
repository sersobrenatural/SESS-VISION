from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import guardar_solicitud, obtener_solicitudes, marcar_como_leido, eliminar_solicitud

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

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

@main_bp.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        from werkzeug.security import check_password_hash
        from app.config import config
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        current_config = config['default']
        if (username == current_config.ADMIN_USERNAME and 
            check_password_hash(current_config.ADMIN_PASSWORD_HASH, password)):
            session['admin_logged_in'] = True
            return redirect(url_for('main.admin'))
        else:
            return render_template('admin.html', error='Credenciales incorrectas')
    
    if not session.get('admin_logged_in'):
        return render_template('admin.html')
    
    solicitudes = obtener_solicitudes()
    return render_template('admin.html', solicitudes=solicitudes, logged_in=True)

@main_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('main.admin'))

@main_bp.route('/api/solicitud', methods=['POST'])
def crear_solicitud():
    try:
        data = request.get_json()
        
        required_fields = ['nombre', 'email', 'telefono', 'servicio', 'mensaje']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
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
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

@main_bp.route('/api/admin/marcar_leido/<int:solicitud_id>')
def marcar_leido(solicitud_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    success = marcar_como_leido(solicitud_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Solicitud no encontrada'}), 404

@main_bp.route('/api/admin/eliminar/<int:solicitud_id>')
def eliminar(solicitud_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    success = eliminar_solicitud(solicitud_id)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Solicitud no encontrada'}), 404

@main_bp.route('/health-check')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'SESS-Vision'})