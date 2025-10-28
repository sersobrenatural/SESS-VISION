// Debug avanzado para CSS
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 DEBUG AVANZADO SESS-VISION');
    console.log('=============================');
    
    // Verificar estructura HTML
    const navbar = document.querySelector('.navbar');
    const navMenu = document.querySelector('.nav-menu');
    const hero = document.querySelector('.hero');
    
    console.log('Navbar encontrado:', !!navbar);
    console.log('Nav-menu encontrado:', !!navMenu);
    console.log('Hero encontrado:', !!hero);
    
    // Verificar estilos aplicados
    if (navbar) {
        const styles = window.getComputedStyle(navbar);
        console.log('Navbar background:', styles.backgroundColor);
        console.log('Navbar display:', styles.display);
    }
    
    // Forzar reflow y repaint
    document.body.style.display = 'none';
    document.body.offsetHeight; // Trigger reflow
    document.body.style.display = 'block';
    
    console.log('✅ Debug completado');
});