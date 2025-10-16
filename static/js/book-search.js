/**
 * BOOK SEARCH - Sistema de Busca e Adição de Livros
 * CGBookStore v3
 *
 * Funcionalidades:
 * - Busca paralela em catálogo local e Google Books
 * - Adição de livros à prateleira
 * - Importação automática do Google Books
 * - Feedback visual em tempo real
 */

(function() {
    'use strict';

    // ============================================
    // CONFIGURAÇÕES E CONSTANTES
    // ============================================

    const CONFIG = {
        API_ENDPOINTS: {
            SEARCH_LOCAL: '/buscar/',
            SEARCH_GOOGLE: '/api/books/search-google/',
            IMPORT_GOOGLE: '/api/books/import-google/',
            ADD_TO_SHELF: '/api/library/add-to-shelf/'
        },
        DEBOUNCE_DELAY: 500,
        DEFAULT_COVER: '/static/img/default-book-cover.jpg'
    };

    // ============================================
    // ELEMENTOS DO DOM
    // ============================================

    let elements = {};

    function initElements() {
        elements = {
            modal: document.getElementById('addBookModal'),
            searchInput: document.getElementById('bookSearchInput'),
            btnSearch: document.getElementById('btnSearchBooks'),

            // Estados
            initialState: document.getElementById('initialState'),
            loadingState: document.getElementById('loadingState'),

            // Abas
            tabsContainer: document.getElementById('searchResultsTabs'),
            localTab: document.getElementById('local-tab'),
            googleTab: document.getElementById('google-tab'),

            // Contadores
            localCount: document.getElementById('localResultsCount'),
            googleCount: document.getElementById('googleResultsCount'),

            // Containers de resultados
            localResults: document.getElementById('localResultsContainer'),
            googleResults: document.getElementById('googleResultsContainer'),
            localNoResults: document.getElementById('localNoResults'),
            googleNoResults: document.getElementById('googleNoResults'),

            // Feedback
            feedbackMessage: document.getElementById('feedbackMessage'),
            feedbackText: document.getElementById('feedbackText'),

            // Templates
            localCardTemplate: document.getElementById('localBookCardTemplate'),
            googleCardTemplate: document.getElementById('googleBookCardTemplate')
        };
    }

    // ============================================
    // GERENCIAMENTO DE ESTADO DO MODAL
    // ============================================

    function showInitialState() {
        elements.initialState.style.display = 'block';
        elements.loadingState.style.display = 'none';
        elements.tabsContainer.style.display = 'none';
        elements.localResults.innerHTML = '';
        elements.googleResults.innerHTML = '';
    }

    function showLoadingState() {
        elements.initialState.style.display = 'none';
        elements.loadingState.style.display = 'block';
        elements.tabsContainer.style.display = 'none';
    }

    function showResultsState() {
        elements.initialState.style.display = 'none';
        elements.loadingState.style.display = 'none';
        elements.tabsContainer.style.display = 'flex';
    }

    // ============================================
    // FEEDBACK VISUAL
    // ============================================

    function showFeedback(message, type = 'success') {
        elements.feedbackMessage.className = `alert alert-${type} alert-dismissible fade show`;
        elements.feedbackText.textContent = message;
        elements.feedbackMessage.style.display = 'block';

        // Auto-hide após 5 segundos
        setTimeout(() => {
            elements.feedbackMessage.style.display = 'none';
        }, 5000);
    }

    // ============================================
    // BUSCA - CATÁLOGO LOCAL
    // ============================================

    async function searchLocalCatalog(query) {
        try {
            // MUDA O ENDPOINT PARA A NOSSA NOVA API
            const url = new URL('/api/books/search-local/', window.location.origin);
            url.searchParams.append('q', query);

            const response = await fetch(url); // Não precisa de headers especiais

            if (!response.ok) {
                throw new Error('Erro na API de busca local');
            }

            const data = await response.json();

            if (data.success) {
                return data.books || []; // Retorna o array de livros com o ID correto!
            } else {
                console.warn('Busca local falhou (API):', data.message);
                return [];
            }

        } catch (error) {
            console.error('Erro na chamada da API de busca local:', error);
            return [];
        }
    }

    // ============================================
    // BUSCA - GOOGLE BOOKS
    // ============================================

    async function searchGoogleBooks(query) {
        try {
            const url = new URL(CONFIG.API_ENDPOINTS.SEARCH_GOOGLE, window.location.origin);
            url.searchParams.append('q', query);
            url.searchParams.append('max_results', 10);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao buscar no Google Books');
            }

            const data = await response.json();

            if (!data.success) {
                console.warn('Busca Google Books sem sucesso:', data.message);
                return [];
            }

            return data.books || [];

        } catch (error) {
            console.error('Erro na busca Google Books:', error);
            return [];
        }
    }

    // ============================================
    // BUSCA PARALELA
    // ============================================

    async function performSearch(query) {
        if (!query || query.trim().length < 2) {
            showFeedback('Digite pelo menos 2 caracteres para buscar', 'warning');
            return;
        }

        showLoadingState();

        try {
            // Buscar em paralelo
            const [localBooks, googleBooks] = await Promise.all([
                searchLocalCatalog(query),
                searchGoogleBooks(query)
            ]);

            // Renderizar resultados
            renderLocalResults(localBooks);
            renderGoogleResults(googleBooks);

            // Atualizar contadores
            elements.localCount.textContent = localBooks.length;
            elements.googleCount.textContent = googleBooks.length;

            // Mostrar abas
            showResultsState();

            // Se não encontrou nada em lugar nenhum
            if (localBooks.length === 0 && googleBooks.length === 0) {
                showFeedback('Nenhum livro encontrado. Tente outros termos.', 'warning');
            }

        } catch (error) {
            console.error('Erro na busca:', error);
            showFeedback('Erro ao buscar livros. Tente novamente.', 'danger');
            showInitialState();
        }
    }

    // ============================================
    // RENDERIZAÇÃO - CATÁLOGO LOCAL
    // ============================================

    function renderLocalResults(books) {
        elements.localResults.innerHTML = '';

        if (books.length === 0) {
            elements.localNoResults.style.display = 'block';
            return;
        }

        elements.localNoResults.style.display = 'none';

        books.forEach(book => {
            const card = createLocalBookCard(book);
            elements.localResults.appendChild(card);
        });
    }

    function createLocalBookCard(book) {
        const template = elements.localCardTemplate.content.cloneNode(true);
        const card = template.querySelector('.book-result-card');

        // Preencher dados
        card.querySelector('.book-cover-img').src = book.cover || CONFIG.DEFAULT_COVER;
        card.querySelector('.book-title').textContent = book.title;
        card.querySelector('.book-author span').textContent = book.author;
        card.querySelector('.book-category span').textContent = book.category;
        card.querySelector('.book-publisher span').textContent = book.publisher || 'N/A';

        // Configurar botão
        const btnAdd = card.querySelector('.btn-add-to-shelf');
        btnAdd.dataset.bookId = book.id;

        // Event listeners
        setupAddToShelfButton(btnAdd);

        return card;
    }

    // ============================================
    // RENDERIZAÇÃO - GOOGLE BOOKS
    // ============================================

    function renderGoogleResults(books) {
        elements.googleResults.innerHTML = '';

        if (books.length === 0) {
            elements.googleNoResults.style.display = 'block';
            return;
        }

        elements.googleNoResults.style.display = 'none';

        books.forEach(book => {
            const card = createGoogleBookCard(book);
            elements.googleResults.appendChild(card);
        });
    }

    function createGoogleBookCard(book) {
        const template = elements.googleCardTemplate.content.cloneNode(true);
        const card = template.querySelector('.book-result-card');

        // Preencher dados
        card.querySelector('.book-cover-img').src = book.thumbnail || CONFIG.DEFAULT_COVER;
        card.querySelector('.book-title').textContent = book.title;
        card.querySelector('.book-author span').textContent = book.authors ? book.authors.join(', ') : 'Autor desconhecido';
        card.querySelector('.book-publisher span').textContent = book.publisher || 'Editora desconhecida';
        card.querySelector('.book-description').textContent = book.description ?
            book.description.substring(0, 150) + '...' : 'Sem descrição disponível';

        // Verificar se já existe no catálogo
        const btnImport = card.querySelector('.btn-import-and-add');
        const btnAddExisting = card.querySelector('.btn-add-existing');
        const badgeAlready = card.querySelector('.already-in-catalog');

        if (book.exists_in_catalog) {
            // Livro JÁ EXISTE: Mostra "Adicionar", esconde "Importar"
            btnImport.style.display = 'none';
            btnAddExisting.style.display = 'inline-block';
            btnAddExisting.dataset.bookId = book.local_book_id;
            badgeAlready.style.display = 'inline-block';

            setupAddToShelfButton(btnAddExisting);
        } else {
            // Livro NÃO EXISTE: Mostra "Importar", esconde "Adicionar"
            btnImport.style.display = 'inline-block';
            btnAddExisting.style.display = 'none'; // <-- A LINHA QUE FALTAVA
            badgeAlready.style.display = 'none';

            btnImport.dataset.googleId = book.google_book_id;
            setupImportAndAddButton(btnImport, book.google_book_id);
        }

        return card;
    }

    // ============================================
    // ADICIONAR À PRATELEIRA
    // ============================================

    function setupAddToShelfButton(button) {
        button.addEventListener('click', function() {
            // LER O ID DIRETAMENTE DO ATRIBUTO DATA DO BOTÃO CLICADO
            const bookId = this.dataset.bookId; // 'this' se refere ao botão

            // Verificação para depuração
            if (!bookId) {
                console.error("ERRO CRÍTICO: bookId não encontrado no data-attribute do botão!");
                showFeedback("Erro interno: ID do livro não encontrado.", "danger");
                return;
            }

            const card = this.closest('.book-result-card');
            const selector = card.querySelector('.shelf-selector');

            // Esconder botão e mostrar dropdown
            this.style.display = 'none';
            selector.style.display = 'block';

            const btnConfirm = selector.querySelector('.btn-confirm-add');
            const btnCancel = selector.querySelector('.btn-cancel-add');
            const selectShelf = selector.querySelector('select');

            // Garante que o evento de clique seja único
            btnConfirm.onclick = async () => {
                await addBookToShelf(bookId, selectShelf.value, card);
            };

            btnCancel.onclick = () => {
                selector.style.display = 'none';
                button.style.display = 'inline-block';
            };
        });
    }

    async function addBookToShelf(bookId, selectedValue, cardElement) {
        // 1. Parsear o valor do select
        let shelfType;
        let customShelfName = '';

        if (selectedValue.startsWith('custom:')) {
            shelfType = 'custom';
            customShelfName = selectedValue.substring(7); // Pega o texto depois de 'custom:'
        } else {
            shelfType = selectedValue;
        }

        // 2. Montar o corpo da requisição
        const requestBody = {
            book_id: bookId,
            shelf_type: shelfType,
            custom_shelf_name: customShelfName // Envia o nome da prateleira personalizada
        };

        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.ADD_TO_SHELF, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();

            if (data.success) {
                // AÇÃO DA PARTE 3 VEM AQUI
                // Disparar um evento para notificar a página principal
                const event = new CustomEvent('libraryUpdated');
                document.dispatchEvent(event);

                // Remover card dos resultados para feedback imediato
                cardElement.style.opacity = '0.5';
                cardElement.style.transition = 'opacity 0.5s';
                setTimeout(() => {
                    cardElement.remove();
                }, 500);

            } else {
                showFeedback(data.message, 'warning');
                // Restaurar botão se falhar
                const selector = cardElement.querySelector('.shelf-selector');
                const button = cardElement.querySelector('.btn-add-to-shelf, .btn-add-existing');
                if (selector) selector.style.display = 'none';
                if (button) button.style.display = 'inline-block';
            }

        } catch (error) {
            console.error('Erro ao adicionar livro:', error);
            showFeedback('Erro de conexão ao adicionar livro. Tente novamente.', 'danger');
        }
    }

    // ============================================
    // IMPORTAR DO GOOGLE BOOKS
    // ============================================

    function setupImportAndAddButton(button, googleBookId) {
        button.addEventListener('click', async function() {
            const card = this.closest('.book-result-card');
            const originalText = this.innerHTML;

            // Loading state
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Importando...';

            try {
                // 1. Importar livro
                const importResponse = await fetch(
                    `${CONFIG.API_ENDPOINTS.IMPORT_GOOGLE}${googleBookId}/`,
                    {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    }
                );

                const importData = await importResponse.json();

                if (!importData.success) {
                    throw new Error(importData.message);
                }

                // 2. Mostrar seletor de prateleira
                const bookId = importData.book_id;

                showFeedback(`"${importData.book_title}" importado! Selecione uma prateleira:`, 'info');

                // Esconder botão import e mostrar seletor
                this.style.display = 'none';
                const selector = card.querySelector('.shelf-selector');
                selector.style.display = 'block';

                // Setup botões
                const btnConfirm = selector.querySelector('.btn-confirm-add');
                const btnCancel = selector.querySelector('.btn-cancel-add');
                const selectShelf = selector.querySelector('select');

                btnConfirm.onclick = async () => {
                    await addBookToShelf(bookId, selectShelf.value, card);
                };

                btnCancel.onclick = () => {
                    selector.style.display = 'none';
                    this.style.display = 'inline-block';
                    this.disabled = false;
                    this.innerHTML = originalText;
                };

            } catch (error) {
                console.error('Erro ao importar:', error);
                showFeedback(`Erro: ${error.message}`, 'danger');

                // Restaurar botão
                this.disabled = false;
                this.innerHTML = originalText;
            }
        });
    }

    // ============================================
    // UTILITÁRIOS
    // ============================================

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

    function updateShelfCounts(counts) {
        // Atualizar contadores na sidebar da biblioteca (se existir)
        if (counts) {
            const countElements = {
                'favorites-count': counts.favorites,
                'to-read-count': counts.to_read,
                'reading-count': counts.reading,
                'read-count': counts.read
            };

            Object.entries(countElements).forEach(([id, value]) => {
                const el = document.getElementById(id);
                if (el) el.textContent = value;
            });
        }
    }

    function debounce(func, wait) {
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

    // ============================================
    // INICIALIZAÇÃO
    // ============================================

    function init() {
        initElements();

        // Event: Botão de busca
        elements.btnSearch.addEventListener('click', () => {
            const query = elements.searchInput.value.trim();
            performSearch(query);
        });

        // Event: Enter no input
        elements.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = elements.searchInput.value.trim();
                performSearch(query);
            }
        });

        // Event: Busca automática com debounce (opcional)
        // const debouncedSearch = debounce((query) => performSearch(query), CONFIG.DEBOUNCE_DELAY);
        // elements.searchInput.addEventListener('input', (e) => debouncedSearch(e.target.value));

        // Event: Reset ao abrir modal
        elements.modal.addEventListener('show.bs.modal', () => {
            elements.searchInput.value = '';
            showInitialState();
        });

        console.log('📚 Book Search System initialized!');
    }

    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();