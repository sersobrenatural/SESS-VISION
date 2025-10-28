#!/usr/bin/env python3
"""
Script para crear administradores - Versión corregida
"""
import sys
import os
import sqlite3
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'instance', 'sessvision.db')

def init_database():
    """Inicializa la base de datos con esquema corregido"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla de administradores con esquema completo
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
    
    # Crear tabla de solicitudes
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
    
    # Crear tabla de logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            usuario TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn

def registrar_admin(username, password, nombre, email, rol='admin'):
    """Registra un nuevo administrador"""
    conn = init_database()
    cursor = conn.cursor()
    
    try:
        # Verificar si el usuario ya existe
        cursor.execute('SELECT id FROM administradores WHERE username = ?', (username,))
        if cursor.fetchone():
            return False, "El nombre de usuario ya existe"
        
        # Verificar si el email ya existe
        cursor.execute('SELECT id FROM administradores WHERE email = ?', (email,))
        if cursor.fetchone():
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
        
        return True, admin_id
        
    except Exception as e:
        conn.close()
        return False, f"Error de base de datos: {str(e)}"

def main():
    print("=" * 50)
    print("    SESS-Vision - Creación de Administrador")
    print("=" * 50)
    
    try:
        # Verificar si ya existe algún administrador
        conn = init_database()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM administradores')
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print("⚠️  Ya existen administradores en el sistema.")
            respuesta = input("¿Desea crear un nuevo administrador? (s/n): ").lower()
            if respuesta != 's':
                print("Operación cancelada.")
                return
        
        print("\nComplete los datos del nuevo administrador:")
        print("-" * 40)
        
        nombre = input("Nombre completo: ").strip()
        if not nombre:
            print("❌ Error: El nombre es obligatorio")
            return
        
        email = input("Email: ").strip()
        if not email or '@' not in email:
            print("❌ Error: El email no es válido")
            return
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("❌ Error: El nombre de usuario es obligatorio")
            return
        
        password = input("Contraseña (mínimo 6 caracteres): ").strip()
        if len(password) < 6:
            print("❌ Error: La contraseña debe tener al menos 6 caracteres")
            return
        
        confirm_password = input("Confirmar contraseña: ").strip()
        
        if password != confirm_password:
            print("❌ Error: Las contraseñas no coinciden")
            return
        
        print("\nCreando administrador...")
        success, result = registrar_admin(username, password, nombre, email)
        
        if success:
            print("✅ Administrador creado exitosamente!")
            print(f"   ID: {result}")
            print(f"   Usuario: {username}")
            print(f"   Nombre: {nombre}")
            print(f"   Email: {email}")
            print("\n📍 Ahora puede iniciar sesión en: http://127.0.0.1:5000/admin")
        else:
            print(f"❌ Error: {result}")
            
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == '__main__':
    main()