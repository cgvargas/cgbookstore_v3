/**
 * =========================================================================
 * CGBookStore v3 - Sistema de Notificações COMPLETO
 *
 * Versão: 3.0.0
 * Data: Outubro 2025
 *
 * Funcionalidades:
 * - ✅ Polling automático (90s, pausa em aba inativa)
 * - ✅ Sistema de sons integrado
 * - ✅ Filtros avançados (status, categoria, prioridade)
 * - ✅ Suporte a múltiplos tipos de notificação
 * - ✅ Preferências do usuário (localStorage)
 * - ✅ Arquitetura extensível
 *
 * Estrutura:
 * 1. Funções Utilitárias Globais
 * 2. Módulo: ReadingProgressManager
 * 3. Módulo: NotificationManager
 * 4. Inicializadores Globais
 * =========================================================================
 */

// -------------------------------------------------------------------------
// 1. Funções Utilitárias Globais
// -------------------------------------------------------------------------

/**
 * Obtém o valor de um cookie. Usado para o CSRF token do Django.
 * @param {string} name - O nome do cookie.
 * @returns {string|null}
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Exibe uma notificação toast. Delega para o LibraryManager.
 * @param {string} message
 * @param {string} type - 'info', 'success', 'error', 'warning'.
 */
function showToast(message, type = 'info') {
    if (window.LibraryManager && typeof window.LibraryManager.showToast === 'function') {
        window.LibraryManager.showToast(message, type);
    } else {
        console.warn(`[Toast Fallback][${type}]: ${message}`);
        alert(message);
    }
}

/**
 * =========================================================================
 * 2. Módulo: ReadingProgressManager
 * Controla o widget de progresso na página de detalhes do livro.
 * =========================================================================
 */
const ReadingProgressManager = {
    /**
     * Cache de elementos do DOM para evitar buscas repetidas.
     */
    elements: {
        widget: document.getElementById('readingProgressWidget'),
        updateBtn: document.getElementById('updateProgressBtn'),
        deadlineBtn: document.getElementById('setDeadlineBtn'),
        removeDeadlineBtn: document.getElementById('removeDeadlineBtn'),
        currentPageInput: document.getElementById('currentPage'),
    },

    /**
     * Anexa os event listeners aos elementos do widget.
     */
    init() {
        if (!this.elements.widget) {
            return; // Aborta se o widget não estiver na página.
        }
        console.log('📚 Reading Progress Manager inicializado.');

        const bookId = this.elements.widget.dataset.bookId;

        this.elements.updateBtn?.addEventListener('click', () => this.handlers.onUpdateProgress());
        this.elements.deadlineBtn?.addEventListener('click', () => this.handlers.onSetDeadline());
        this.elements.removeDeadlineBtn?.addEventListener('click', () => this.handlers.onRemoveDeadline(bookId));
        this.elements.currentPageInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handlers.onUpdateProgress();
            }
        });
    },

    /**
     * Contém as funções que são chamadas pelos event listeners.
     */
    handlers: {
        /**
         * Lida com o clique no botão 'Salvar Progresso'.
         */
        async onUpdateProgress() {
            const { widget, currentPageInput } = ReadingProgressManager.elements;
            const bookId = widget.dataset.bookId;
            const totalPages = parseInt(document.getElementById('totalPages').textContent, 10);
            const currentPage = parseInt(currentPageInput.value, 10);

            if (isNaN(currentPage) || currentPage < 0 || currentPage > totalPages) {
                return showToast('Por favor, insira um número de página válido.', 'error');
            }

            const updateBtn = ReadingProgressManager.elements.updateBtn;
            updateBtn.disabled = true;
            updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Salvando...';

            try {
                const response = await fetch('/api/reading/update-progress/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                    body: JSON.stringify({ book_id: bookId, current_page: currentPage }),
                });
                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    document.getElementById('progress-bar-inner').style.width = data.progress.percentage + '%';
                    document.getElementById('progress-percentage').textContent = data.progress.percentage + '%';

                    // Se o livro foi completado e movido para "Lidos"
                    if (data.progress.moved_to_read) {
                        // Aguardar 2 segundos e recarregar a página para atualizar a UI
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    }
                } else {
                    showToast(data.message, 'error');
                }
            } catch (error) {
                showToast('Erro de conexão ao salvar progresso.', 'error');
            } finally {
                updateBtn.disabled = false;
                updateBtn.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Progresso';
            }
        },

        /**
         * Lida com o clique no botão 'Definir Prazo'.
         */
        async onSetDeadline() {
            if (typeof Swal === 'undefined') return showToast('Componente de modal não carregado.', 'error');

            const { widget } = ReadingProgressManager.elements;
            const bookId = widget.dataset.bookId;
            const currentDeadline = widget.dataset.deadline || new Date().toISOString().split('T')[0];

            const { value: newDeadline } = await Swal.fire({
                title: 'Definir Prazo de Leitura',
                html: `<input type="date" id="deadline-input" class="swal2-input" value="${currentDeadline}">`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Definir Prazo',
                cancelButtonText: 'Cancelar',
                preConfirm: () => {
                    const dateValue = document.getElementById('deadline-input').value;
                    if (!dateValue) return Swal.showValidationMessage('Selecione uma data.');
                    if (new Date(dateValue) < new Date().setHours(0, 0, 0, 0)) return Swal.showValidationMessage('O prazo não pode ser no passado.');
                    return dateValue;
                }
            });

            if (newDeadline) {
                try {
                    const response = await fetch('/api/reading/set-deadline/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                        body: JSON.stringify({ book_id: bookId, deadline: newDeadline }),
                    });
                    const data = await response.json();
                    if (data.success) {
                        showToast(data.message, 'success');
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        showToast(data.message, 'error');
                    }
                } catch (error) {
                    showToast('Erro de conexão ao definir prazo.', 'error');
                }
            }
        },

        /**
         * Lida com o clique no botão 'Remover Prazo'.
         * @param {string} bookId
         */
        async onRemoveDeadline(bookId) {
            const result = await Swal.fire({
                title: 'Remover Prazo?',
                text: "Tem certeza que deseja remover o prazo?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                confirmButtonText: 'Sim, remover!',
                cancelButtonText: 'Cancelar',
            });

            if (result.isConfirmed) {
                try {
                    const response = await fetch('/api/reading/remove-deadline/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                        body: JSON.stringify({ book_id: bookId }),
                    });
                    const data = await response.json();
                    if (data.success) {
                        showToast(data.message, 'success');
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        showToast(data.message, 'error');
                    }
                } catch (error) {
                    showToast('Erro de conexão ao remover prazo.', 'error');
                }
            }
        },
    },
};

/**
 * =========================================================================
 * 3. Módulo: NotificationManager
 * Sistema completo de gerenciamento de notificações
 * =========================================================================
 */
const NotificationManager = {
    /**
     * Configurações e preferências
     */
    settings: {
        pollingInterval: 90000,  // 90 segundos
        soundEnabled: true,      // Som ativo por padrão
        filters: {
            status: 'unread',    // 'all', 'unread', 'read'
            category: 'all',     // 'all', 'reading', 'system'
            priority: 'all'      // 'all', 1, 2, 3
        }
    },

    /**
     * Estado do componente
     */
    state: {
        currentPage: 1,
        hasNextPage: true,
        isLoading: false,
        hasInitialized: false,
        isEditMode: false,
        pollingTimer: null,
        lastUnreadCount: 0,
        isTabActive: true
    },

    /**
     * Cache de elementos do DOM
     */
    elements: {
        toggle: document.querySelector('.notifications-toggle'),
        dropdown: document.querySelector('.notifications-dropdown'),
        list: document.querySelector('.notifications-list'),
        loader: document.getElementById('notifications-loader'),
        badge: document.querySelector('.notifications-badge'),
        normalModeActions: document.querySelector('.notifications-header-actions[data-mode="normal"]'),
        editModeActions: document.querySelector('.notifications-header-actions[data-mode="edit"]'),
        soundToggle: null,  // Será criado dinamicamente
        filterStatus: null, // Será criado dinamicamente
        filterCategory: null, // Será criado dinamicamente
    },

    /**
     * Inicialização do sistema
     */
    init() {
        if (!this.elements.toggle || !this.elements.dropdown) {
            console.warn('⚠️ Elementos de notificação não encontrados');
            return;
        }

        console.log('🔔 Notification Manager V3 inicializado.');

        // Carregar preferências do localStorage
        this.loadPreferences();

        // Criar controles adicionais
        this.ui.createControls();

        // Anexar event listeners
        this.attachEventListeners();

        // Buscar contador inicial
        setTimeout(() => {
            this.api.fetchUnreadCount();
        }, 1000);

        // Iniciar polling
        this.startPolling();

        // Monitorar visibilidade da aba
        this.monitorTabVisibility();
    },

    /**
     * Anexa event listeners
     */
    attachEventListeners() {
        const { elements } = this;

        // Toggle dropdown
        elements.toggle.addEventListener('click', () => {
            console.log('🖱️ Sininho clicado!');
            this.handlers.onToggleDropdown();
        });

        // Scroll infinito
        elements.list?.addEventListener('scroll', () => this.handlers.onScroll());

        // Delegação de eventos no dropdown
        elements.dropdown.addEventListener('click', (e) => this.handlers.onDropdownClick(e));

        // Fechar ao clicar fora
        document.addEventListener('click', (e) => {
            const { toggle, dropdown } = elements;
            if (dropdown && !dropdown.contains(e.target) && !toggle.contains(e.target) && dropdown.classList.contains('show')) {
                this.handlers.onToggleDropdown(false);
            }
        });
    },

    /**
     * Monitora visibilidade da aba (para pausar/retomar polling)
     */
    monitorTabVisibility() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.state.isTabActive = false;
                console.log('⏸️ Polling pausado (aba inativa)');
            } else {
                this.state.isTabActive = true;
                console.log('▶️ Polling retomado');
                // Buscar atualizações imediatamente ao retornar
                this.api.fetchUnreadCount();
            }
        });
    },

    /**
     * Inicia o polling automático
     */
    startPolling() {
        // Limpar timer existente
        if (this.state.pollingTimer) {
            clearInterval(this.state.pollingTimer);
        }

        // Criar novo timer
        this.state.pollingTimer = setInterval(() => {
            // Só faz polling se a aba estiver ativa
            if (this.state.isTabActive) {
                console.log('🔄 Polling: Verificando novas notificações...');
                this.api.fetchUnreadCount();
            }
        }, this.settings.pollingInterval);

        console.log(`⏱️ Polling iniciado (${this.settings.pollingInterval / 1000}s)`);
    },

    /**
     * Para o polling
     */
    stopPolling() {
        if (this.state.pollingTimer) {
            clearInterval(this.state.pollingTimer);
            this.state.pollingTimer = null;
            console.log('⏹️ Polling parado');
        }
    },

    /**
     * Carrega preferências do localStorage
     */
    loadPreferences() {
        try {
            const saved = localStorage.getItem('notificationPreferences');
            if (saved) {
                const prefs = JSON.parse(saved);
                this.settings = { ...this.settings, ...prefs };
                console.log('📋 Preferências carregadas:', this.settings);
            }
        } catch (error) {
            console.warn('⚠️ Erro ao carregar preferências:', error);
        }
    },

    /**
     * Salva preferências no localStorage
     */
    savePreferences() {
        try {
            localStorage.setItem('notificationPreferences', JSON.stringify(this.settings));
            console.log('💾 Preferências salvas');
        } catch (error) {
            console.warn('⚠️ Erro ao salvar preferências:', error);
        }
    },

    /**
     * Handlers de eventos
     */
    handlers: {
        /**
         * Lida com cliques no dropdown
         */
        onDropdownClick(e) {
            const { handlers } = NotificationManager;
            const target = e.target;

            // Botão de marcar como lida
            const markReadBtn = target.closest('.btn-mark-read');
            if (markReadBtn && !NotificationManager.state.isEditMode) {
                e.stopPropagation();
                const notifId = markReadBtn.dataset.notificationId;
                const category = markReadBtn.dataset.category;
                handlers.onMarkAsRead(notifId, category);
                return;
            }

            // Botões de ação
            if (target.closest('.btn-mark-all-read')) return handlers.onMarkAllAsRead();
            if (target.closest('.btn-edit-notifications')) return handlers.onToggleEditMode(true);
            if (target.closest('.btn-cancel-edit')) return handlers.onToggleEditMode(false);
            if (target.closest('.btn-delete-selected')) return handlers.onDeleteSelected();
            if (target.closest('.btn-toggle-sound')) return handlers.onToggleSound();

            // Filtros
            const filterStatus = target.closest('.filter-status');
            const filterCategory = target.closest('.filter-category');
            if (filterStatus || filterCategory) {
                handlers.onFilterChange();
            }
        },

        /**
         * Scroll infinito
         */
        onScroll() {
            const { state, elements, api } = NotificationManager;
            if (state.isLoading || !state.hasNextPage) return;

            const { scrollTop, scrollHeight, clientHeight } = elements.list;
            if (scrollHeight - scrollTop - clientHeight < 50) {
                state.currentPage++;
                api.fetchNotifications(state.currentPage);
            }
        },

        /**
         * Toggle dropdown
         */
        onToggleDropdown(forceState) {
            const { state, elements, api } = NotificationManager;
            const shouldBeOpen = typeof forceState === 'boolean' ? forceState : !elements.dropdown.classList.contains('show');

            elements.dropdown.classList.toggle('show', shouldBeOpen);

            if (shouldBeOpen) {
                if (!state.hasInitialized) {
                    api.resetAndFetch();
                    state.hasInitialized = true;
                }
            } else {
                this.onToggleEditMode(false);
            }
        },

        /**
         * Toggle modo de edição
         */
        onToggleEditMode(forceState) {
            const { state, elements } = NotificationManager;
            state.isEditMode = typeof forceState === 'boolean' ? forceState : !state.isEditMode;

            elements.dropdown.classList.toggle('edit-mode', state.isEditMode);
            elements.normalModeActions.style.display = state.isEditMode ? 'none' : 'flex';
            elements.editModeActions.style.display = state.isEditMode ? 'flex' : 'none';

            elements.list.querySelectorAll('.notification-checkbox-wrapper').forEach(el => el.style.display = state.isEditMode ? 'flex' : 'none');
            elements.list.querySelectorAll('.btn-mark-read').forEach(el => el.style.display = state.isEditMode ? 'none' : 'block');
        },

        /**
         * Toggle som
         */
        onToggleSound() {
            const { settings, elements } = NotificationManager;

            if (window.NotificationSounds) {
                const enabled = window.NotificationSounds.toggle();
                settings.soundEnabled = enabled;
                NotificationManager.savePreferences();

                // Atualizar ícone
                const icon = elements.soundToggle?.querySelector('i');
                if (icon) {
                    icon.className = enabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
                }

                showToast(enabled ? '🔊 Sons ativados' : '🔇 Sons desativados', 'info');
            }
        },

        /**
         * Marcar notificação como lida
         */
        onMarkAsRead(notificationId, category) {
            NotificationManager.api.markAsRead(notificationId, category);
        },

        /**
         * Marcar todas como lidas
         */
        onMarkAllAsRead() {
            NotificationManager.api.markAllAsRead();
        },

        /**
         * Deletar selecionadas
         */
        onDeleteSelected() {
            NotificationManager.api.deleteSelectedNotifications();
        },

        /**
         * Mudança nos filtros
         */
        onFilterChange() {
            const { elements, settings } = NotificationManager;

            // Atualizar settings
            if (elements.filterStatus) {
                settings.filters.status = elements.filterStatus.value;
            }
            if (elements.filterCategory) {
                settings.filters.category = elements.filterCategory.value;
            }

            // Salvar preferências
            NotificationManager.savePreferences();

            // Recarregar notificações
            NotificationManager.api.resetAndFetch();
        }
    },

    /**
     * Funções de API
     */
    api: {
        /**
         * Busca notificações
         */
        async fetchNotifications(page = 1) {
            const { state, elements, ui, settings } = NotificationManager;
            if (state.isLoading || (!state.hasNextPage && page > 1)) return;

            state.isLoading = true;
            if (elements.loader) elements.loader.style.display = 'block';

            try {
                const params = new URLSearchParams({
                    page: page,
                    unread_only: settings.filters.status === 'unread',
                    category: settings.filters.category
                });

                const response = await fetch(`/api/notifications/unified/?${params}`);
                const data = await response.json();

                if (data.success) {
                    if (page === 1) elements.list.innerHTML = '';
                    ui.renderNotifications(data.notifications);
                    ui.updateBadge(data.unread_count);
                    state.hasNextPage = data.has_next_page;
                }
            } catch (error) {
                console.error('Erro ao carregar notificações:', error);
            } finally {
                state.isLoading = false;
                if (elements.loader) elements.loader.style.display = 'none';
            }
        },

        /**
         * Busca apenas contador (leve)
         */
        async fetchUnreadCount() {
            const { ui, state } = NotificationManager;
            try {
                const response = await fetch('/api/notifications/unread-count/');

                if (!response.ok) {
                    console.warn('Endpoint de contador não disponível');
                    return;
                }

                const data = await response.json();

                if (data.success) {
                    const newCount = data.unread_count;

                    // Se aumentou, tocar som (nova notificação)
                    if (newCount > state.lastUnreadCount && state.lastUnreadCount > 0) {
                        console.log('🔔 Nova notificação detectada!');
                        if (window.NotificationSounds && NotificationManager.settings.soundEnabled) {
                            window.NotificationSounds.play(2); // Prioridade média
                        }
                    }

                    state.lastUnreadCount = newCount;
                    ui.updateBadge(newCount);
                }
            } catch (error) {
                console.warn('Erro no contador:', error.message);
            }
        },

        /**
         * Marcar como lida
         */
        async markAsRead(notificationId, category) {
            const { elements, ui, api } = NotificationManager;
            const item = elements.list.querySelector(`.notification-item[data-notification-id="${notificationId}"]`);
            if (!item || item.classList.contains('read')) return;

            try {
                const response = await fetch('/api/notifications/unified/mark-read/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        notification_id: notificationId,
                        category: category
                    })
                });

                const data = await response.json();
                if (data.success) {
                    item.classList.remove('unread');
                    item.classList.add('read');
                    item.querySelector('.btn-mark-read')?.remove();
                    ui.updateBadge(data.unread_count);
                }
            } catch (error) {
                console.error('Erro ao marcar notificação:', error);
            }
        },

        /**
         * Marcar todas como lidas
         */
        async markAllAsRead() {
            try {
                const response = await fetch('/api/notifications/unified/mark-all-read/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();
                if (data.success && data.updated_count > 0) {
                    showToast(data.message, 'success');
                    this.resetAndFetch();
                }
            } catch (error) {
                console.error('Erro ao marcar todas:', error);
            }
        },

        /**
         * Deletar notificações selecionadas
         */
        async deleteSelectedNotifications() {
            const { elements, handlers, api } = NotificationManager;
            const selected = elements.list.querySelectorAll('.notification-select-checkbox:checked');
            if (selected.length === 0) return showToast('Nenhuma notificação selecionada.', 'warning');

            const notifications = Array.from(selected).map(cb => ({
                id: parseInt(cb.value, 10),
                category: cb.dataset.category
            }));

            const result = await Swal.fire({
                title: 'Deletar Notificações?',
                text: `Tem certeza que deseja deletar ${notifications.length} notificação(ões)?`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                confirmButtonText: 'Sim, deletar!',
                cancelButtonText: 'Cancelar',
            });

            if (!result.isConfirmed) return;

            try {
                const response = await fetch('/api/notifications/unified/delete-selected/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ notifications })
                });

                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    showToast(data.message, 'success');
                    handlers.onToggleEditMode(false);
                    api.resetAndFetch();
                } else {
                    showToast(data.message || 'Erro ao deletar.', 'error');
                }
            } catch (error) {
                console.error('Erro ao deletar:', error);
                showToast('Erro de conexão. Tente novamente.', 'error');
            }
        },

        /**
         * Reseta e recarrega
         */
        resetAndFetch() {
            const { state, elements, api } = NotificationManager;
            state.currentPage = 1;
            state.hasNextPage = true;
            state.isLoading = false;
            elements.list.innerHTML = '';
            api.fetchNotifications(1);
        }
    },

    /**
     * Funções de UI
     */
    ui: {
        /**
         * Cria controles adicionais (som, filtros)
         */
        createControls() {
            const { elements, settings } = NotificationManager;
            const header = elements.dropdown.querySelector('.notifications-header');

            if (!header) return;

            // Botão de som
            const soundBtn = document.createElement('button');
            soundBtn.className = 'btn-toggle-sound';
            soundBtn.title = 'Ativar/Desativar sons';
            soundBtn.innerHTML = `<i class="fas fa-volume-${settings.soundEnabled ? 'up' : 'mute'}"></i>`;
            header.appendChild(soundBtn);
            elements.soundToggle = soundBtn;

            // Filtros
            const filtersDiv = document.createElement('div');
            filtersDiv.className = 'notification-filters';
            filtersDiv.innerHTML = `
                <select class="filter-status">
                    <option value="all">Todas</option>
                    <option value="unread" ${settings.filters.status === 'unread' ? 'selected' : ''}>Não Lidas</option>
                    <option value="read" ${settings.filters.status === 'read' ? 'selected' : ''}>Lidas</option>
                </select>
                <select class="filter-category">
                    <option value="all">Todas</option>
                    <option value="reading">📚 Leitura</option>
                    <option value="system">🔔 Sistema</option>
                </select>
            `;

            header.appendChild(filtersDiv);
            elements.filterStatus = filtersDiv.querySelector('.filter-status');
            elements.filterCategory = filtersDiv.querySelector('.filter-category');
        },

        /**
         * Renderiza notificações
         */
        renderNotifications(notifications) {
            const { state, elements } = NotificationManager;

            if (notifications.length === 0 && state.currentPage === 1) {
                elements.list.innerHTML = '<div class="notification-empty">📭 Nenhuma notificação</div>';
                return;
            }

            const fragment = document.createDocumentFragment();

            notifications.forEach(notif => {
                const item = document.createElement('div');
                item.className = `notification-item ${notif.is_read ? 'read' : 'unread'} category-${notif.category}`;
                item.dataset.notificationId = notif.id;
                item.dataset.category = notif.category;

                // Chip de categoria
                const categoryChip = `<span class="category-chip category-${notif.category}">${notif.category === 'reading' ? '📚' : '🔔'}</span>`;

                // Botão de ação
                const actionBtn = notif.action_url ?
                    `<a href="${notif.action_url}" class="btn-notification-action">${notif.action_text || 'Ver'}</a>` : '';

                item.innerHTML = `
                    <div class="notification-checkbox-wrapper" style="display: ${state.isEditMode ? 'flex' : 'none'};">
                        <input type="checkbox" class="notification-select-checkbox" value="${notif.id}" data-category="${notif.category}">
                    </div>
                    <div class="notification-icon"><i class="${notif.icon_class}"></i></div>
                    <div class="notification-content">
                        <div class="notification-title">
                            ${categoryChip}
                            ${notif.type_display}
                        </div>
                        ${notif.book_title ? `<div class="notification-book">${notif.book_title}</div>` : ''}
                        <div class="notification-message">${notif.message}</div>
                        <div class="notification-footer">
                            <span class="notification-time">${notif.formatted_time}</span>
                            ${actionBtn}
                        </div>
                    </div>
                    ${!notif.is_read && !state.isEditMode ?
                        `<button class="btn-mark-read" data-notification-id="${notif.id}" data-category="${notif.category}" title="Marcar como lida">
                            <i class="fas fa-check"></i>
                        </button>` : ''}
                `;

                fragment.appendChild(item);
            });

            elements.list.appendChild(fragment);
        },

        /**
         * Atualiza badge
         */
        updateBadge(count) {
            const { badge } = NotificationManager.elements;
            if (!badge) return;

            if (count > 0) {
                badge.textContent = count > 9 ? '9+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }
};

// =========================================================================
// 4. Inicializadores Globais
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
    ReadingProgressManager.init();
    NotificationManager.init();
});