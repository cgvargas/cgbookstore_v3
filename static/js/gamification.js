/**
 * CGBookStore v3 - Sistema de Gamificação
 * Arquivo: gamification.js
 * Versão: 1.0
 * Data: 24/10/2025
 *
 * Funcionalidades:
 * - Sistema de notificações (toasts)
 * - Animações de desbloqueio de conquistas
 * - Modais interativos
 * - Integração com APIs REST
 * - Loading states
 * - Gerenciamento de badges
 */

// ========================================
// 1. CONFIGURAÇÕES GLOBAIS
// ========================================

const GamificationConfig = {
    // Configurações de API
    api: {
        achievements: '/api/gamification/achievements/',
        achievementProgress: '/api/gamification/achievement-progress/',
        achievementDetails: '/api/gamification/achievement-details/',
        claimAchievement: '/api/gamification/claim-achievement/',
        checkNewAchievements: '/api/gamification/check-new-achievements/',
        badges: '/api/gamification/badges/',
        showcaseBadge: '/api/gamification/showcase-badge/',
        removeShowcaseBadge: '/api/gamification/remove-showcase-badge/',
        ranking: '/api/gamification/ranking/',
        userStats: '/api/gamification/user-stats/',
    },

    // Configurações de notificações
    toast: {
        duration: 5000, // 5 segundos
        position: 'top-end', // top-end, top-center, bottom-end, etc.
    },

    // Configurações de animações
    animations: {
        confettiDuration: 3000,
        modalFadeIn: 300,
        toastFadeIn: 300,
    },

    // Configurações de sons (opcional)
    sounds: {
        enabled: true,
        achievementUnlocked: '/static/sounds/achievement.mp3',
        badgeReceived: '/static/sounds/badge.mp3',
    }
};

// ========================================
// 2. SISTEMA DE NOTIFICAÇÕES (TOASTS)
// ========================================

class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    /**
     * Inicializa o container de toasts
     */
    init() {
        // Criar container se não existir
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container position-fixed p-3';
            this.container.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    /**
     * Mostra uma notificação toast
     * @param {string} message - Mensagem a ser exibida
     * @param {string} type - Tipo: success, error, warning, info
     * @param {number} duration - Duração em ms (opcional)
     */
    show(message, type = 'info', duration = null) {
        const toastId = 'toast-' + Date.now();
        const toastDuration = duration || GamificationConfig.toast.duration;

        // Ícones por tipo
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        // Cores por tipo
        const colors = {
            success: 'bg-success',
            error: 'bg-danger',
            warning: 'bg-warning',
            info: 'bg-info'
        };

        // Criar elemento toast
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${colors[type]} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${icons[type]} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Fechar"></button>
                </div>
            </div>
        `;

        // Adicionar ao container
        this.container.insertAdjacentHTML('beforeend', toastHTML);

        // Inicializar Bootstrap Toast
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: toastDuration
        });

        // Mostrar toast
        toast.show();

        // Remover do DOM após fechar
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    /**
     * Atalhos para tipos específicos
     */
    success(message, duration = null) {
        this.show(message, 'success', duration);
    }

    error(message, duration = null) {
        this.show(message, 'error', duration);
    }

    warning(message, duration = null) {
        this.show(message, 'warning', duration);
    }

    info(message, duration = null) {
        this.show(message, 'info', duration);
    }
}

// ========================================
// 3. ANIMAÇÕES DE CONQUISTAS
// ========================================

class AchievementModal {
    constructor() {
        this.modal = null;
        this.init();
    }

    /**
     * Inicializa o modal de conquista
     */
    init() {
        // Verificar se modal já existe
        if (!document.getElementById('achievement-modal')) {
            const modalHTML = `
                <div class="modal fade" id="achievement-modal" tabindex="-1" aria-labelledby="achievementModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content bg-dark text-white border-warning">
                            <div class="modal-header border-warning">
                                <h5 class="modal-title" id="achievementModalLabel">
                                    <i class="fas fa-trophy text-warning me-2"></i>
                                    Conquista Desbloqueada!
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Fechar"></button>
                            </div>
                            <div class="modal-body text-center">
                                <div id="achievement-confetti" class="position-relative">
                                    <i id="achievement-icon" class="fas fa-trophy fa-5x text-warning mb-3"></i>
                                </div>
                                <h3 id="achievement-name" class="text-warning mb-2"></h3>
                                <p id="achievement-description" class="text-light mb-3"></p>
                                <div class="badge bg-warning text-dark fs-5">
                                    <i class="fas fa-star me-1"></i>
                                    <span id="achievement-xp">0</span> XP
                                </div>
                            </div>
                            <div class="modal-footer border-warning justify-content-center">
                                <button type="button" class="btn btn-warning" data-bs-dismiss="modal">
                                    <i class="fas fa-check me-2"></i>
                                    Incrível!
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        // Obter referência do modal
        this.modal = new bootstrap.Modal(document.getElementById('achievement-modal'));
    }

    /**
     * Mostra o modal de conquista desbloqueada
     * @param {Object} achievement - Dados da conquista
     */
    show(achievement) {
        // Atualizar conteúdo do modal
        document.getElementById('achievement-icon').className = `fas ${achievement.icon} fa-5x text-warning mb-3`;
        document.getElementById('achievement-name').textContent = achievement.name;
        document.getElementById('achievement-description').textContent = achievement.description;
        document.getElementById('achievement-xp').textContent = achievement.xp_reward;

        // Mostrar modal
        this.modal.show();

        // Adicionar confete (opcional)
        this.addConfetti();

        // Tocar som (opcional)
        this.playSound();
    }

    /**
     * Adiciona efeito de confete (usando biblioteca externa ou CSS)
     */
    addConfetti() {
        // Implementação simples com CSS (pode ser substituída por biblioteca como canvas-confetti)
        const confettiContainer = document.getElementById('achievement-confetti');
        confettiContainer.classList.add('confetti-animation');

        setTimeout(() => {
            confettiContainer.classList.remove('confetti-animation');
        }, GamificationConfig.animations.confettiDuration);
    }

    /**
     * Toca som de conquista desbloqueada
     */
    playSound() {
        if (GamificationConfig.sounds.enabled) {
            const audio = new Audio(GamificationConfig.sounds.achievementUnlocked);
            audio.volume = 0.3;
            audio.play().catch(err => console.log('Erro ao reproduzir som:', err));
        }
    }
}

// ========================================
// 4. INTEGRAÇÃO COM APIS
// ========================================

class GamificationAPI {
    /**
     * Obtém o CSRF token para requisições POST
     */
    static getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    /**
     * Faz requisição à API
     * @param {string} url - URL da API
     * @param {string} method - Método HTTP (GET, POST, etc.)
     * @param {Object} data - Dados para enviar (opcional)
     */
    static async request(url, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            credentials: 'same-origin',
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Erro na requisição');
            }

            return result;
        } catch (error) {
            console.error('Erro na API:', error);
            throw error;
        }
    }

    /**
     * Reivindica uma conquista
     * @param {number} achievementId - ID da conquista
     */
    static async claimAchievement(achievementId) {
        return await this.request(
            GamificationConfig.api.claimAchievement,
            'POST',
            { achievement_id: achievementId }
        );
    }

    /**
     * Verifica se há novas conquistas disponíveis
     */
    static async checkNewAchievements() {
        return await this.request(GamificationConfig.api.checkNewAchievements, 'POST');
    }

    /**
     * Obtém progresso de uma conquista
     * @param {number} achievementId - ID da conquista
     */
    static async getAchievementProgress(achievementId) {
        return await this.request(
            `${GamificationConfig.api.achievementProgress}${achievementId}/`
        );
    }

    /**
     * Obtém detalhes de uma conquista
     * @param {number} achievementId - ID da conquista
     */
    static async getAchievementDetails(achievementId) {
        return await this.request(
            `${GamificationConfig.api.achievementDetails}${achievementId}/`
        );
    }

    /**
     * Destaca um badge no perfil
     * @param {number} badgeId - ID do badge
     */
    static async showcaseBadge(badgeId) {
        return await this.request(
            GamificationConfig.api.showcaseBadge,
            'POST',
            { badge_id: badgeId }
        );
    }

    /**
     * Remove badge do destaque
     * @param {number} badgeId - ID do badge
     */
    static async removeShowcaseBadge(badgeId) {
        return await this.request(
            GamificationConfig.api.removeShowcaseBadge,
            'POST',
            { badge_id: badgeId }
        );
    }

    /**
     * Obtém ranking mensal
     */
    static async getMonthlyRanking() {
        return await this.request(GamificationConfig.api.ranking);
    }

    /**
     * Obtém estatísticas do usuário
     */
    static async getUserStats() {
        return await this.request(GamificationConfig.api.userStats);
    }
}

// ========================================
// 5. GERENCIAMENTO DE BADGES
// ========================================

class BadgeManager {
    /**
     * Destaca um badge (toggle)
     * @param {number} badgeId - ID do badge
     * @param {HTMLElement} button - Botão clicado
     */
    static async toggleShowcase(badgeId, button) {
        const isShowcased = button.classList.contains('showcased');

        // Mostrar loading
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            if (isShowcased) {
                // Remover do destaque
                await GamificationAPI.removeShowcaseBadge(badgeId);
                button.classList.remove('showcased', 'btn-warning');
                button.classList.add('btn-outline-warning');
                button.innerHTML = '<i class="fas fa-star me-2"></i>Destacar';
                toastManager.success('Badge removido do destaque!');
            } else {
                // Adicionar ao destaque
                await GamificationAPI.showcaseBadge(badgeId);
                button.classList.add('showcased', 'btn-warning');
                button.classList.remove('btn-outline-warning');
                button.innerHTML = '<i class="fas fa-star me-2"></i>Destacado';
                toastManager.success('Badge destacado no perfil!');
            }
        } catch (error) {
            toastManager.error(error.message || 'Erro ao atualizar badge');
            button.innerHTML = originalHTML;
        } finally {
            button.disabled = false;
        }
    }
}

// ========================================
// 6. GERENCIAMENTO DE CONQUISTAS
// ========================================

class AchievementManager {
    /**
     * Reivindica uma conquista disponível
     * @param {number} achievementId - ID da conquista
     * @param {HTMLElement} button - Botão clicado
     */
    static async claim(achievementId, button) {
        // Mostrar loading
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const result = await GamificationAPI.claimAchievement(achievementId);

            if (result.success) {
                // Mostrar modal de conquista desbloqueada
                achievementModal.show(result.achievement);

                // Atualizar UI
                button.innerHTML = '<i class="fas fa-check me-2"></i>Reivindicada';
                button.classList.remove('btn-warning');
                button.classList.add('btn-success', 'disabled');

                // Atualizar contador de XP (se existir)
                this.updateXPCounter(result.new_xp);

                toastManager.success(`Você ganhou ${result.achievement.xp_reward} XP!`);
            }
        } catch (error) {
            toastManager.error(error.message || 'Erro ao reivindicar conquista');
            button.innerHTML = originalHTML;
            button.disabled = false;
        }
    }

    /**
     * Verifica novas conquistas disponíveis
     */
    static async checkNew() {
        try {
            const result = await GamificationAPI.checkNewAchievements();

            if (result.new_achievements && result.new_achievements.length > 0) {
                // Mostrar notificação para cada nova conquista
                result.new_achievements.forEach(achievement => {
                    toastManager.info(
                        `Nova conquista disponível: ${achievement.name}`,
                        8000
                    );
                });

                // Atualizar badge de notificação (se existir)
                this.updateNotificationBadge(result.new_achievements.length);
            }
        } catch (error) {
            console.error('Erro ao verificar novas conquistas:', error);
        }
    }

    /**
     * Atualiza o contador de XP na interface
     * @param {number} newXP - Novo valor de XP
     */
    static updateXPCounter(newXP) {
        const xpElements = document.querySelectorAll('[data-user-xp]');
        xpElements.forEach(element => {
            element.textContent = Utils.formatNumber(newXP);
        });
    }

    /**
     * Atualiza badge de notificação de conquistas
     * @param {number} count - Número de conquistas disponíveis
     */
    static updateNotificationBadge(count) {
        const badge = document.getElementById('achievement-notification-badge');
        if (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }
}

// ========================================
// 7. UTILITÁRIOS
// ========================================

const Utils = {
    /**
     * Formata número com separador de milhares
     * @param {number} num - Número a ser formatado
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    },

    /**
     * Atualiza uma barra de progresso
     * @param {HTMLElement} progressBar - Elemento da barra
     * @param {number} percentage - Porcentagem (0-100)
     */
    updateProgressBar(progressBar, percentage) {
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        progressBar.textContent = Math.round(percentage) + '%';
    },

    /**
     * Adiciona animação de pulse a um elemento
     * @param {HTMLElement} element - Elemento a ser animado
     */
    addPulseAnimation(element) {
        element.classList.add('pulse-animation');
        setTimeout(() => {
            element.classList.remove('pulse-animation');
        }, 1000);
    }
};

// ========================================
// 8. INICIALIZAÇÃO
// ========================================

// Instâncias globais
let toastManager;
let achievementModal;

/**
 * Inicializa o sistema de gamificação
 */
function initGamification() {
    console.log('🎮 Inicializando Sistema de Gamificação...');

    // Criar instâncias
    toastManager = new ToastManager();
    achievementModal = new AchievementModal();

    // Configurar event listeners
    setupEventListeners();

    // Verificar novas conquistas (a cada 5 minutos)
    setInterval(() => {
        AchievementManager.checkNew();
    }, 5 * 60 * 1000);

    // Verificar imediatamente ao carregar
    AchievementManager.checkNew();

    console.log('✅ Sistema de Gamificação Inicializado!');
}

/**
 * Configura event listeners para botões e ações
 */
function setupEventListeners() {
    // Botões de reivindicar conquista
    document.querySelectorAll('[data-claim-achievement]').forEach(button => {
        button.addEventListener('click', function() {
            const achievementId = parseInt(this.dataset.claimAchievement);
            AchievementManager.claim(achievementId, this);
        });
    });

    // Botões de destacar badge
    document.querySelectorAll('[data-showcase-badge]').forEach(button => {
        button.addEventListener('click', function() {
            const badgeId = parseInt(this.dataset.showcaseBadge);
            BadgeManager.toggleShowcase(badgeId, this);
        });
    });

    // Botão de verificar novas conquistas
    const checkButton = document.getElementById('check-new-achievements-btn');
    if (checkButton) {
        checkButton.addEventListener('click', function() {
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Verificando...';

            AchievementManager.checkNew().finally(() => {
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Verificar Novas';
            });
        });
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initGamification);

// Exportar para uso global (se necessário)
window.GamificationAPI = GamificationAPI;
window.ToastManager = ToastManager;
window.AchievementModal = AchievementModal;
window.BadgeManager = BadgeManager;
window.AchievementManager = AchievementManager;