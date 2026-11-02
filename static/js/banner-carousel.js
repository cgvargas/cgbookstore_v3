/**
 * BANNER CAROUSEL - Sistema de Carrossel Automático de Banners
 * CGBookStore v3
 *
 * Funcionalidades:
 * - Loader inteligente com círculo roxo com interrupção girando e contador % no centro
 * - Pré-carregamento dinâmico em segundo plano do próximo banner
 * - Sincronização do autoplay com a prontidão real da mídia (vídeo/imagem)
 * - Navegação manual (prev/next) e indicadores clicáveis
 * - Pausa ao hover e controle de reprodução
 * - Tracking de visualizações e cliques
 */

class BannerCarousel {
    constructor() {
        this.container = document.getElementById('homeBannerCarousel');
        if (!this.container) return;

        this.slides = Array.from(this.container.querySelectorAll('.banner-slide'));
        this.indicators = Array.from(this.container.querySelectorAll('.banner-indicator'));
        this.autoplayButton = this.container.querySelector('.banner-autoplay-toggle');

        this.currentIndex = 0;
        this.isPlaying = true;
        this.autoplayTimeout = null;
        this.autoplayDelay = 6000; // 6 segundos de exibição após carregamento

        // Estado de cada slide: { isReady, currentPercent, loaderEl, counterEl }
        this.slidesState = [];

        this.init();
    }

    init() {
        if (this.slides.length === 0) return;

        // Configurar loaders e monitoramento de mídia de cada slide
        this.setupSlidesMedia();

        if (this.slides.length > 1) {
            // Configurar eventos de navegação e controles
            this.setupEvents();
        }

        // Registrar visualização do primeiro banner
        this.trackBannerView(this.currentIndex);

        console.log(`[BannerCarousel] Inicializado com ${this.slides.length} banners.`);
    }

    /**
     * Configura o monitoramento de carregamento e o contador numérico de cada slide
     */
    setupSlidesMedia() {
        this.slides.forEach((slide, index) => {
            const loader = slide.querySelector('.banner-media-loader');
            const counterNum = slide.querySelector('.banner-loader-num');
            const video = slide.querySelector('video');
            const img = slide.querySelector('img.banner-image');

            const state = {
                isReady: false,
                currentPercent: 0,
                loaderEl: loader,
                counterEl: counterNum,
                simulatedTimer: null
            };
            this.slidesState[index] = state;

            if (video) {
                this.monitorVideo(video, index);
            } else if (img) {
                this.monitorImage(img, index);
            } else {
                // Sem mídia específica, pronto imediatamente
                this.markSlideReady(index);
            }
        });
    }

    /**
     * Anima o contador numérico suavemente de fromVal até toVal
     */
    animateCounter(index, targetPercent, duration = 300, onComplete = null) {
        const state = this.slidesState[index];
        if (!state || !state.counterEl) return;

        const startPercent = state.currentPercent;
        const diff = targetPercent - startPercent;
        if (diff <= 0) return;

        const startTime = performance.now();

        const step = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Easing cúbico suave
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const val = Math.min(100, Math.round(startPercent + diff * easeProgress));

            state.currentPercent = val;
            state.counterEl.textContent = val;

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                state.currentPercent = targetPercent;
                state.counterEl.textContent = targetPercent;
                if (onComplete) onComplete();
            }
        };

        requestAnimationFrame(step);
    }

    /**
     * Inicia simulação de progresso progressivo enquanto a mídia faz download no Cloudflare
     */
    startSimulatedProgress(index, maxPercent = 88) {
        const state = this.slidesState[index];
        if (!state || state.isReady) return;

        // Início rápido: vai a 15% imediatamente
        this.animateCounter(index, Math.min(15, maxPercent), 200);

        let currentTarget = 15;
        state.simulatedTimer = setInterval(() => {
            if (state.isReady || currentTarget >= maxPercent) {
                clearInterval(state.simulatedTimer);
                return;
            }
            // Incrementa pequenos passos simulando stream de dados
            const increment = Math.max(2, Math.floor(Math.random() * 8));
            currentTarget = Math.min(maxPercent, currentTarget + increment);
            this.animateCounter(index, currentTarget, 300);
        }, 350);
    }

    /**
     * Monitora eventos de carregamento e buffer de vídeo MP4
     */
    monitorVideo(video, index) {
        const state = this.slidesState[index];

        // Se o vídeo já tiver dados suficientes no cache local
        if (video.readyState >= 3) {
            this.markSlideReady(index);
            return;
        }

        // Inicia contagem simulada enquanto aguarda primeiros bytes do Cloudflare
        this.startSimulatedProgress(index, 85);

        // Atualização via buffer real da mídia quando disponível
        const onProgress = () => {
            if (state.isReady) return;
            if (video.buffered.length > 0 && video.duration > 0) {
                const bufferedEnd = video.buffered.end(video.buffered.length - 1);
                const realPercent = Math.min(92, Math.round((bufferedEnd / video.duration) * 100));
                if (realPercent > state.currentPercent) {
                    this.animateCounter(index, realPercent, 250);
                }
            }
        };

        const onReadyToPlay = () => {
            if (state.isReady) return;
            video.removeEventListener('canplay', onReadyToPlay);
            video.removeEventListener('playing', onReadyToPlay);
            video.removeEventListener('progress', onProgress);

            if (state.simulatedTimer) clearInterval(state.simulatedTimer);

            // Animar até 100% e finalizar loader
            this.animateCounter(index, 100, 300, () => {
                setTimeout(() => {
                    this.markSlideReady(index);
                    // Iniciar reprodução suave se for o slide ativo
                    if (this.currentIndex === index) {
                        video.play().catch(() => {});
                    }
                }, 180);
            });
        };

        video.addEventListener('progress', onProgress);
        video.addEventListener('canplay', onReadyToPlay);
        video.addEventListener('playing', onReadyToPlay);

        // Fallback de segurança: revela após 7s se houver lentidão incomum
        setTimeout(() => {
            if (!state.isReady) {
                onReadyToPlay();
            }
        }, 7000);
    }

    /**
     * Monitora carregamento de imagem
     */
    monitorImage(img, index) {
        const state = this.slidesState[index];

        // Se a imagem já foi carregada do cache do navegador
        if (img.complete && img.naturalWidth > 0) {
            this.markSlideReady(index);
            return;
        }

        this.startSimulatedProgress(index, 90);

        const onImageLoaded = () => {
            if (state.isReady) return;
            img.removeEventListener('load', onImageLoaded);
            img.removeEventListener('error', onImageError);

            if (state.simulatedTimer) clearInterval(state.simulatedTimer);

            this.animateCounter(index, 100, 250, () => {
                setTimeout(() => {
                    this.markSlideReady(index);
                }, 150);
            });
        };

        const onImageError = () => {
            img.removeEventListener('load', onImageLoaded);
            img.removeEventListener('error', onImageError);
            if (state.simulatedTimer) clearInterval(state.simulatedTimer);
            this.markSlideReady(index);
        };

        img.addEventListener('load', onImageLoaded);
        img.addEventListener('error', onImageError);

        // Fallback
        setTimeout(() => {
            if (!state.isReady) onImageLoaded();
        }, 6000);
    }

    /**
     * Marca o slide como pronto, esconde o loader com fade-out suave e agenda o próximo banner
     */
    markSlideReady(index) {
        const state = this.slidesState[index];
        if (!state) return;

        state.isReady = true;
        if (state.simulatedTimer) clearInterval(state.simulatedTimer);

        if (state.loaderEl) {
            state.loaderEl.classList.add('loaded');
        }

        // Se for o slide que está visível agora, agenda a contagem do carrossel e pré-carrega o próximo
        if (this.currentIndex === index) {
            this.scheduleAutoplay();
            this.preloadNextSlide();
        }
    }

    /**
     * Pré-carrega a mídia do próximo slide em segundo plano
     */
    preloadNextSlide() {
        if (this.slides.length <= 1) return;
        const nextIndex = (this.currentIndex + 1) % this.slides.length;
        const nextSlide = this.slides[nextIndex];
        if (!nextSlide) return;

        // Pré-carregar vídeo
        const nextVideo = nextSlide.querySelector('video');
        if (nextVideo && nextVideo.readyState < 2) {
            nextVideo.preload = 'auto';
            nextVideo.load();
        }

        // Pré-carregar imagem
        const nextImg = nextSlide.querySelector('img.banner-image');
        if (nextImg && !nextImg.complete) {
            nextImg.loading = 'eager';
            const imgCache = new Image();
            imgCache.src = nextImg.src;
        }
    }

    setupEvents() {
        // Pausar autoplay ao passar o cursor no banner
        this.container.addEventListener('mouseenter', () => {
            if (this.isPlaying) {
                this.pauseAutoplay();
            }
        });

        this.container.addEventListener('mouseleave', () => {
            if (this.isPlaying) {
                this.scheduleAutoplay();
            }
        });

        // Botão de play/pause manual
        if (this.autoplayButton) {
            this.autoplayButton.addEventListener('click', () => {
                this.toggleAutoplay();
            });
        }

        // Suporte ao teclado (setas esquerda/direita)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.prev();
            } else if (e.key === 'ArrowRight') {
                this.next();
            }
        });

        // Pausa quando a aba do navegador perde o foco para economizar recursos
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoplay();
            } else if (this.isPlaying) {
                this.scheduleAutoplay();
            }
        });
    }

    /**
     * Navega para um slide específico
     */
    goTo(index) {
        if (index === this.currentIndex || !this.slides[index]) return;

        // Limpar agendamento atual
        this.pauseAutoplay();

        // Pausar vídeo do slide anterior se houver
        const currentVideo = this.slides[this.currentIndex].querySelector('video');
        if (currentVideo) {
            currentVideo.pause();
        }

        // Alternar classes active
        this.slides[this.currentIndex].classList.remove('active');
        if (this.indicators[this.currentIndex]) {
            this.indicators[this.currentIndex].classList.remove('active');
        }

        this.currentIndex = index;

        this.slides[this.currentIndex].classList.add('active');
        if (this.indicators[this.currentIndex]) {
            this.indicators[this.currentIndex].classList.add('active');
        }

        // Reproduzir vídeo do novo slide se estiver pronto
        const newVideo = this.slides[this.currentIndex].querySelector('video');
        if (newVideo) {
            newVideo.currentTime = 0;
            newVideo.play().catch(() => {});
        }

        // Registrar visualização no analytics
        this.trackBannerView(this.currentIndex);

        // Se o slide já estiver pronto, programa próximo banner e faz prefetch do seguinte
        const state = this.slidesState[this.currentIndex];
        if (state && state.isReady) {
            this.scheduleAutoplay();
            this.preloadNextSlide();
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

    /**
     * Agenda a rotação para o próximo banner após o tempo de exibição completo
     */
    scheduleAutoplay() {
        this.pauseAutoplay();
        if (!this.isPlaying || this.slides.length <= 1) return;

        this.autoplayTimeout = setTimeout(() => {
            this.next();
        }, this.autoplayDelay);
    }

    pauseAutoplay() {
        if (this.autoplayTimeout) {
            clearTimeout(this.autoplayTimeout);
            this.autoplayTimeout = null;
        }
    }

    toggleAutoplay() {
        this.isPlaying = !this.isPlaying;

        if (this.isPlaying) {
            this.scheduleAutoplay();
            if (this.autoplayButton) {
                this.autoplayButton.innerHTML = '<i class="fas fa-pause"></i>';
                this.autoplayButton.classList.remove('paused');
                this.autoplayButton.title = 'Pausar carrossel';
            }
        } else {
            this.pauseAutoplay();
            if (this.autoplayButton) {
                this.autoplayButton.innerHTML = '<i class="fas fa-play"></i>';
                this.autoplayButton.classList.add('paused');
                this.autoplayButton.title = 'Reproduzir carrossel';
            }
        }
    }

    /**
     * Registra visualização do banner no backend
     */
    trackBannerView(index) {
        if (!this.slides[index]) return;
        const bannerId = this.slides[index].dataset.bannerId;
        if (!bannerId) return;

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
     * Obtém CSRF token
     */
    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];

        if (cookieValue) return cookieValue;

        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

/**
 * Registra clique no banner
 */
function trackBannerClick(bannerId) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    const csrfToken = cookieValue || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

    fetch(`/api/banner/${bannerId}/click/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    }).catch(error => {
        console.error('Erro ao registrar clique do banner:', error);
    });
}

// Objeto global para chamadas inline (prev, next, goTo)
window.bannerCarousel = {
    _instance: null,
    _ready: false,

    _ensureReady() {
        if (!this._ready && document.readyState !== 'loading') {
            this._instance = new BannerCarousel();
            this._ready = true;
        }
        return this._ready;
    },

    prev() {
        if (this._ensureReady() && this._instance) {
            this._instance.prev();
        }
    },

    next() {
        if (this._ensureReady() && this._instance) {
            this._instance.next();
        }
    },

    goTo(index) {
        if (this._ensureReady() && this._instance) {
            this._instance.goTo(index);
        }
    },

    toggleAutoplay() {
        if (this._ensureReady() && this._instance) {
            this._instance.toggleAutoplay();
        }
    }
};

// Inicialização segura após o carregamento do DOM
document.addEventListener('DOMContentLoaded', function() {
    window.bannerCarousel._instance = new BannerCarousel();
    window.bannerCarousel._ready = true;
});
