// Funciones para el panel de administración
document.addEventListener('DOMContentLoaded', function() {
    setupAdminEventListeners();
});

function setupAdminEventListeners() {
    // Botones de "Marcar como Leído"
    document.querySelectorAll('.mark-read-btn').forEach(button => {
        button.addEventListener('click', function() {
            const solicitudId = this.getAttribute('data-solicitud-id');
            marcarComoLeido(solicitudId);
        });
    });

    // Botones de "Eliminar"
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const solicitudId = this.getAttribute('data-solicitud-id');
            eliminarSolicitud(solicitudId);
        });
    });
}

async function marcarComoLeido(solicitudId) {
    if (!confirm('¿Marcar esta solicitud como leída?')) {
        return;
    }

    try {
        const response = await fetch(`/api/admin/marcar_leido/${solicitudId}`);
        const result = await response.json();

        if (response.ok) {
            // Actualizar la interfaz
            actualizarSolicitudUI(solicitudId, 'leida');
            actualizarEstadisticas();
            mostrarNotificacion('Solicitud marcada como leída', 'success');
        } else {
            mostrarNotificacion('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error de conexión', 'error');
    }
}

async function eliminarSolicitud(solicitudId) {
    if (!confirm('¿Está seguro de que desea eliminar esta solicitud? Esta acción no se puede deshacer.')) {
        return;
    }

    try {
        const response = await fetch(`/api/admin/eliminar/${solicitudId}`);
        const result = await response.json();

        if (response.ok) {
            // Eliminar de la interfaz
            removerSolicitudUI(solicitudId);
            actualizarEstadisticas();
            mostrarNotificacion('Solicitud eliminada', 'success');
        } else {
            mostrarNotificacion('Error: ' + result.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error de conexión', 'error');
    }
}

function actualizarSolicitudUI(solicitudId, accion) {
    const solicitudCard = document.getElementById(`solicitud-${solicitudId}`);
    if (!solicitudCard) return;

    if (accion === 'leida') {
        // Cambiar botón por badge "Leída"
        const actionsContainer = solicitudCard.querySelector('.solicitud-actions');
        const markReadButton = solicitudCard.querySelector('.mark-read-btn');
        
        if (markReadButton) {
            const badge = document.createElement('span');
            badge.className = 'badge badge-success';
            badge.textContent = 'Leída';
            markReadButton.replaceWith(badge);
        }
        
        // Remover clase unread
        solicitudCard.classList.remove('unread');
    }
}

function removerSolicitudUI(solicitudId) {
    const solicitudCard = document.getElementById(`solicitud-${solicitudId}`);
    if (solicitudCard) {
        solicitudCard.remove();
        
        // Si no hay más solicitudes, mostrar mensaje vacío
        const solicitudesContainer = document.getElementById('solicitudes-container');
        const remainingSolicitudes = solicitudesContainer.querySelectorAll('.solicitud-card');
        
        if (remainingSolicitudes.length === 0) {
            solicitudesContainer.innerHTML = '<div class="no-solicitudes"><p>No hay solicitudes para mostrar</p></div>';
        }
    }
}

function actualizarEstadisticas() {
    const solicitudesContainer = document.getElementById('solicitudes-container');
    const totalSolicitudes = solicitudesContainer.querySelectorAll('.solicitud-card').length;
    const unreadSolicitudes = solicitudesContainer.querySelectorAll('.solicitud-card.unread').length;
    const readSolicitudes = totalSolicitudes - unreadSolicitudes;

    // Actualizar contadores
    const totalEl = document.getElementById('total-solicitudes');
    const unreadEl = document.getElementById('unread-solicitudes');
    const readEl = document.getElementById('read-solicitudes');

    if (totalEl) totalEl.textContent = totalSolicitudes;
    if (unreadEl) unreadEl.textContent = unreadSolicitudes;
    if (readEl) readEl.textContent = readSolicitudes;
}

function mostrarNotificacion(message, type) {
    // Crear notificación temporal
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 12px 20px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.backgroundColor = '#10B981';
    } else {
        notification.style.backgroundColor = '#EF4444';
    }
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.remove();
    }, 3000);
}