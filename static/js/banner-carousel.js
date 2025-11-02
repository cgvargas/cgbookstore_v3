/**
 * BANNER CAROUSEL - Sistema de Carrossel Automático de Banners
 * CGBookStore v3
 *
 * Funcionalidades:
 * - Rotação automática de banners
 * - Navegação manual (prev/next)
 * - Indicadores clicáveis
 * - Controle de auto-play (pause/play)
 * - Tracking de visualizações e cliques
 * - Suporte a teclado (setas)
 * - Pausa automática ao hover
 */

class BannerCarousel {
    constructor() {
        this.container = document.getElementById('homeBannerCarousel');
        if (!this.container) return;

        this.slides = this.container.querySelectorAll('.banner-slide');
        this.indicators = this.container.querySelectorAll('.banner-indicator');
        this.autoplayButton = this.container.querySelector('.banner-autoplay-toggle');

        this.currentIndex = 0;
        this.isPlaying = true;
        this.autoplayInterval = null;
        this.autoplayDelay = 5000; // 5 segundos

        this.init();
    }

    init() {
        if (this.slides.length <= 1) return; // Não inicializar se houver apenas 1 banner

        // Configurar eventos
        this.setupEvents();

        // Iniciar autoplay
        this.startAutoplay();

        // Registrar visualização do primeiro banner
        this.trackBannerView(this.currentIndex);

        console.log(`Banner Carousel inicializado com ${this.slides.length} banners`);
    }

    setupEvents() {
        // Pausar autoplay ao hover no carousel
        this.container.addEventListener('mouseenter', () => {
            if (this.isPlaying) {
                this.pauseAutoplay();
            }
        });

        this.container.addEventListener('mouseleave', () => {
            if (this.isPlaying) {
                this.startAutoplay();
            }
        });

        // Suporte a teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.prev();
            } else if (e.key === 'ArrowRight') {
                this.next();
            }
        });
    }

    goTo(index) {
        if (index === this.currentIndex) return;

        // Remover classe active do slide e indicador atuais
        this.slides[this.currentIndex].classList.remove('active');
        this.indicators[this.currentIndex].classList.remove('active');

        // Atualizar índice
        this.currentIndex = index;

        // Adicionar classe active ao novo slide e indicador
        this.slides[this.currentIndex].classList.add('active');
        this.indicators[this.currentIndex].classList.add('active');

        // Registrar visualização
        this.trackBannerView(this.currentIndex);

        // Reiniciar autoplay se estiver ativo
        if (this.isPlaying) {
            this.resetAutoplay();
        }
    }

    next() {
        const nextIndex = (this.currentIndex + 1) % this.slides.length;
        this.goTo(nextIndex);
    }

    prev() {
        const prevIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
        this.goTo(prevIndex);
    }

    startAutoplay() {
        this.autoplayInterval = setInterval(() => {
            this.next();
        }, this.autoplayDelay);
    }

    pauseAutoplay() {
        if (this.autoplayInterval) {
            clearInterval(this.autoplayInterval);
            this.autoplayInterval = null;
        }
    }

    resetAutoplay() {
        this.pauseAutoplay();
        this.startAutoplay();
    }

    toggleAutoplay() {
        this.isPlaying = !this.isPlaying;

        if (this.isPlaying) {
            this.startAutoplay();
            this.autoplayButton.innerHTML = '<i class="fas fa-pause"></i>';
            this.autoplayButton.classList.remove('paused');
            this.autoplayButton.title = 'Pausar carrossel';
        } else {
            this.pauseAutoplay();
            this.autoplayButton.innerHTML = '<i class="fas fa-play"></i>';
            this.autoplayButton.classList.add('paused');
            this.autoplayButton.title = 'Reproduzir carrossel';
        }
    }

    /**
     * Registra visualização do banner (envia para backend)
     */
    trackBannerView(index) {
        const bannerId = this.slides[index].dataset.bannerId;
        if (!bannerId) return;

        // Enviar requisição AJAX para incrementar contador de views
        fetch(`/api/banner/${bannerId}/view/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            }
        }).catch(error => {
            console.error('Erro ao registrar visualização do banner:', error);
        });
    }

    /**
     * Obtém CSRF token para requisições POST
     */
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

/**
 * Registra clique no banner (função global chamada pelo template)
 */
function trackBannerClick(bannerId) {
    fetch(`/api/banner/${bannerId}/click/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    }).catch(error => {
        console.error('Erro ao registrar clique do banner:', error);
    });
}

/**
 * Função auxiliar para obter CSRF token
 */
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Inicializar carousel quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    window.bannerCarousel = new BannerCarousel();
});
