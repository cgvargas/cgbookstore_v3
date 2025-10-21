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

    /**
     * Atualiza o contador de uma prateleira personalizada na sidebar.
     * @param {HTMLElement} gridElement - Elemento da grid da prateleira
     */
    function updateCustomShelfCount(gridElement) {
        if (!gridElement) return;

        // Verificar se é uma prateleira personalizada
        const customShelfName = gridElement.dataset.customShelf;
        if (!customShelfName) return;

        // Contar livros restantes
        const remainingBooks = gridElement.querySelectorAll('.book-card').length;

        // Atualizar contador na sidebar
        const sidebarItem = document.querySelector(`[data-custom-name="${customShelfName}"]`);
        if (sidebarItem) {
            const countElement = sidebarItem.querySelector('.count');
            if (countElement) {
                countElement.textContent = remainingBooks;
            }
        }

        // Atualizar header da página se estiver visualizando esta prateleira
        const shelfCountHeader = document.getElementById('shelf-count');
        const currentShelfName = document.getElementById('shelf-title')?.textContent;
        if (shelfCountHeader && currentShelfName === customShelfName) {
            shelfCountHeader.textContent = remainingBooks;
        }
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
                // Atualizar contadores de prateleiras padrão
                updateShelfCounts(data.shelf_counts);

                // Localizar TODOS os cards do livro (pode estar em múltiplos lugares)
                const bookCards = document.querySelectorAll(`[data-bookshelf-id="${bookshelfId}"]`);

                bookCards.forEach(bookCard => {
                    // Aplicar animação fade-out
                    bookCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    bookCard.style.opacity = '0';
                    bookCard.style.transform = 'scale(0.8)';

                    // Remover do DOM após animação
                    setTimeout(() => {
                        const parentGrid = bookCard.closest('.books-grid');
                        const parentManageList = bookCard.closest('#books-list');

                        bookCard.remove();

                        // Se for na grid principal, verificar se ficou vazia
                        if (parentGrid && !parentManageList) {
                            const remainingBooks = parentGrid.querySelectorAll('.book-card');

                            if (remainingBooks.length === 0) {
                                const shelfTitle = document.getElementById('shelf-title')?.textContent || 'Prateleira';
                                const shelfType = getCurrentShelfType();
                                const emptyMessage = createEmptyShelfMessage(shelfTitle, shelfType);
                                parentGrid.innerHTML = emptyMessage;
                            }
                        }

                        // Se for no modal de gerenciamento, recarregar a lista
                        if (parentManageList) {
                            const selectShelf = document.getElementById('select-shelf');
                            if (selectShelf && selectShelf.value) {
                                setTimeout(() => {
                                    loadShelfBooks(selectShelf.value);
                                }, 300);
                            }
                        }

                        // Atualizar contador de prateleira personalizada (se aplicável)
                        updateCustomShelfCount(parentGrid);
                    }, 300);
                });

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
    // ✅ NOVO: GERENCIAMENTO DE MODAL DE PRATELEIRA PERSONALIZADA
    // ========================================

    /**
     * Mostra modal de criar prateleira personalizada.
     * ✅ COM LIMPEZA AUTOMÁTICA DE BACKDROPS
     */
    function showCustomShelfModal() {
        const modal = document.getElementById('libraryCustomShelfModal');
        const nameInput = document.getElementById('libraryCustomShelfName');
        const errorDiv = document.getElementById('libraryCustomShelfError');

        if (!modal) {
            console.error('Modal libraryCustomShelfModal não encontrado');
            return;
        }

        // ✅ CORREÇÃO CRÍTICA: Limpar TUDO antes de abrir
        cleanupModals();

        // Limpar form
        if (nameInput) nameInput.value = '';
        if (errorDiv) errorDiv.style.display = 'none';

        try {
            // Verificar instância existente
            let bsModal = bootstrap.Modal.getInstance(modal);

            // Se existir, destruir completamente
            if (bsModal) {
                bsModal.dispose();
                bsModal = null;
            }

            // Criar nova instância limpa
            bsModal = new bootstrap.Modal(modal, {
                backdrop: true,
                keyboard: true,
                focus: false
            });

            // Focar no input após modal abrir
            modal.addEventListener('shown.bs.modal', function focusInput() {
                setTimeout(() => {
                    if (nameInput) nameInput.focus();
                }, 150);
            }, { once: true });

            // ✅ NOVO: Limpar quando modal fechar
            modal.addEventListener('hidden.bs.modal', function cleanup() {
                cleanupModals();
            }, { once: true });

            // Mostrar modal
            bsModal.show();

        } catch (error) {
            console.error('Erro ao abrir modal:', error);
            cleanupModals(); // Limpar mesmo em caso de erro
            showToast('Erro ao abrir modal. Tente novamente.', 'error');
        }
    }

    /**
     * ✅ NOVA FUNÇÃO: Limpa todos os resíduos de modais
     */
    function cleanupModals() {
        // Remover todos os backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());

        // Remover classe modal-open do body
        document.body.classList.remove('modal-open');

        // Restaurar overflow do body
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';

        // Forçar remoção de atributos aria
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = '';
            modal.classList.remove('show');
            modal.removeAttribute('aria-modal');
            modal.removeAttribute('role');
            modal.setAttribute('aria-hidden', 'true');
        });

        console.log('🧹 Modais limpos');
    }

    /**
     * Cria prateleira personalizada a partir do modal.
     */
    function createCustomShelfFromModal() {
        const nameInput = document.getElementById('libraryCustomShelfName');
        const errorDiv = document.getElementById('libraryCustomShelfError');
        const createBtn = document.getElementById('libraryCreateCustomShelfBtn');

        if (!nameInput) {
            console.error('Input libraryCustomShelfName não encontrado');
            return;
        }

        const customShelfName = nameInput.value.trim();

        // Validação
        if (!customShelfName) {
            if (errorDiv) {
                errorDiv.textContent = 'Por favor, insira um nome para a prateleira.';
                errorDiv.style.display = 'block';
            }
            nameInput.focus();
            return;
        }

        if (customShelfName.length > 100) {
            if (errorDiv) {
                errorDiv.textContent = 'Nome muito longo (máximo 100 caracteres).';
                errorDiv.style.display = 'block';
            }
            return;
        }

        // Loading
        if (createBtn) {
            createBtn.disabled = true;
            createBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Criando...';
        }
        if (errorDiv) errorDiv.style.display = 'none';

        // Criar prateleira
        createCustomShelf(customShelfName)
            .then(data => {
                if (data.success) {
                    // Fechar modal
                    const modal = document.getElementById('libraryCustomShelfModal');
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();

                    // Recarregar página
                    showToast('Prateleira criada! Recarregando...', 'success', 1500);
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    // Mostrar erro
                    if (errorDiv) {
                        errorDiv.textContent = data.message;
                        errorDiv.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Erro ao criar prateleira:', error);
                if (errorDiv) {
                    errorDiv.textContent = 'Erro ao criar prateleira. Tente novamente.';
                    errorDiv.style.display = 'block';
                }
            })
            .finally(() => {
                // Restaurar botão
                if (createBtn) {
                    createBtn.disabled = false;
                    createBtn.innerHTML = '<i class="fas fa-check me-2"></i>Criar Prateleira';
                }
            });
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
    // GERENCIAMENTO AVANÇADO DE PRATELEIRAS
    // ========================================

    /**
     * Carrega a lista de prateleiras personalizadas no modal.
     */
    async function loadCustomShelvesList() {
        const container = document.getElementById('shelves-list');
        if (!container) return;

        try {
            // Pegar prateleiras do DOM (já carregadas no template)
            const customShelvesNav = document.querySelectorAll('[data-shelf-type="custom"]');

            if (customShelvesNav.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-folder-open fa-3x mb-3"></i>
                        <p>Você ainda não tem prateleiras personalizadas.</p>
                        <p class="small">Clique em "Nova Prateleira" para criar uma.</p>
                    </div>
                `;
                return;
            }

            let html = '';
            customShelvesNav.forEach(nav => {
                const shelfName = nav.dataset.customName;
                const count = nav.querySelector('.count')?.textContent || '0';

                html += `
                    <div class="shelf-item">
                        <div class="shelf-item-info">
                            <i class="fas fa-folder"></i>
                            <div class="shelf-item-details">
                                <h6>${shelfName}</h6>
                                <small>${count} livro(s)</small>
                            </div>
                        </div>
                        <div class="shelf-item-actions">
                            <button class="btn btn-sm btn-outline-primary btn-xs"
                                    onclick="LibraryManager.renameCustomShelf('${shelfName.replace(/'/g, "\\'")}')">
                                <i class="fas fa-edit"></i> Renomear
                            </button>
                            <button class="btn btn-sm btn-outline-danger btn-xs"
                                    onclick="LibraryManager.deleteCustomShelf('${shelfName.replace(/'/g, "\\'")}')">
                                <i class="fas fa-trash"></i> Deletar
                            </button>
                        </div>
                    </div>
                `;
            });

            container.innerHTML = html;

        } catch (error) {
            console.error('Erro ao carregar prateleiras:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erro ao carregar prateleiras. Tente novamente.
                </div>
            `;
        }
    }

    /**
     * Deleta uma prateleira personalizada.
     * @param {string} shelfName - Nome da prateleira a deletar
     */
    async function deleteCustomShelf(shelfName) {
        // Confirmação com SweetAlert2 (se disponível) ou confirm nativo
        const confirmed = typeof Swal !== 'undefined'
            ? await Swal.fire({
                title: 'Deletar Prateleira?',
                html: `
                    <p>Tem certeza que deseja deletar a prateleira <strong>"${shelfName}"</strong>?</p>
                    <p class="text-danger small">⚠️ Todos os livros desta prateleira serão removidos!</p>
                `,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sim, deletar!',
                cancelButtonText: 'Cancelar'
            }).then(result => result.isConfirmed)
            : confirm(`Tem certeza que deseja deletar a prateleira "${shelfName}"?\n\nTodos os livros serão removidos!`);

        if (!confirmed) return;

        try {
            const response = await fetch('/api/library/delete-custom-shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ shelf_name: shelfName })
            });

            const data = await response.json();

            if (data.success) {
                showToast(`${data.message} (${data.deleted_books_count} livro(s) removidos)`, 'success');

                // Recarregar página após 1.5s
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.message || 'Erro ao deletar prateleira.', 'error');
            }

        } catch (error) {
            console.error('Erro ao deletar prateleira:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        }
    }

    /**
     * Renomeia uma prateleira personalizada.
     * @param {string} oldName - Nome atual da prateleira
     */
    async function renameCustomShelf(oldName) {
        // Prompt com SweetAlert2 (se disponível) ou prompt nativo
        let newName;

        if (typeof Swal !== 'undefined') {
            const result = await Swal.fire({
                title: 'Renomear Prateleira',
                html: `
                    <p class="mb-2">Nome atual: <strong>${oldName}</strong></p>
                    <input type="text" id="new-shelf-name" class="swal2-input"
                           placeholder="Novo nome" value="${oldName}" maxlength="100">
                `,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Renomear',
                cancelButtonText: 'Cancelar',
                preConfirm: () => {
                    const input = document.getElementById('new-shelf-name');
                    const value = input.value.trim();
                    if (!value) {
                        Swal.showValidationMessage('O nome não pode ser vazio');
                        return false;
                    }
                    if (value.length > 100) {
                        Swal.showValidationMessage('Nome muito longo (máx: 100 caracteres)');
                        return false;
                    }
                    return value;
                }
            });

            if (!result.isConfirmed) return;
            newName = result.value;
        } else {
            newName = prompt(`Renomear prateleira "${oldName}".\n\nNovo nome:`, oldName);
            if (!newName || newName.trim() === '') return;
            newName = newName.trim();
        }

        try {
            const response = await fetch('/api/library/rename-custom-shelf/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ old_name: oldName, new_name: newName })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');

                // Recarregar página após 1.5s
                setTimeout(() => location.reload(), 1500);
            } else {
                showToast(data.message || 'Erro ao renomear prateleira.', 'error');
            }

        } catch (error) {
            console.error('Erro ao renomear prateleira:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        }
    }

    /**
     * Carrega os livros de uma prateleira no modal de gerenciamento.
     * @param {string} shelfValue - Valor do select (ex: "favorites", "custom:Nome")
     */
    async function loadShelfBooks(shelfValue) {
        const container = document.getElementById('books-list');
        if (!container || !shelfValue) {
            container.innerHTML = `
                <div class="text-muted text-center py-4">
                    <i class="fas fa-arrow-up fa-2x mb-2"></i>
                    <p>Selecione uma prateleira acima para gerenciar seus livros.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `;

        try {
            // Parse shelf type e name
            let shelfType, customName;
            if (shelfValue.startsWith('custom:')) {
                shelfType = 'custom';
                customName = shelfValue.substring(7); // Remove "custom:"
            } else {
                shelfType = shelfValue;
                customName = '';
            }

            // Buscar livros da prateleira (via DOM - mais simples)
            const shelfGrid = shelfType === 'custom'
                ? document.querySelector('[data-custom-shelf="' + customName + '"]')
                : document.getElementById('shelf-' + shelfType);

            if (!shelfGrid) {
                container.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Prateleira não encontrada.
                    </div>
                `;
                return;
            }

            const bookCards = shelfGrid.querySelectorAll('.book-card');

            if (bookCards.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-book-open fa-3x mb-3"></i>
                        <p>Esta prateleira está vazia.</p>
                    </div>
                `;
                return;
            }

            // ✅ CORREÇÃO: Construir HTML de forma mais segura
            const bookItems = [];

            bookCards.forEach(card => {
                const bookshelfId = card.dataset.bookshelfId;
                const bookTitle = card.querySelector('.book-title')?.textContent || 'Sem título';
                const bookAuthor = card.querySelector('.book-author')?.textContent || 'Autor desconhecido';
                const bookCoverImg = card.querySelector('.book-cover');
                const bookCover = bookCoverImg ? bookCoverImg.src : '/static/images/no-cover.jpg';
                const bookNotes = card.dataset.notes || '';

                // Escapar HTML para segurança
                const escapedTitle = escapeHtml(bookTitle);
                const escapedAuthor = escapeHtml(bookAuthor);
                const escapedNotes = escapeHtml(bookNotes);

                bookItems.push(`
                    <div class="book-manage-item" data-bookshelf-id="${bookshelfId}">
                        <img src="${bookCover}" alt="${escapedTitle}" class="book-manage-cover" onerror="this.src='/static/images/no-cover.jpg'">
                        <div class="book-manage-info">
                            <h6>${escapedTitle}</h6>
                            <small><i class="fas fa-user me-1"></i>${escapedAuthor}</small>
                            ${escapedNotes ? '<small class="text-muted"><i class="fas fa-sticky-note me-1"></i>' + escapedNotes + '</small>' : ''}
                        </div>
                        <div class="book-manage-actions">
                            <button class="btn btn-sm btn-outline-primary btn-xs"
                                    onclick="LibraryManager.updateBookNotes(${bookshelfId})"
                                    title="Editar notas">
                                <i class="fas fa-edit"></i> Notas
                            </button>
                            <button class="btn btn-sm btn-outline-danger btn-xs"
                                    onclick="LibraryManager.removeFromShelf(${bookshelfId})"
                                    title="Remover da prateleira">
                                <i class="fas fa-trash"></i> Remover
                            </button>
                        </div>
                    </div>
                `);
            });

            container.innerHTML = bookItems.join('');

        } catch (error) {
            console.error('Erro ao carregar livros:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erro ao carregar livros. Tente novamente.
                </div>
            `;
        }
    }

    /**
     * Escapa HTML para prevenir XSS
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Atualiza as notas de um livro.
     * @param {number} bookshelfId - ID do BookShelf
     */
    async function updateBookNotes(bookshelfId) {
        // Buscar notas atuais do card
        const bookItem = document.querySelector(`[data-bookshelf-id="${bookshelfId}"]`);
        const currentNotes = bookItem?.dataset.notes || '';
        const bookTitle = bookItem?.querySelector('h6')?.textContent || 'Livro';

        // Prompt com SweetAlert2 ou prompt nativo
        let newNotes;

        if (typeof Swal !== 'undefined') {
            const result = await Swal.fire({
                title: 'Editar Notas',
                html: `
                    <p class="mb-2"><strong>${bookTitle}</strong></p>
                    <textarea id="book-notes" class="swal2-textarea"
                              placeholder="Suas anotações sobre este livro..."
                              style="height: 150px;">${currentNotes}</textarea>
                `,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Salvar',
                cancelButtonText: 'Cancelar',
                preConfirm: () => {
                    return document.getElementById('book-notes').value.trim();
                }
            });

            if (!result.isConfirmed) return;
            newNotes = result.value;
        } else {
            newNotes = prompt(`Editar notas para "${bookTitle}":`, currentNotes);
            if (newNotes === null) return; // Cancelou
            newNotes = newNotes.trim();
        }

        try {
            const response = await fetch('/api/library/update-book-notes/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    bookshelf_id: bookshelfId,
                    notes: newNotes
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');

                // Recarregar lista de livros da prateleira atual
                const selectShelf = document.getElementById('select-shelf');
                if (selectShelf && selectShelf.value) {
                    // Aguardar toast antes de recarregar
                    setTimeout(() => {
                        loadShelfBooks(selectShelf.value);
                    }, 800);
                }

                // Também atualizar no book-card principal se existir
                const mainBookCard = document.querySelector(`.books-grid .book-card[data-bookshelf-id="${bookshelfId}"]`);
                if (mainBookCard) {
                    mainBookCard.dataset.notes = newNotes;
                }
            } else {
                showToast(data.message || 'Erro ao atualizar notas.', 'error');
            }

        } catch (error) {
            console.error('Erro ao atualizar notas:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        }
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
        addLibraryButton: addLibraryButton,
        // Gerenciamento avançado
        loadCustomShelvesList: loadCustomShelvesList,
        deleteCustomShelf: deleteCustomShelf,
        renameCustomShelf: renameCustomShelf,
        loadShelfBooks: loadShelfBooks,
        updateBookNotes: updateBookNotes,
        // ✅ NOVOS: Métodos para modal de prateleira personalizada
        showCustomShelfModal: showCustomShelfModal,
        createCustomShelfFromModal: createCustomShelfFromModal,
        cleanupModals: cleanupModals
    };
})();

// ✅ CORREÇÃO: Expor LibraryManager globalmente
window.LibraryManager = LibraryManager;

// Auto-inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', LibraryManager.init);
} else {
    LibraryManager.init();
}

// Inicializar modal de gerenciamento quando abrir
document.addEventListener('DOMContentLoaded', function() {
    const manageModal = document.getElementById('manageShelvesModal');
    if (manageModal) {
        manageModal.addEventListener('show.bs.modal', function() {
            LibraryManager.loadCustomShelvesList();
        });
    }
});

// Função global para loadShelfBooks (chamada pelo select no template)
function loadShelfBooks(shelfValue) {
    LibraryManager.loadShelfBooks(shelfValue);
}