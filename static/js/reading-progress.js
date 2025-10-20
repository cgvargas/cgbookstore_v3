/**
 * Sistema de Gerenciamento de Progresso de Leitura e Notificações
 * CGBookStore v3
 *
 * CORREÇÕES APLICADAS:
 * ✓ Método updateProgress(bookId, currentPage) - público
 * ✓ Método showDeadlineModal(bookId) - público
 * ✓ Método updateProgressFromEvent(event) - interno
 */

// ========== UTILITÁRIOS ==========

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

function showToast(message, type = 'success') {
    // Criar toast
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Animar entrada
    setTimeout(() => toast.classList.add('show'), 100);

    // Remover após 3 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ========== PROGRESSO DE LEITURA ==========

class ReadingProgressManager {
    constructor() {
        this.csrfToken = getCookie('csrftoken');
        this.init();
    }

    init() {
        // Atualizar progresso
        document.querySelectorAll('.progress-slider').forEach(slider => {
            slider.addEventListener('change', (e) => this.updateProgressFromEvent(e));
        });

        // Botões de prazo
        document.querySelectorAll('.btn-set-deadline').forEach(btn => {
            btn.addEventListener('click', (e) => this.openDeadlineModal(e));
        });

        // Botões de abandono
        document.querySelectorAll('.btn-abandon-book').forEach(btn => {
            btn.addEventListener('click', (e) => this.abandonBook(e));
        });

        // Botões de restauração
        document.querySelectorAll('.btn-restore-book').forEach(btn => {
            btn.addEventListener('click', (e) => this.restoreBook(e));
        });
    }

    /**
     * ✨ NOVO: Método público para atualizar progresso (chamado do book_detail.html)
     * @param {number} bookId - ID do livro
     * @param {number} currentPage - Página atual
     */
    async updateProgress(bookId, currentPage) {
        try {
            const response = await fetch('/api/reading/update-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    book_id: bookId,
                    current_page: currentPage
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');

                // Se completou, recarregar página
                if (data.progress.is_finished) {
                    setTimeout(() => location.reload(), 2000);
                }

                return data;
            } else {
                showToast(data.message, 'error');
                return null;
            }
        } catch (error) {
            console.error('Erro ao atualizar progresso:', error);
            showToast('Erro ao atualizar progresso', 'error');
            return null;
        }
    }

    /**
     * 🔄 MODIFICADO: Método interno para atualizar progresso via evento (biblioteca)
     */
    async updateProgressFromEvent(event) {
        const slider = event.target;
        const bookId = slider.dataset.bookId;
        const currentPage = parseInt(slider.value);
        const progressText = slider.parentElement.querySelector('.progress-text');
        const progressBar = slider.parentElement.querySelector('.progress-bar');

        const data = await this.updateProgress(bookId, currentPage);

        if (data && data.success) {
            // Atualizar UI da biblioteca
            if (progressText) {
                progressText.textContent = `${currentPage}/${data.progress.total_pages} páginas (${data.progress.percentage}%)`;
            }

            if (progressBar) {
                progressBar.style.width = `${data.progress.percentage}%`;
            }
        }
    }

    /**
     * ✨ NOVO: Método público para mostrar modal de prazo (chamado do book_detail.html)
     * @param {number} bookId - ID do livro
     */
    showDeadlineModal(bookId) {
        const modal = this.createDeadlineModal(bookId, 'este livro');
        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('show'), 10);
    }

    openDeadlineModal(event) {
        const button = event.target.closest('.btn-set-deadline');
        const bookId = button.dataset.bookId;
        const bookTitle = button.dataset.bookTitle;

        // Criar modal
        const modal = this.createDeadlineModal(bookId, bookTitle);
        document.body.appendChild(modal);

        // Mostrar modal
        setTimeout(() => modal.classList.add('show'), 10);
    }

    createDeadlineModal(bookId, bookTitle) {
        const modal = document.createElement('div');
        modal.className = 'deadline-modal';
        modal.innerHTML = `
            <div class="deadline-modal-content">
                <div class="deadline-modal-header">
                    <h3>Definir Prazo de Leitura</h3>
                    <button class="btn-close-modal">&times;</button>
                </div>
                <div class="deadline-modal-body">
                    <p><strong>${bookTitle}</strong></p>
                    <label for="deadline-date">Data limite:</label>
                    <input type="date" id="deadline-date" class="form-control"
                           min="${new Date().toISOString().split('T')[0]}">
                </div>
                <div class="deadline-modal-footer">
                    <button class="btn btn-secondary btn-cancel-deadline">Cancelar</button>
                    <button class="btn btn-primary btn-save-deadline" data-book-id="${bookId}">Salvar</button>
                </div>
            </div>
        `;

        // Event listeners
        modal.querySelector('.btn-close-modal').addEventListener('click', () => this.closeModal(modal));
        modal.querySelector('.btn-cancel-deadline').addEventListener('click', () => this.closeModal(modal));
        modal.querySelector('.btn-save-deadline').addEventListener('click', (e) => this.saveDeadline(e, modal));
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal(modal);
        });

        return modal;
    }

    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }

    async saveDeadline(event, modal) {
        const button = event.target;
        const bookId = button.dataset.bookId;
        const deadlineInput = modal.querySelector('#deadline-date');
        const deadline = deadlineInput.value;

        if (!deadline) {
            showToast('Por favor, selecione uma data', 'error');
            return;
        }

        try {
            const response = await fetch('/api/reading/set-deadline/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    book_id: bookId,
                    deadline: deadline
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
                this.closeModal(modal);
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('Erro ao definir prazo:', error);
            showToast('Erro ao definir prazo', 'error');
        }
    }

    async abandonBook(event) {
        const button = event.target.closest('.btn-abandon-book');
        const bookId = button.dataset.bookId;
        const bookTitle = button.dataset.bookTitle;

        if (!confirm(`Tem certeza que deseja abandonar "${bookTitle}"?`)) {
            return;
        }

        try {
            const response = await fetch('/api/reading/abandon-book/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    book_id: bookId
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('Erro ao abandonar livro:', error);
            showToast('Erro ao abandonar livro', 'error');
        }
    }

    async restoreBook(event) {
        const button = event.target.closest('.btn-restore-book');
        const bookId = button.dataset.bookId;

        try {
            const response = await fetch('/api/reading/restore-book/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    book_id: bookId
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('Erro ao restaurar livro:', error);
            showToast('Erro ao restaurar livro', 'error');
        }
    }
}

// ========== NOTIFICAÇÕES ==========

class NotificationManager {
    constructor() {
        this.csrfToken = getCookie('csrftoken');
        this.init();
    }

    init() {
        this.loadNotifications();

        // Dropdown toggle
        const notifToggle = document.querySelector('.notifications-toggle');
        if (notifToggle) {
            notifToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleDropdown();
            });
        }

        // Marcar todas como lidas
        const markAllBtn = document.querySelector('.btn-mark-all-read');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => this.markAllAsRead());
        }

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (e) => {
            const dropdown = document.querySelector('.notifications-dropdown');
            const toggle = document.querySelector('.notifications-toggle');
            if (dropdown && !dropdown.contains(e.target) && !toggle.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    }

    toggleDropdown() {
        const dropdown = document.querySelector('.notifications-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications/list/?limit=10');
            const data = await response.json();

            if (data.success) {
                this.updateBadge(data.unread_count);
                this.renderNotifications(data.notifications);
            }
        } catch (error) {
            console.error('Erro ao carregar notificações:', error);
        }
    }

    updateBadge(count) {
        const badge = document.querySelector('.notifications-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 9 ? '9+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    renderNotifications(notifications) {
        const container = document.querySelector('.notifications-list');
        if (!container) return;

        if (notifications.length === 0) {
            container.innerHTML = '<div class="notification-empty">Nenhuma notificação</div>';
            return;
        }

        container.innerHTML = notifications.map(notif => `
            <div class="notification-item ${notif.is_read ? 'read' : 'unread'}"
                 data-notification-id="${notif.id}">
                <div class="notification-icon">
                    <i class="${notif.icon_class}"></i>
                </div>
                <div class="notification-content">
                    <div class="notification-title">${notif.type_display}</div>
                    <div class="notification-book">${notif.book_title}</div>
                    <div class="notification-message">${notif.message}</div>
                    <div class="notification-time">${notif.formatted_time}</div>
                </div>
                ${!notif.is_read ? `
                    <button class="btn-mark-read" data-notification-id="${notif.id}">
                        <i class="fas fa-check"></i>
                    </button>
                ` : ''}
            </div>
        `).join('');

        // Event listeners para marcar como lida
        container.querySelectorAll('.btn-mark-read').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.markAsRead(btn.dataset.notificationId);
            });
        });
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch('/api/notifications/mark-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    notification_id: notificationId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar notificação:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
                this.loadNotifications();
            }
        } catch (error) {
            console.error('Erro ao marcar todas:', error);
        }
    }
}

// ========== INICIALIZAÇÃO ==========

document.addEventListener('DOMContentLoaded', () => {
    // Inicializar gerenciadores
    window.readingProgressManager = new ReadingProgressManager();
    window.notificationManager = new NotificationManager();

    // Atualizar notificações a cada 5 minutos
    setInterval(() => {
        if (window.notificationManager) {
            window.notificationManager.loadNotifications();
        }
    }, 300000); // 5 minutos
});