/**
 * GLOBAL SEARCH - Sistema de Busca Global de Livros
 * CGBookStore v3
 *
 * Funcionalidades:
 * - Busca paralela em catálogo local e Google Books
 * - Exibição de resultados em abas separadas
 * - Links para detalhes dos livros
 * - Feedback visual em tempo real
 */

(function() {
    'use strict';

    // ============================================
    // CONFIGURAÇÕES E CONSTANTES
    // ============================================

    const CONFIG = {
        API_ENDPOINTS: {
            SEARCH_LOCAL: '/api/books/search-local/',
            SEARCH_GOOGLE: '/api/books/search-google/'
        }
    };

    // ============================================
    // ELEMENTOS DO DOM
    // ============================================

    let elements = {};

    function initElements() {
        const modal = document.getElementById('globalSearchModal');
        elements = {
            modal: document.getElementById('globalSearchModal'),
            searchInput: document.getElementById('globalSearchInput'),
            btnSearch: document.getElementById('btnGlobalSearch'),

            // Estados
            initialState: document.getElementById('globalInitialState'),
            loadingState: document.getElementById('globalLoadingState'),

            // Abas
            tabsContainer: document.getElementById('globalSearchTabs'),
            localTab: document.getElementById('global-local-tab'),
            googleTab: document.getElementById('global-google-tab'),

            // Contadores
            localCount: document.getElementById('globalLocalCount'),
            googleCount: document.getElementById('globalGoogleCount'),

            // Containers de resultados
            localResults: document.getElementById('globalLocalResultsContainer'),
            googleResults: document.getElementById('globalGoogleResultsContainer'),
            localNoResults: document.getElementById('globalLocalNoResults'),
            googleNoResults: document.getElementById('globalGoogleNoResults'),

            // Feedback
            feedbackMessage: document.getElementById('globalFeedbackMessage'),
            feedbackText: document.getElementById('globalFeedbackText'),

            // Templates
            localCardTemplate: document.getElementById('globalLocalBookCardTemplate'),
            googleCardTemplate: document.getElementById('globalGoogleBookCardTemplate'),
            bookDetailUrlTemplate: modal ? modal.dataset.bookDetailUrl : '',

            // Data from template
            defaultCoverUrl: modal ? modal.dataset.defaultCover : '',
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
            const url = new URL(CONFIG.API_ENDPOINTS.SEARCH_LOCAL, window.location.origin);
            url.searchParams.append('q', query);

            const response = await fetch(url);

            if (!response.ok) {
                throw new Error('Erro na API de busca local');
            }

            const data = await response.json();

            if (data.success) {
                return data.books || [];
            } else {
                console.warn('Busca local falhou:', data.message);
                return [];
            }

        } catch (error) {
            console.error('Erro na busca local:', error);
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

            // Debug
            console.log('=== RESULTADOS DA BUSCA ===');
            console.log('Livros locais:', localBooks.length, localBooks);
            console.log('Livros Google:', googleBooks.length, googleBooks);

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
        card.querySelector('.book-cover-img').src = book.cover || elements.defaultCoverUrl;
        card.querySelector('.book-title').textContent = book.title;
        card.querySelector('.book-author span').textContent = book.author;
        card.querySelector('.book-category span').textContent = book.category;
        card.querySelector('.book-publisher span').textContent = book.publisher || 'N/A';

        // Configurar link de detalhes (USAR SLUG, NÃO ID)
        const btnViewDetails = card.querySelector('.btn-view-details');
        btnViewDetails.href = elements.bookDetailUrlTemplate.replace('BOOK_SLUG_PLACEHOLDER', book.slug);

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
        card.querySelector('.book-cover-img').src = book.thumbnail || elements.defaultCoverUrl;
        card.querySelector('.book-title').textContent = book.title;
        card.querySelector('.book-author span').textContent = book.authors ? book.authors.join(', ') : 'Autor desconhecido';
        card.querySelector('.book-publisher span').textContent = book.publisher || 'Editora desconhecida';
        card.querySelector('.book-description').textContent = book.description ?
            book.description.substring(0, 150) + '...' : 'Sem descrição disponível';

        // Verificar se já existe no catálogo
        const btnViewDetails = card.querySelector('.btn-view-details');
        const badgeAlready = card.querySelector('.already-in-catalog');

        if (book.exists_in_catalog) {
            // Livro JÁ EXISTE: Mostrar link para página de detalhes (USAR SLUG, NÃO ID)
            btnViewDetails.innerHTML = '<i class="fas fa-eye"></i> Ver Detalhes';
            btnViewDetails.href = elements.bookDetailUrlTemplate.replace('BOOK_SLUG_PLACEHOLDER', book.local_book_slug);
            badgeAlready.style.display = 'inline-block';
        } else {
            // Livro NÃO EXISTE: Mostrar link para o Google Books
            btnViewDetails.classList.remove('btn-primary');
            btnViewDetails.classList.add('btn-info');
            btnViewDetails.innerHTML = '<i class="fab fa-google"></i> Ver no Google';
            btnViewDetails.href = book.info_link || '#';
            btnViewDetails.target = '_blank'; // Garante que abrirá em nova aba
            btnViewDetails.rel = 'noopener noreferrer';
            badgeAlready.style.display = 'none';
        }

        return card;
    }

    // ============================================
    // INICIALIZAÇÃO
    // ============================================

    function init() {
        initElements();

        if (!elements.modal) {
            console.warn('Global Search Modal not found on this page');
            return;
        }

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

        // Event: Reset ao abrir modal
        elements.modal.addEventListener('show.bs.modal', () => {
            elements.searchInput.value = '';
            showInitialState();
        });

        console.log('🔍 Global Search System initialized!');
    }

    // Inicializar quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
