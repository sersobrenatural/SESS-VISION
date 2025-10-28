// SESS-Vision Main Script - Production Ready
(function() {
    'use strict';
    
    const SESSVision = {
        init() {
            this.initNavigation();
            this.initSmoothScroll();
            this.initCounters();
            this.initFormHandling();
            this.initScrollEffects();
            this.initAccessibility();
        },
        
        initNavigation() {
            const hamburger = document.querySelector('.hamburger');
            const navMenu = document.querySelector('.nav-menu');
            const dropbtn = document.querySelector('.dropbtn');
            
            if (hamburger && navMenu) {
                hamburger.addEventListener('click', () => {
                    const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
                    hamburger.classList.toggle('active');
                    navMenu.classList.toggle('active');
                    hamburger.setAttribute('aria-expanded', !isExpanded);
                });
                
                document.addEventListener('click', (e) => {
                    if (!e.target.matches('.dropbtn') && !e.target.closest('.dropdown')) {
                        document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                            dropdown.style.display = 'none';
                        });
                    }
                });
            }
            
            if (dropbtn) {
                dropbtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const dropdown = e.target.nextElementSibling;
                    const isExpanded = e.target.getAttribute('aria-expanded') === 'true';
                    
                    document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                        dropdown.style.display = 'none';
                    });
                    
                    dropdown.style.display = isExpanded ? 'none' : 'block';
                    e.target.setAttribute('aria-expanded', !isExpanded);
                });
            }
        },
        
        initSmoothScroll() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        },
        
        initCounters() {
            const counters = document.querySelectorAll('[data-count]');
            if (!counters.length) return;
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            counters.forEach(counter => observer.observe(counter));
        },
        
        animateCounter(element) {
            const target = parseInt(element.getAttribute('data-count'));
            const duration = 2000;
            const step = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    element.textContent = target + '+';
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current);
                }
            }, 16);
        },
        
        initFormHandling() {
            const solicitudForm = document.getElementById('solicitudForm');
            if (!solicitudForm) return;
            
            solicitudForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleFormSubmit(solicitudForm);
            });
        },
        
        async handleFormSubmit(form) {
            const submitBtn = form.querySelector('.submit-btn');
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoader = submitBtn.querySelector('.btn-loader');
            const alertDiv = document.getElementById('alert');
            
            btnText.style.display = 'none';
            btnLoader.style.display = 'block';
            submitBtn.disabled = true;
            
            const formData = {
                nombre: document.getElementById('nombre').value.trim(),
                email: document.getElementById('email').value.trim(),
                telefono: document.getElementById('telefono').value.trim(),
                servicio: document.getElementById('servicio').value,
                mensaje: document.getElementById('mensaje').value.trim()
            };
            
            try {
                const response = await fetch('/api/solicitud', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    this.showAlert(alertDiv, result.message, 'success');
                    form.reset();
                } else {
                    this.showAlert(alertDiv, result.error, 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                this.showAlert(alertDiv, 'Error de conexión. Por favor, intente nuevamente.', 'error');
            } finally {
                btnText.style.display = 'block';
                btnLoader.style.display = 'none';
                submitBtn.disabled = false;
            }
        },
        
        initScrollEffects() {
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;
            
            let ticking = false;
            
            const updateNavbar = () => {
                if (window.scrollY > 100) {
                    navbar.style.background = 'rgba(255, 255, 255, 0.98)';
                    navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
                } else {
                    navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                    navbar.style.boxShadow = 'none';
                }
                ticking = false;
            };
            
            window.addEventListener('scroll', () => {
                if (!ticking) {
                    requestAnimationFrame(updateNavbar);
                    ticking = true;
                }
            });
        },
        
        initAccessibility() {
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    document.querySelectorAll('.dropdown-content').forEach(dropdown => {
                        dropdown.style.display = 'none';
                    });
                }
            });
            
            document.querySelectorAll('[role="menu"] a').forEach(menuItem => {
                menuItem.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        e.target.click();
                    }
                });
            });
        },
        
        showAlert(alertDiv, message, type = 'info') {
            if (!alertDiv) return;
            
            alertDiv.textContent = message;
            alertDiv.className = `alert alert-${type} show`;
            
            setTimeout(() => {
                alertDiv.classList.remove('show');
            }, 5000);
        }
    };
    
    document.addEventListener('DOMContentLoaded', () => SESSVision.init());
    
    if (window.addEventListener) {
        window.addEventListener('load', SESSVision.init, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', SESSVision.init);
    }
})();