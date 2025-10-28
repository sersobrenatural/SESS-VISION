import sqlite3
import os
from datetime import datetime

def get_db_path():
    return os.path.join(os.path.dirname(__file__), '..', 'instance', 'sessvision.db')

def init_db():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT NOT NULL,
            servicio TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            leido BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def guardar_solicitud(nombre, email, telefono, servicio, mensaje):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO solicitudes (nombre, email, telefono, servicio, mensaje)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, email, telefono, servicio, mensaje))
    
    conn.commit()
    solicitud_id = cursor.lastrowid
    conn.close()
    return solicitud_id

def obtener_solicitudes():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nombre, email, telefono, servicio, mensaje, 
               datetime(fecha) as fecha, leido
        FROM solicitudes 
        ORDER BY fecha DESC
    ''')
    
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
            'leido': bool(row[7])
        })
    
    conn.close()
    return solicitudes

def marcar_como_leido(solicitud_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('UPDATE solicitudes SET leido = 1 WHERE id = ?', (solicitud_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def eliminar_solicitud(solicitud_id):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('DELETE FROM solicitudes WHERE id = ?', (solicitud_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success