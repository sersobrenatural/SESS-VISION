// Funciones del panel de administración
class AdminPanel {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
    }

    setupEventListeners() {
        // Marcar como leído
        document.addEventListener('click', (e) => {
            if (e.target.matches('.mark-read-btn') || e.target.closest('.mark-read-btn')) {
                const btn = e.target.matches('.mark-read-btn') ? e.target : e.target.closest('.mark-read-btn');
                this.marcarComoLeido(btn.dataset.id);
            }
        });

        // Cambiar estado
        document.addEventListener('change', (e) => {
            if (e.target.matches('.status-select')) {
                this.cambiarEstado(e.target.dataset.id, e.target.value);
            }
        });

        // Eliminar solicitud
        document.addEventListener('click', (e) => {
            if (e.target.matches('.delete-btn') || e.target.closest('.delete-btn')) {
                const btn = e.target.matches('.delete-btn') ? e.target : e.target.closest('.delete-btn');
                this.eliminarSolicitud(btn.dataset.id);
            }
        });
    }

    async marcarComoLeido(solicitudId) {
        try {
            const response = await fetch(`/api/admin/marcar_leido/${solicitudId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Solicitud marcada como leída', 'success');
                this.actualizarUI(solicitudId, 'leido');
                this.actualizarEstadisticas();
            } else {
                this.showNotification('Error: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión', 'error');
        }
    }

    async cambiarEstado(solicitudId, estado) {
        try {
            const response = await fetch(`/api/admin/actualizar_estado/${solicitudId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ estado })
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(`Estado actualizado a ${estado}`, 'success');
                this.actualizarUI(solicitudId, 'estado', estado);
            } else {
                this.showNotification('Error: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión', 'error');
        }
    }

    async eliminarSolicitud(solicitudId) {
        if (!confirm('¿Está seguro de que desea eliminar esta solicitud? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/admin/eliminar/${solicitudId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification('Solicitud eliminada', 'success');
                this.removerSolicitudUI(solicitudId);
                this.actualizarEstadisticas();
            } else {
                this.showNotification('Error: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión', 'error');
        }
    }

    actualizarUI(solicitudId, accion, datos = null) {
        const solicitudCard = document.getElementById(`solicitud-${solicitudId}`);
        if (!solicitudCard) return;

        switch (accion) {
            case 'leido':
                solicitudCard.classList.remove('unread');
                const markReadBtn = solicitudCard.querySelector('.mark-read-btn');
                if (markReadBtn) markReadBtn.remove();
                break;

            case 'estado':
                const statusBadge = solicitudCard.querySelector('.status');
                if (statusBadge) {
                    statusBadge.textContent = this.getEstadoText(datos);
                    statusBadge.className = `status status-${datos}`;
                }
                break;
        }
    }

    removerSolicitudUI(solicitudId) {
        const solicitudCard = document.getElementById(`solicitud-${solicitudId}`);
        if (solicitudCard) {
            solicitudCard.remove();
            
            // Si no hay más solicitudes, mostrar estado vacío
            const container = document.querySelector('.solicitudes-list');
            if (container && container.children.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <h4>No hay solicitudes</h4>
                        <p>No se encontraron solicitudes con los filtros aplicados.</p>
                    </div>
                `;
            }
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/admin/estadisticas');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatsDisplay(stats);
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    updateStatsDisplay(stats) {
        // Actualizar contadores en tiempo real si es necesario
        const totalEl = document.getElementById('total-solicitudes');
        const unreadEl = document.getElementById('unread-solicitudes');
        
        if (totalEl) totalEl.textContent = stats.total;
        if (unreadEl) unreadEl.textContent = stats.no_leidas;
    }

    actualizarEstadisticas() {
        // Recargar estadísticas después de una acción
        setTimeout(() => this.loadStats(), 500);
    }

    getEstadoText(estado) {
        const estados = {
            'pendiente': '⏳ Pendiente',
            'contactado': '✅ Contactado',
            'cerrado': '🔒 Cerrado'
        };
        return estados[estado] || estado;
    }

    showNotification(message, type = 'info') {
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
            border-radius: 8px;
            color: white;
            font-weight: 500;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        if (type === 'success') {
            notification.style.backgroundColor = '#10B981';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#EF4444';
        } else {
            notification.style.backgroundColor = '#3B82F6';
        }
        
        document.body.appendChild(notification);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new AdminPanel();
});