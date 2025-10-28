import sqlite3
import os
from datetime import datetime, timedelta
import json
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_path():
    return os.path.join(os.path.dirname(__file__), '..', 'instance', 'sessvision.db')

def log_sistema(tipo, mensaje, usuario=None):
    """Registra un evento en el log del sistema"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logs_sistema (tipo, mensaje, usuario)
        VALUES (?, ?, ?)
    ''', (tipo, mensaje, usuario))
    
    conn.commit()
    conn.close()

def init_db():
    """Inicializa la base de datos con tablas mejoradas"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla de solicitudes mejorada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT NOT NULL,
            servicio TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leido BOOLEAN DEFAULT 0,
            prioridad INTEGER DEFAULT 1,
            estado TEXT DEFAULT 'pendiente',
            notas TEXT DEFAULT '',
            fecha_contacto TIMESTAMP NULL,
            fecha_cierre TIMESTAMP NULL
        )
    ''')
    
    # Tabla de administradores mejorada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            rol TEXT DEFAULT 'admin',
            activo BOOLEAN DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_login TIMESTAMP NULL
        )
    ''')
    
    # Tabla de logs del sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            usuario TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # NO crear administrador por defecto
    conn.commit()
    conn.close()
    
    log_sistema('sistema', 'Base de datos inicializada correctamente')

def guardar_solicitud(nombre, email, telefono, servicio, mensaje):
    """Guarda una nueva solicitud de servicio"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Determinar prioridad automáticamente
    prioridad = 1  # baja por defecto
    palabras_urgentes = ['urgente', 'emergencia', 'inmediato', 'ya', 'ahora']
    if any(palabra in mensaje.lower() for palabra in palabras_urgentes):
        prioridad = 3  # alta
    
    cursor.execute('''
        INSERT INTO solicitudes (nombre, email, telefono, servicio, mensaje, prioridad)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, email, telefono, servicio, mensaje, prioridad))
    
    conn.commit()
    solicitud_id = cursor.lastrowid
    conn.close()
    
    # Log del sistema
    log_sistema('solicitud', f'Nueva solicitud de {nombre} para {servicio}', 'sistema')
    
    return solicitud_id

def obtener_solicitudes(filtro_estado=None, filtro_servicio=None, orden='fecha_desc'):
    """Obtiene solicitudes con filtros y ordenación"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    query = '''
        SELECT id, nombre, email, telefono, servicio, mensaje, 
               datetime(fecha) as fecha, leido, prioridad, estado, notas,
               datetime(fecha_contacto) as fecha_contacto,
               datetime(fecha_cierre) as fecha_cierre
        FROM solicitudes 
    '''
    
    params = []
    where_conditions = []
    
    if filtro_estado and filtro_estado != 'todos':
        where_conditions.append('estado = ?')
        params.append(filtro_estado)
    
    if filtro_servicio and filtro_servicio != 'todos':
        where_conditions.append('servicio = ?')
        params.append(filtro_servicio)
    
    if where_conditions:
        query += ' WHERE ' + ' AND '.join(where_conditions)
    
    # Ordenación
    if orden == 'fecha_desc':
        query += ' ORDER BY fecha DESC'
    elif orden == 'fecha_asc':
        query += ' ORDER BY fecha ASC'
    elif orden == 'prioridad_desc':
        query += ' ORDER BY prioridad DESC, fecha DESC'
    elif orden == 'nombre_asc':
        query += ' ORDER BY nombre ASC'
    
    cursor.execute(query, params)
    
    solicitudes = []
    for row in cursor.fetchall():
        solicitudes.append({
            'id': row[0],
            'nombre': row[1],
            'email': row[2],
            'telefono': row[3],
            'servicio': row[4],
            'mensaje': row[5],
            'fecha': row[6],
            'leido': bool(row[7]),
            'prioridad': row[8],
            'estado': row[9],
            'notas': row[10],
            'fecha_contacto': row[11],
            'fecha_cierre': row[12]
        })
    
    conn.close()
    return solicitudes

def obtener_estadisticas():
    """Obtiene estadísticas para el dashboard"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Total solicitudes
    cursor.execute('SELECT COUNT(*) FROM solicitudes')
    total = cursor.fetchone()[0]
    
    # Solicitudes no leídas
    cursor.execute('SELECT COUNT(*) FROM solicitudes WHERE leido = 0')
    no_leidas = cursor.fetchone()[0]
    
    # Solicitudes por estado
    cursor.execute('SELECT estado, COUNT(*) FROM solicitudes GROUP BY estado')
    por_estado = dict(cursor.fetchall())
    
    # Solicitudes por servicio
    cursor.execute('SELECT servicio, COUNT(*) FROM solicitudes GROUP BY servicio')
    por_servicio = dict(cursor.fetchall())
    
    # Solicitudes de los últimos 7 días
    cursor.execute('''
        SELECT DATE(fecha), COUNT(*) 
        FROM solicitudes 
        WHERE fecha >= date('now', '-7 days')
        GROUP BY DATE(fecha)
    ''')
    ultimos_7_dias = dict(cursor.fetchall())
    
    conn.close()
    
    return {
        'total': total,
        'no_leidas': no_leidas,
        'por_estado': por_estado,
        'por_servicio': por_servicio,
        'ultimos_7_dias': ultimos_7_dias
    }

def marcar_como_leido(solicitud_id):
    """Marca una solicitud como leída"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('UPDATE solicitudes SET leido = 1 WHERE id = ?', (solicitud_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_sistema('solicitud', f'Solicitud {solicitud_id} marcada como leída')
    
    return success

def actualizar_estado(solicitud_id, estado, notas=''):
    """Actualiza el estado de una solicitud"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    if estado == 'contactado':
        cursor.execute('''
            UPDATE solicitudes 
            SET estado = ?, notas = ?, fecha_contacto = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (estado, notas, solicitud_id))
    elif estado == 'cerrado':
        cursor.execute('''
            UPDATE solicitudes 
            SET estado = ?, notas = ?, fecha_cierre = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (estado, notas, solicitud_id))
    else:
        cursor.execute('''
            UPDATE solicitudes 
            SET estado = ?, notas = ? 
            WHERE id = ?
        ''', (estado, notas, solicitud_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        log_sistema('solicitud', f'Solicitud {solicitud_id} actualizada a estado: {estado}')
    
    return success

def eliminar_solicitud(solicitud_id):
    """Elimina una solicitud"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Primero obtenemos los datos para el log
    cursor.execute('SELECT nombre, servicio FROM solicitudes WHERE id = ?', (solicitud_id,))
    resultado = cursor.fetchone()
    
    cursor.execute('DELETE FROM solicitudes WHERE id = ?', (solicitud_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success and resultado:
        log_sistema('solicitud', f'Solicitud eliminada: {resultado[0]} - {resultado[1]}')
    
    return success

def registrar_admin(username, password, nombre, email, rol='admin'):
    """Registra un nuevo administrador"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Verificar si el usuario ya existe
    cursor.execute('SELECT id FROM administradores WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return False, "El nombre de usuario ya existe"
    
    # Verificar si el email ya existe
    cursor.execute('SELECT id FROM administradores WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return False, "El email ya está registrado"
    
    # Crear hash de la contraseña
    password_hash = generate_password_hash(password)
    
    # Insertar nuevo administrador
    cursor.execute('''
        INSERT INTO administradores (username, password_hash, nombre, email, rol)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, password_hash, nombre, email, rol))
    
    conn.commit()
    admin_id = cursor.lastrowid
    conn.close()
    
    log_sistema('registro', f'Nuevo administrador registrado: {nombre} ({username})')
    return True, admin_id

def verificar_admin(username, password):
    """Verifica las credenciales del administrador y actualiza último login"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, password_hash, nombre, email, rol, activo 
        FROM administradores 
        WHERE username = ? AND activo = 1
    ''', (username,))
    
    admin = cursor.fetchone()
    
    if admin and check_password_hash(admin[2], password):
        # Actualizar último login
        cursor.execute('''
            UPDATE administradores 
            SET ultimo_login = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (admin[0],))
        conn.commit()
        
        admin_data = {
            'id': admin[0],
            'username': admin[1],
            'nombre': admin[3],
            'email': admin[4],
            'rol': admin[5]
        }
        conn.close()
        return admin_data
    
    conn.close()
    return None

def obtener_administradores():
    """Obtiene todos los administradores (excepto contraseñas)"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, username, nombre, email, rol, activo, fecha_creacion, ultimo_login
        FROM administradores 
        ORDER BY fecha_creacion DESC
    ''')
    
    admins = []
    for row in cursor.fetchall():
        admins.append({
            'id': row[0],
            'username': row[1],
            'nombre': row[2],
            'email': row[3],
            'rol': row[4],
            'activo': bool(row[5]),
            'fecha_creacion': row[6],
            'ultimo_login': row[7]
        })
    
    conn.close()
    return admins

def actualizar_estado_admin(admin_id, activo):
    """Activa o desactiva un administrador"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE administradores 
        SET activo = ? 
        WHERE id = ?
    ''', (activo, admin_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    if success:
        estado = "activado" if activo else "desactivado"
        log_sistema('admin', f'Administrador {admin_id} {estado}')
    
    return success

def obtener_primer_admin():
    """Verifica si existe al menos un administrador en el sistema"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM administradores')
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0