/**
 * Library Manager - Sistema de Gestão da Biblioteca Pessoal
 * CGBookStore v3
 *
 * Gerencia adição, remoção e movimentação de livros na biblioteca pessoal.
 * Integrado com Django REST API.
 */

const LibraryManager = (function() {
    'use strict';

    // ========================================
    // UTILIDADES
    // ========================================

    /**
     * Obtém o CSRF token dos cookies.
     * @returns {string|null} CSRF token ou null
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
     * Exibe um toast de notificação.
     * @param {string} message - Mensagem a exibir
     * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duração em ms (padrão: 3000)
     */
    function showToast(message, type = 'info', duration = 3000) {
        // Remover toasts anteriores
        const existingToasts = document.querySelectorAll('.library-toast');
        existingToasts.forEach(toast => toast.remove());

        // Criar container se não existir
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
            `;
            document.body.appendChild(container);
        }

        // Mapear tipos para cores de borda e texto
        const colorMap = {
            'success': {
                border: '#28a745',
                text: '#28a745',
                icon: 'fa-check-circle'
            },
            'error': {
                border: '#dc3545',
                text: '#dc3545',
                icon: 'fa-exclamation-circle'
            },
            'warning': {
                border: '#ffc107',
                text: '#ffc107',
                icon: 'fa-exclamation-triangle'
            },
            'info': {
                border: '#17a2b8',
                text: '#17a2b8',
                icon: 'fa-info-circle'
            }
        };

        const colors = colorMap[type] || colorMap.info;

        // Criar toast
        const toast = document.createElement('div');
        toast.className = 'library-toast alert d-flex align-items-center';
        toast.style.cssText = `
            min-width: 300px;
            max-width: 500px;
            background-color: transparent;
            border: 2px solid ${colors.border};
            color: ${colors.text};
            font-weight: 500;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            animation: slideInRight 0.3s ease-out;
        `;

        toast.innerHTML = `
            <i class="fas ${colors.icon} me-2" style="font-size: 1.2rem;"></i>
            <span style="flex-grow: 1;">${message}</span>
            <button type="button" class="btn-close ms-2" data-bs-dismiss="alert" style="filter: invert(${type === 'success' ? '0.5' : '0'}) sepia(1) saturate(5) hue-rotate(${type === 'success' ? '90' : '0'}deg);"></button>
        `;

        container.appendChild(toast);

        // Auto-remover após duração
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Mostra indicador de loading no botão.
     * @param {HTMLElement} button - Elemento do botão
     * @param {boolean} loading - true para mostrar, false para esconder
     */
    function setButtonLoading(button, loading) {
        if (!button) return;

        if (loading) {
            button.dataset.originalContent = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalContent || button.innerHTML;
        }
    }

    /**
     * Atualiza os contadores de prateleiras na UI.
     * @param {Object} counts - Objeto com contadores {favorites: 0, to_read: 1, ...}
     */
    function updateShelfCounts(counts) {
        if (!counts) return;

        const countMap = {
            'favorites': ['favorites-count', 'badge-favorites'],
            'to_read': ['to-read-count', 'badge-to-read'],
            'reading': ['reading-count', 'badge-reading'],
            'read': ['read-count', 'badge-read'],
            'abandoned': ['abandoned-count', 'badge-abandoned']
        };

        Object.keys(counts).forEach(shelfType => {
            const ids = countMap[shelfType];
            if (ids) {
                ids.forEach(id => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = counts[shelfType];
                    }
                });
            }
        });
    }

    // ========================================
    // API CALLS
    // ========================================

    /**
     * Adiciona um livro a uma prateleira.
     * @param {number} bookId - ID do livro
     * @param {string} shelfType - Tipo da prateleira
     * @param {string} customShelfName - Nome da prateleira personalizada (opcional)
     * @param {string} notes - Notas pessoais (opcional)
     * @returns {Promise<Object>} Resposta da API
     */
    async function addToShelf(bookId, shelfType, customShelfName = '', notes = '') {
        try {
            const response = await fetch('/api/library/add-to-shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    book_id: bookId,
                    shelf_type: shelfType,
                    custom_shelf_name: customShelfName,
                    notes: notes
                })
            });

            const data = await response.json();

            if (data.success) {
                updateShelfCounts(data.shelf_counts);
                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }

            return data;
        } catch (error) {
            console.error('Erro ao adicionar livro:', error);
            showToast('Erro ao conectar com o servidor.', 'error');
            return { success: false, message: error.message };
        }
    }

    /**
     * Remove um livro da prateleira.
     * @param {number} bookshelfId - ID do BookShelf
     * @returns {Promise<Object>} Resposta da API
     */
    async function removeFromShelf(bookshelfId) {
        try {
            const response = await fetch('/api/library/remove-from-shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    bookshelf_id: bookshelfId
                })
            });

            const data = await response.json();

            if (data.success) {
                // Atualizar contadores
                updateShelfCounts(data.shelf_counts);

                // Localizar o card do livro
                const bookCard = document.querySelector(`[data-bookshelf-id="${bookshelfId}"]`);

                if (bookCard) {
                    // Aplicar animação fade-out
                    bookCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    bookCard.style.opacity = '0';
                    bookCard.style.transform = 'scale(0.8)';

                    // Remover do DOM após animação
                    setTimeout(() => {
                        const parentGrid = bookCard.closest('.books-grid');
                        bookCard.remove();

                        // Verificar se a prateleira ficou vazia
                        const remainingBooks = parentGrid.querySelectorAll('.book-card');

                        if (remainingBooks.length === 0) {
                            // Obter informações da prateleira atual
                            const shelfTitle = document.getElementById('shelf-title').textContent;
                            const shelfType = getCurrentShelfType();

                            // Criar mensagem de prateleira vazia
                            const emptyMessage = createEmptyShelfMessage(shelfTitle, shelfType);
                            parentGrid.innerHTML = emptyMessage;
                        }
                    }, 300);
                }

                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }

            return data;
        } catch (error) {
            console.error('Erro ao remover livro:', error);
            showToast('Erro ao conectar com o servidor.', 'error');
            return { success: false, message: error.message };
        }
    }

    /**
     * Obtém o tipo da prateleira atual visível.
     * @returns {string} Tipo da prateleira
     */
    function getCurrentShelfType() {
        const visibleShelf = document.querySelector('.books-grid[style*="display: grid"]');
        if (visibleShelf) {
            const shelfId = visibleShelf.id;
            return shelfId.replace('shelf-', '');
        }
        return 'favorites';
    }

    /**
     * Cria HTML para mensagem de prateleira vazia.
     * @param {string} shelfTitle - Título da prateleira
     * @param {string} shelfType - Tipo da prateleira
     * @returns {string} HTML da mensagem
     */
    function createEmptyShelfMessage(shelfTitle, shelfType) {
        const icons = {
            'favorites': 'fa-heart',
            'to_read': 'fa-bookmark',
            'reading': 'fa-book-open',
            'read': 'fa-check-circle'
        };

        const icon = icons[shelfType] || 'fa-folder';

        return `
            <div class="empty-shelf" style="grid-column: 1 / -1;">
                <i class="fas ${icon}"></i>
                <h4>Nenhum livro em ${shelfTitle}</h4>
                <p>Adicione livros a esta prateleira para vê-los aqui!</p>
                <a href="/livros/" class="btn btn-primary mt-3">
                    Explorar Livros
                </a>
            </div>
        `;
    }

    /**
     * Move um livro para outra prateleira.
     * @param {number} bookshelfId - ID do BookShelf
     * @param {string} newShelfType - Novo tipo de prateleira
     * @param {string} newCustomShelfName - Novo nome da prateleira personalizada (opcional)
     * @returns {Promise<Object>} Resposta da API
     */
    async function moveToShelf(bookshelfId, newShelfType, newCustomShelfName = '') {
        try {
            const response = await fetch('/api/library/move-to-shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    bookshelf_id: bookshelfId,
                    new_shelf_type: newShelfType,
                    new_custom_shelf_name: newCustomShelfName
                })
            });

            const data = await response.json();

            if (data.success) {
                updateShelfCounts(data.shelf_counts);
                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }

            return data;
        } catch (error) {
            console.error('Erro ao mover livro:', error);
            showToast('Erro ao conectar com o servidor.', 'error');
            return { success: false, message: error.message };
        }
    }

    /**
     * Obtém as prateleiras de um livro.
     * @param {number} bookId - ID do livro
     * @returns {Promise<Object>} Resposta da API
     */
    async function getBookShelves(bookId) {
        try {
            const response = await fetch(`/api/library/get-book-shelves/${bookId}/`);
            const data = await response.json();

            if (!data.success) {
                showToast(data.message, 'error');
            }

            return data;
        } catch (error) {
            console.error('Erro ao buscar prateleiras:', error);
            showToast('Erro ao conectar com o servidor.', 'error');
            return { success: false, message: error.message };
        }
    }

    /**
     * Cria uma prateleira personalizada.
     * @param {string} customShelfName - Nome da prateleira
     * @returns {Promise<Object>} Resposta da API
     */
    async function createCustomShelf(customShelfName) {
        try {
            const response = await fetch('/api/library/create-custom-shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    custom_shelf_name: customShelfName
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
            } else {
                showToast(data.message, 'error');
            }

            return data;
        } catch (error) {
            console.error('Erro ao criar prateleira:', error);
            showToast('Erro ao conectar com o servidor.', 'error');
            return { success: false, message: error.message };
        }
    }

    // ========================================
    // UI HELPERS
    // ========================================

    /**
     * Adiciona botão "Adicionar à Biblioteca" em um elemento.
     * @param {HTMLElement} element - Elemento onde adicionar o botão
     * @param {number} bookId - ID do livro
     */
    function addLibraryButton(element, bookId) {
        const button = document.createElement('button');
        button.className = 'btn btn-primary btn-add-to-library';
        button.dataset.bookId = bookId;
        button.innerHTML = '<i class="fas fa-book-reader me-2"></i>Adicionar à Biblioteca';

        button.addEventListener('click', function() {
            showAddToLibraryModal(bookId);
        });

        element.appendChild(button);
    }

    /**
     * Mostra modal para escolher prateleira.
     * @param {number} bookId - ID do livro
     */
    function showAddToLibraryModal(bookId) {
        // Implementação do modal será na FASE 4
        // Por enquanto, adiciona direto em "Quero Ler"
        addToShelf(bookId, 'to_read');
    }

    // ========================================
    // INICIALIZAÇÃO
    // ========================================

    /**
     * Inicializa os event listeners.
     */
    function init() {
        console.log('📚 Library Manager inicializado');

        // Event delegation para botões dinâmicos
        document.addEventListener('click', function(e) {
            // Botão adicionar à biblioteca
            if (e.target.closest('.btn-add-to-library')) {
                const button = e.target.closest('.btn-add-to-library');
                const bookId = button.dataset.bookId;
                if (bookId) {
                    setButtonLoading(button, true);
                    addToShelf(parseInt(bookId), 'to_read')
                        .finally(() => setButtonLoading(button, false));
                }
            }

            // Botão remover da biblioteca
            if (e.target.closest('.btn-remove-from-library')) {
                const button = e.target.closest('.btn-remove-from-library');
                const bookshelfId = button.dataset.bookshelfId;
                if (bookshelfId && confirm('Deseja remover este livro da biblioteca?')) {
                    setButtonLoading(button, true);
                    removeFromShelf(parseInt(bookshelfId))
                        .then(data => {
                            if (data.success) {
                                // Remover card da UI
                                const card = button.closest('.card');
                                if (card) {
                                    card.style.animation = 'fadeOut 0.3s ease-out';
                                    setTimeout(() => card.remove(), 300);
                                }
                            }
                        })
                        .finally(() => setButtonLoading(button, false));
                }
            }

            // Botão mover para prateleira
            if (e.target.closest('.btn-move-to-shelf')) {
                const button = e.target.closest('.btn-move-to-shelf');
                const bookshelfId = button.dataset.bookshelfId;
                const newShelfType = button.dataset.shelfType;
                if (bookshelfId && newShelfType) {
                    setButtonLoading(button, true);
                    moveToShelf(parseInt(bookshelfId), newShelfType)
                        .finally(() => setButtonLoading(button, false));
                }
            }
        });

        // Adicionar estilos de animação
        addAnimationStyles();
    }

    /**
     * Adiciona estilos CSS para animações.
     */
    function addAnimationStyles() {
        if (document.getElementById('library-manager-styles')) return;

        const style = document.createElement('style');
        style.id = 'library-manager-styles';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }

            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }

            @keyframes fadeOut {
                from {
                    opacity: 1;
                    transform: scale(1);
                }
                to {
                    opacity: 0;
                    transform: scale(0.95);
                }
            }

            .library-toast {
                animation: slideInRight 0.3s ease-out;
            }
        `;
        document.head.appendChild(style);
    }

    // ========================================
    // API PÚBLICA
    // ========================================

    return {
        init: init,
        addToShelf: addToShelf,
        removeFromShelf: removeFromShelf,
        moveToShelf: moveToShelf,
        getBookShelves: getBookShelves,
        createCustomShelf: createCustomShelf,
        showToast: showToast,
        addLibraryButton: addLibraryButton
    };

})();

// Auto-inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', LibraryManager.init);
} else {
    LibraryManager.init();
}