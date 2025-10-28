# SESS-Vision - Sistema Web de Seguridad Electrónica

Sistema web empresarial profesional para SESS-Vision, empresa de seguridad electrónica con gestión de contactos y panel de administración.

## 🎯 Características

### Página Principal
- Diseño moderno y profesional
- Logo corporativo SESS-Vision
- Sección Hero con llamadas a la acción
- Catálogo completo de servicios:
  - **Video Vigilancia**: Cámaras PTZ, reconocimiento facial, térmicas, ocultas
  - **Controles de Acceso**: Biométricos, cerraduras inteligentes, lectores RFID, barreras vehiculares, detectores de placas, torniquetes
  - **Alarmas de Intrusión**: Sensores de movimiento inteligente, infrarrojos, pánico, video verificación, GPS con internet
  - **Sistemas Anti Incendios**: Detectores de humo, gas y fuego
- Formulario de contacto funcional
- Diseño responsive

### Panel de Administración
- Sistema de autenticación seguro
- Dashboard con estadísticas en tiempo real
- Gestión completa de mensajes
- Interfaz profesional

### Base de Datos
- SQLite para almacenamiento persistente
- Gestión automática de mensajes
- Sistema de marcado de lectura

## 📦 Estructura del Proyecto (Patrón MVC)

```
sessvision/
├── app/                      # Paquete principal de la aplicación
│   ├── __init__.py          # Factory de la aplicación Flask
│   ├── config.py            # Configuraciones (Dev, Prod, Test)
│   ├── models.py            # Modelos de base de datos
│   ├── routes.py            # Rutas públicas
│   ├── auth.py              # Autenticación y rutas protegidas
│   ├── static/              # Archivos estáticos
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │       └── logo.svg
│   └── templates/           # Plantillas HTML
│       ├── index.html
│       └── admin.html
├── instance/                 # Datos de instancia (DB, configuración local)
│   └── sessvision.db        # Base de datos SQLite (auto-generada)
├── run.py                    # Punto de entrada de la aplicación
├── requirements.txt          # Dependencias de Python
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Archivos ignorados por Git
├── README.md                 # Este archivo
└── DEPLOY.md                 # Guía de despliegue en producción
```

## 🚀 Instalación y Configuración
### Requisitos
- Python 3.8 o superior
- pip o uv

### Pasos de Instalación

#### 1. Clonar o descargar el proyecto
```bash
cd sessvision
```

#### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo con tus credenciales:

```bash
cp .env.example .env
```

Edita `.env`:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=tu-secret-key-muy-segura
ADMIN_USERNAME=admin
ADMIN_PASSWORD=tu-password-segura
```

**Generar SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 5. Iniciar el servidor

**Modo desarrollo:**
```bash
python run.py
```

**Modo producción con Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

#### 6. Acceder a la aplicación
- Página principal: http://localhost:5000
- Panel de administración: http://localhost:5000/admin

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambia las credenciales antes de desplegar en producción.

## 📡 API Endpoints

### Endpoints Públicos

#### `POST /api/contacto`
Envía un mensaje de contacto.

**Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "telefono": "+34 600 000 000",
  "servicio": "Video Vigilancia",
  "mensaje": "Solicito información sobre cámaras PTZ"
}
```

### Endpoints de Administración
#### `POST /api/admin/login`
Inicia sesión y obtiene token de autenticación.

**Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "message": "Login exitoso",
  "token": "abc123..."
}
```

#### `GET /api/admin/messages`
Obtiene todos los mensajes (requiere autenticación).

**Headers:**
```
Authorization: Bearer {token}
```

#### `PUT /api/admin/messages/{id}/read`
Marca un mensaje como leído.

#### `DELETE /api/admin/messages/{id}`
Elimina un mensaje.

## 🛠️ Tecnologías

### Backend
- **Flask 3.0** - Framework web
- **SQLite** - Base de datos
- **Werkzeug** - Utilidades WSGI
- **Python 3.8+** - Lenguaje de programación

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (Custom Properties)
- **JavaScript (Vanilla)** - Interactividad
- **Google Fonts (Inter)** - Tipografía
- **SVG** - Iconografía

### Arquitectura
- **Application Factory Pattern** - Patrón de diseño Flask
- **Blueprints** - Modularización de rutas
- **MVC Pattern** - Separación de responsabilidades

## 🔒 Seguridad

- Contraseñas hasheadas con SHA-256
- Tokens de autenticación basados en secrets
- Validación de datos en servidor
- Protección contra inyección SQL (parametrización)
- Variables de entorno para secretos
- CORS configurado
- Headers de seguridad

## 📄 Base de Datos

### Tabla: `mensajes`

| Campo    | Tipo      | Descripción              | Restricciones |
|----------|-----------|---------------------------|---------------|
| id       | INTEGER   | Identificador único      | PRIMARY KEY   |
| nombre   | TEXT      | Nombre del cliente        | NOT NULL      |
| email    | TEXT      | Correo electrónico       | NOT NULL      |
| telefono | TEXT      | Teléfono de contacto     | NOT NULL      |
| servicio | TEXT      | Servicio de interés     | NOT NULL      |
| mensaje  | TEXT      | Contenido del mensaje     | NOT NULL      |
| fecha    | TIMESTAMP | Fecha y hora de envío    | DEFAULT NOW   |
| leido    | BOOLEAN   | Estado de lectura         | DEFAULT FALSE |

## 🌐 Despliegue en Producción

Consulta el archivo <filepath>DEPLOY.md</filepath> para instrucciones detalladas de despliegue con:

- Gunicorn + Systemd
- Nginx como proxy reverso
- Docker
- Configuración HTTPS
- Optimizaciones de rendimiento

## 🎨 Personalización

### Cambiar Colores del Tema

Edita las variables CSS en `app/templates/index.html` y `admin.html`:

```css
:root {
    --primary-500: #0066CC;  /* Color principal */
    --primary-700: #004C99;  /* Color hover */
    --neutral-900: #0F172A;  /* Texto principal */
}
```

### Añadir Nuevos Servicios

Edita `app/templates/index.html` dentro de la sección `.services-grid`.

### Modificar el Logo

Reemplaza `app/static/images/logo.svg` con tu logo personalizado.

## 📚 Documentación Adicional

- <filepath>DEPLOY.md</filepath> - Guía de despliegue en producción
- <filepath>.env.example</filepath> - Variables de entorno disponibles
- <filepath>app/config.py</filepath> - Configuraciones del sistema

## 📝 Scripts Útiles

### Crear secret key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Hash de contraseña (para variables de entorno)
```bash
echo -n 'mi_password' | sha256sum | cut -d' ' -f1
```

### Backup de base de datos
```bash
cp instance/sessvision.db instance/backup_$(date +%Y%m%d_%H%M%S).db
```

### Ver logs en producción (systemd)
```bash
sudo journalctl -u sessvision -f
```

## 🤝 Soporte

Para soporte técnico o consultas:
- Email: soporte@sess-vision.com
- Web: www.sess-vision.com

## 📜 Licencia

© 2025 SESS-Vision - Seguridad Electrónica Profesional. Todos los derechos reservados.

---

**Sistema listo para producción ✅**

Diseñado y desarrollado con ❤️ por el equipo de SESS-Vision.
