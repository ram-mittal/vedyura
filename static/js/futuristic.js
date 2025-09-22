/**
 * Futuristic Vedyura JavaScript
 * Enhanced interactions and animations
 */

class VedyuraApp {
    constructor() {
        this.init();
    }

    init() {
        this.initTheme(); // Initialize theme first
        this.setupEventListeners();
        this.initAnimations();
        this.setupIntersectionObserver();
        this.initParticleSystem();
        this.setupCursorEffects();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        }

        // Mobile menu
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', this.toggleMobileMenu.bind(this));
        }

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', this.smoothScroll.bind(this));
        });

        // Window resize handler
        window.addEventListener('resize', this.handleResize.bind(this));

        // Scroll handler for navbar
        window.addEventListener('scroll', this.handleScroll.bind(this));
        
        // Theme change handler
        window.addEventListener('themeChanged', this.handleThemeChange.bind(this));
    }

    toggleTheme() {
        const body = document.body;
        const themeIcon = document.querySelector('.theme-icon');
        const themeToggle = document.getElementById('themeToggle');
        
        // Toggle theme class (now using light-theme as alternative)
        body.classList.toggle('light-theme');
        
        // Update icon with smooth transition
        if (themeIcon) {
            themeIcon.style.transform = 'scale(0.8)';
            setTimeout(() => {
                themeIcon.textContent = body.classList.contains('light-theme') ? '🌙' : '☀️';
                themeIcon.style.transform = 'scale(1)';
            }, 150);
        }
        
        // Add visual feedback to toggle button
        if (themeToggle) {
            themeToggle.style.transform = 'scale(0.95)';
            setTimeout(() => {
                themeToggle.style.transform = 'scale(1)';
            }, 100);
        }
        
        // Store theme preference
        const currentTheme = body.classList.contains('light-theme') ? 'light' : 'dark';
        localStorage.setItem('vedyura-theme', currentTheme);
        
        // Dispatch custom event for other components
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: currentTheme } 
        }));
    }

    toggleMobileMenu() {
        const navLinks = document.querySelector('.nav-links');
        const mobileToggle = document.querySelector('.mobile-menu-toggle');
        
        if (navLinks && mobileToggle) {
            navLinks.classList.toggle('active');
            mobileToggle.classList.toggle('active');
        }
    }

    smoothScroll(e) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    handleResize() {
        // Handle responsive adjustments
        this.updateParticleSystem();
    }

    handleScroll() {
        const nav = document.querySelector('.futuristic-nav');
        if (nav) {
            const isLightTheme = document.body.classList.contains('light-theme');
            
            if (window.scrollY > 100) {
                if (isLightTheme) {
                    nav.style.background = 'rgba(255, 255, 255, 0.95)';
                } else {
                    nav.style.background = 'rgba(10, 10, 10, 0.95)';
                }
                nav.style.backdropFilter = 'blur(20px)';
                nav.style.boxShadow = isLightTheme ? '0 2px 20px rgba(0, 0, 0, 0.1)' : '0 2px 20px rgba(0, 0, 0, 0.3)';
            } else {
                if (isLightTheme) {
                    nav.style.background = 'rgba(255, 255, 255, 0.9)';
                } else {
                    nav.style.background = 'rgba(10, 10, 10, 0.8)';
                }
                nav.style.backdropFilter = 'blur(20px)';
                nav.style.boxShadow = 'none';
            }
        }
    }

    handleThemeChange(event) {
        // Update navigation background immediately when theme changes
        this.handleScroll();
        
        // Update any other theme-dependent elements
        const particles = document.querySelectorAll('.floating-particle');
        particles.forEach(particle => {
            if (event.detail.theme === 'light') {
                particle.style.opacity = '0.05';
            } else {
                particle.style.opacity = '0.3';
            }
        });
    }

    initAnimations() {
        // Initialize GSAP animations if available
        if (typeof gsap !== 'undefined') {
            this.setupGSAPAnimations();
        } else {
            this.setupCSSAnimations();
        }
    }

    setupCSSAnimations() {
        // Animate elements on scroll
        const animateOnScroll = (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        };

        const observer = new IntersectionObserver(animateOnScroll, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe elements for animation
        document.querySelectorAll('.feature-card, .stat-item, .section-header').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    setupIntersectionObserver() {
        // Stats counter animation
        const statsObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.hasAttribute('data-animated')) {
                    entry.target.setAttribute('data-animated', 'true');
                    this.animateStats(entry.target);
                    statsObserver.unobserve(entry.target); // Stop observing after animation
                }
            });
        }, { threshold: 0.3, rootMargin: '0px 0px -100px 0px' });

        document.querySelectorAll('.stat-number').forEach(stat => {
            statsObserver.observe(stat);
        });
    }

    animateStats(element) {
        const target = parseInt(element.dataset.count);
        const duration = 1500;
        const start = performance.now();
        let animationId;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - start;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function - smooth ease out
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(easeOutCubic * target);
            
            // Update text with proper suffix
            if (target === 80) {
                element.textContent = current + '%';
            } else {
                element.textContent = current + '+';
            }
            
            if (progress < 1) {
                animationId = requestAnimationFrame(animate);
            } else {
                // Ensure final value is set correctly
                if (target === 80) {
                    element.textContent = target + '%';
                } else {
                    element.textContent = target + '+';
                }
                cancelAnimationFrame(animationId);
            }
        };
        
        animationId = requestAnimationFrame(animate);
    }

    initParticleSystem() {
        this.createFloatingParticles();
    }

    createFloatingParticles() {
        const particleContainer = document.querySelector('.hero-background');
        if (!particleContainer) return;

        const particleCount = window.innerWidth > 768 ? 20 : 10;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'floating-particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 2}px;
                height: ${Math.random() * 4 + 2}px;
                background: rgba(102, 126, 234, ${Math.random() * 0.5 + 0.2});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: floatParticle ${Math.random() * 10 + 10}s linear infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            particleContainer.appendChild(particle);
        }
    }

    updateParticleSystem() {
        // Update particle system on resize
        const particles = document.querySelectorAll('.floating-particle');
        particles.forEach(particle => {
            particle.style.left = Math.random() * 100 + '%';
        });
    }

    setupCursorEffects() {
        // Custom cursor effects
        const cursor = document.createElement('div');
        cursor.className = 'custom-cursor';
        cursor.style.cssText = `
            position: fixed;
            width: 20px;
            height: 20px;
            background: rgba(102, 126, 234, 0.3);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            transition: transform 0.1s ease;
            display: none;
        `;
        document.body.appendChild(cursor);

        // Show custom cursor on desktop
        if (window.innerWidth > 768) {
            cursor.style.display = 'block';
            
            document.addEventListener('mousemove', (e) => {
                cursor.style.left = e.clientX - 10 + 'px';
                cursor.style.top = e.clientY - 10 + 'px';
            });

            // Cursor hover effects
            document.querySelectorAll('a, button, .feature-card').forEach(el => {
                el.addEventListener('mouseenter', () => {
                    cursor.style.transform = 'scale(2)';
                    cursor.style.background = 'rgba(102, 126, 234, 0.5)';
                });
                
                el.addEventListener('mouseleave', () => {
                    cursor.style.transform = 'scale(1)';
                    cursor.style.background = 'rgba(102, 126, 234, 0.3)';
                });
            });
        }
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Initialize theme from localStorage
    initTheme() {
        const savedTheme = localStorage.getItem('vedyura-theme');
        const body = document.body;
        const themeIcon = document.querySelector('.theme-icon');
        
        // Set initial theme based on saved preference or default to dark
        if (savedTheme === 'light') {
            body.classList.add('light-theme');
            if (themeIcon) {
                themeIcon.textContent = '🌙';
            }
        } else if (savedTheme === 'dark') {
            body.classList.remove('light-theme');
            if (themeIcon) {
                themeIcon.textContent = '☀️';
            }
        } else {
            // Default to dark theme (no class needed)
            // Check system preference if no saved theme
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (!prefersDark) {
                // Only switch to light if system prefers light
                body.classList.add('light-theme');
                if (themeIcon) {
                    themeIcon.textContent = '🌙';
                }
            } else {
                // Stay with default dark theme
                if (themeIcon) {
                    themeIcon.textContent = '☀️';
                }
            }
        }
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('vedyura-theme')) {
                if (!e.matches) {
                    // System prefers light
                    body.classList.add('light-theme');
                    if (themeIcon) {
                        themeIcon.textContent = '🌙';
                    }
                } else {
                    // System prefers dark
                    body.classList.remove('light-theme');
                    if (themeIcon) {
                        themeIcon.textContent = '☀️';
                    }
                }
            }
        });
    }
}

// Enhanced tilt effect for cards
class TiltEffect {
    constructor(element) {
        this.element = element;
        this.init();
    }

    init() {
        this.element.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.element.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }

    handleMouseMove(e) {
        const rect = this.element.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 8;
        const rotateY = (centerX - x) / 8;
        
        this.element.style.transform = `
            perspective(1000px) 
            rotateX(${rotateX}deg) 
            rotateY(${rotateY}deg) 
            translateZ(20px)
        `;
        
        // Add glow effect
        const glow = this.element.querySelector('.feature-glow');
        if (glow) {
            glow.style.opacity = '0.2';
        }
    }

    handleMouseLeave() {
        this.element.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
        
        const glow = this.element.querySelector('.feature-glow');
        if (glow) {
            glow.style.opacity = '0';
        }
    }
}

// Hologram animation controller
class HologramController {
    constructor() {
        this.init();
    }

    init() {
        const hologramContainer = document.querySelector('.hologram-container');
        if (hologramContainer) {
            this.createDataStreams();
            this.animateDataPoints();
        }
    }

    createDataStreams() {
        const container = document.querySelector('.hologram-data');
        if (!container) return;

        // Create additional visual elements
        for (let i = 0; i < 3; i++) {
            const stream = document.createElement('div');
            stream.className = 'data-stream';
            stream.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                width: 2px;
                height: 100px;
                background: linear-gradient(to bottom, transparent, rgba(79, 172, 254, 0.8), transparent);
                transform: translate(-50%, -50%) rotate(${i * 120}deg);
                animation: dataStream 3s ease-in-out infinite;
                animation-delay: ${i * 0.5}s;
            `;
            container.appendChild(stream);
        }
    }

    animateDataPoints() {
        const dataPoints = document.querySelectorAll('.data-point');
        dataPoints.forEach((point, index) => {
            point.addEventListener('mouseenter', () => {
                point.style.transform = `
                    translate(-50%, -50%) 
                    rotate(var(--angle)) 
                    translateY(-150px) 
                    scale(1.5)
                `;
                point.style.boxShadow = '0 0 20px rgba(79, 172, 254, 0.8)';
            });
            
            point.addEventListener('mouseleave', () => {
                point.style.transform = `
                    translate(-50%, -50%) 
                    rotate(var(--angle)) 
                    translateY(-150px) 
                    scale(1)
                `;
                point.style.boxShadow = 'none';
            });
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main app
    const app = new VedyuraApp();
    
    // Initialize tilt effects
    document.querySelectorAll('[data-tilt]').forEach(el => {
        new TiltEffect(el);
    });
    
    // Initialize hologram
    new HologramController();
    
    // Add floating particle animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes floatParticle {
            0% {
                transform: translateY(100vh) translateX(0px) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) translateX(100px) rotate(360deg);
                opacity: 0;
            }
        }
        
        @keyframes dataStream {
            0%, 100% {
                opacity: 0.3;
                height: 50px;
            }
            50% {
                opacity: 1;
                height: 150px;
            }
        }
    `;
    document.head.appendChild(style);
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VedyuraApp, TiltEffect, HologramController };
}
