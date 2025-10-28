#!/usr/bin/env python3
"""
Script para migrar la base de datos a la nueva estructura
"""
import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'instance', 'sessvision.db')

def migrate_database():
    print("🔄 Migrando base de datos a la nueva estructura...")
    
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar si existe la columna 'rol'
        cursor.execute("PRAGMA table_info(administradores)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'rol' not in columns:
            print("➕ Agregando columna 'rol' a la tabla administradores...")
            cursor.execute("ALTER TABLE administradores ADD COLUMN rol TEXT DEFAULT 'admin'")
        
        if 'activo' not in columns:
            print("➕ Agregando columna 'activo' a la tabla administradores...")
            cursor.execute("ALTER TABLE administradores ADD COLUMN activo BOOLEAN DEFAULT 1")
        
        if 'fecha_creacion' not in columns:
            print("➕ Agregando columna 'fecha_creacion' a la tabla administradores...")
            cursor.execute("ALTER TABLE administradores ADD COLUMN fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        if 'ultimo_login' not in columns:
            print("➕ Agregando columna 'ultimo_login' a la tabla administradores...")
            cursor.execute("ALTER TABLE administradores ADD COLUMN ultimo_login TIMESTAMP NULL")
        
        # Verificar tabla de logs
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs_sistema'")
        if not cursor.fetchone():
            print("📝 Creando tabla logs_sistema...")
            cursor.execute('''
                CREATE TABLE logs_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    usuario TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        conn.commit()
        print("✅ Migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()