// ========================================
// CATALOG FILTERS - UX ENHANCEMENTS
// Sistema de filtros interativos do catálogo
// ========================================

document.addEventListener('DOMContentLoaded', function() {

    // ========== ELEMENTOS DO DOM ==========
    const filterForm = document.getElementById('filterForm');
    const checkboxes = document.querySelectorAll('.filter-checkbox');
    const selectSort = document.querySelector('.filter-select');
    const priceMinInput = document.querySelector('input[name="price_min"]');
    const priceMaxInput = document.querySelector('input[name="price_max"]');
    const searchInput = document.querySelector('input[name="q"]');
    const submitBtn = filterForm.querySelector('button[type="submit"]');
    const clearBtn = document.querySelector('a[href*="book_list"]:not([href*="?"])');

    // ========== AUTO-SUBMIT AO MUDAR FILTROS ==========

    /**
     * Auto-submit quando checkbox é alterado
     */
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            showLoadingState();
            filterForm.submit();
        });
    });

    /**
     * Auto-submit quando ordenação é alterada
     */
    if (selectSort) {
        selectSort.addEventListener('change', function() {
            showLoadingState();
            filterForm.submit();
        });
    }

    /**
     * Submit ao pressionar Enter no campo de busca
     */
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                showLoadingState();
                filterForm.submit();
            }
        });
    }

    // ========== VALIDAÇÃO DE PREÇO ==========

    /**
     * Valida se preço mínimo é menor que preço máximo
     */
    function validatePriceRange() {
        const minValue = parseFloat(priceMinInput.value) || 0;
        const maxValue = parseFloat(priceMaxInput.value) || Infinity;

        if (minValue > maxValue && maxValue !== Infinity) {
            showToast('Preço mínimo não pode ser maior que o máximo', 'warning');
            priceMinInput.classList.add('is-invalid');
            priceMaxInput.classList.add('is-invalid');
            return false;
        } else {
            priceMinInput.classList.remove('is-invalid');
            priceMaxInput.classList.remove('is-invalid');
            return true;
        }
    }

    /**
     * Valida preços ao sair do campo
     */
    if (priceMinInput) {
        priceMinInput.addEventListener('blur', validatePriceRange);
    }

    if (priceMaxInput) {
        priceMaxInput.addEventListener('blur', validatePriceRange);
    }

    /**
     * Impede envio do formulário se preços inválidos
     */
    filterForm.addEventListener('submit', function(e) {
        if (priceMinInput.value || priceMaxInput.value) {
            if (!validatePriceRange()) {
                e.preventDefault();
                return false;
            }
        }
        showLoadingState();
    });

    // ========== LOADING STATE ==========

    /**
     * Mostra estado de carregamento no botão submit
     */
    function showLoadingState() {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.classList.add('loading');
            const originalText = submitBtn.innerHTML;
            submitBtn.setAttribute('data-original-text', originalText);
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
        }

        // Adiciona overlay de loading nos cards
        const booksGrid = document.querySelector('.row.row-cols-1');
        if (booksGrid) {
            booksGrid.style.opacity = '0.5';
            booksGrid.style.pointerEvents = 'none';
        }
    }

    /**
     * Remove estado de carregamento (ao voltar da página)
     */
    function hideLoadingState() {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
            const originalText = submitBtn.getAttribute('data-original-text');
            if (originalText) {
                submitBtn.innerHTML = originalText;
            }
        }

        const booksGrid = document.querySelector('.row.row-cols-1');
        if (booksGrid) {
            booksGrid.style.opacity = '1';
            booksGrid.style.pointerEvents = 'auto';
        }
    }

    // Restaura estado ao voltar pela navegação
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            hideLoadingState();
        }
    });

    // ========== CONTADOR DE FILTROS ATIVOS ==========

    /**
     * Atualiza contador de filtros ativos em tempo real
     */
    function updateActiveFiltersCount() {
        const checkedBoxes = document.querySelectorAll('.filter-checkbox:checked').length;
        const hasSearch = searchInput && searchInput.value.trim() !== '';
        const hasMinPrice = priceMinInput && priceMinInput.value !== '';
        const hasMaxPrice = priceMaxInput && priceMaxInput.value !== '';
        const hasNonDefaultSort = selectSort && selectSort.value !== 'newest';

        let count = checkedBoxes;
        if (hasSearch) count++;
        if (hasMinPrice) count++;
        if (hasMaxPrice) count++;
        if (hasNonDefaultSort) count++;

        // Atualiza badge de contagem (se existir)
        let counterBadge = document.querySelector('.filters-counter');
        if (!counterBadge && count > 0) {
            counterBadge = document.createElement('span');
            counterBadge.className = 'badge bg-danger rounded-pill ms-2 filters-counter';
            const headerTitle = document.querySelector('.filters-sidebar .card-header h5');
            if (headerTitle) {
                headerTitle.appendChild(counterBadge);
            }
        }

        if (counterBadge) {
            if (count > 0) {
                counterBadge.textContent = count;
                counterBadge.style.display = 'inline-block';
            } else {
                counterBadge.style.display = 'none';
            }
        }
    }

    // Atualiza ao carregar a página
    updateActiveFiltersCount();

    // Atualiza ao mudar qualquer filtro
    checkboxes.forEach(cb => cb.addEventListener('change', updateActiveFiltersCount));
    if (selectSort) selectSort.addEventListener('change', updateActiveFiltersCount);
    if (searchInput) searchInput.addEventListener('input', updateActiveFiltersCount);
    if (priceMinInput) priceMinInput.addEventListener('input', updateActiveFiltersCount);
    if (priceMaxInput) priceMaxInput.addEventListener('input', updateActiveFiltersCount);

    // ========== SCROLL SUAVE AO FILTRAR ==========

    /**
     * Scroll suave para o topo do catálogo após aplicar filtros
     */
    function smoothScrollToTop() {
        const catalogHeader = document.querySelector('.container.my-4 h1');
        if (catalogHeader) {
            catalogHeader.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    // Se veio de filtro (tem query params), faz scroll
    if (window.location.search) {
        setTimeout(smoothScrollToTop, 100);
    }

    // ========== LIMPAR FILTROS COM CONFIRMAÇÃO ==========

    /**
     * Confirma limpeza de filtros se houver muitos ativos
     */
    if (clearBtn) {
        clearBtn.addEventListener('click', function(e) {
            const checkedBoxes = document.querySelectorAll('.filter-checkbox:checked').length;

            if (checkedBoxes >= 3) {
                const confirmClear = confirm('Tem certeza que deseja limpar todos os filtros?');
                if (!confirmClear) {
                    e.preventDefault();
                }
            }
        });
    }

    // ========== SISTEMA DE TOAST/NOTIFICAÇÃO ==========

    /**
     * Exibe toast de notificação
     * @param {string} message - Mensagem a exibir
     * @param {string} type - Tipo: success, warning, danger, info
     */
    function showToast(message, type = 'info') {
        // Remove toast anterior se existir
        const existingToast = document.querySelector('.catalog-toast');
        if (existingToast) {
            existingToast.remove();
        }

        // Cria novo toast
        const toast = document.createElement('div');
        toast.className = `catalog-toast alert alert-${type} alert-dismissible fade show`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(toast);

        // Remove automaticamente após 5 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    // ========== DEBOUNCE PARA BUSCA ==========

    /**
     * Debounce - evita submit excessivo ao digitar
     */
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

    /**
     * Auto-submit na busca com debounce (500ms)
     */
    if (searchInput) {
        const debouncedSubmit = debounce(() => {
            if (searchInput.value.trim().length >= 3 || searchInput.value.trim().length === 0) {
                showLoadingState();
                filterForm.submit();
            }
        }, 800);

        searchInput.addEventListener('input', debouncedSubmit);
    }

    // ========== HIGHLIGHT DOS CARDS AO CARREGAR ==========

    /**
     * Adiciona animação de entrada nos cards
     */
    function animateCards() {
        const cards = document.querySelectorAll('.book-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';

                setTimeout(() => {
                    card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 50);
            }, index * 50);
        });
    }

    // Anima cards ao carregar
    animateCards();

    // ========== MOSTRAR/OCULTAR FILTROS NO MOBILE ==========

    /**
     * Fecha collapse de filtros ao aplicar no mobile
     */
    const mobileFiltersCollapse = document.getElementById('mobileFilters');
    if (mobileFilters && window.innerWidth < 768) {
        filterForm.addEventListener('submit', function() {
            const bsCollapse = bootstrap.Collapse.getInstance(mobileFiltersCollapse);
            if (bsCollapse) {
                bsCollapse.hide();
            }
        });
    }

    // ========== INDICADOR VISUAL DE CATEGORIA ATIVA ==========

    /**
     * Adiciona classe especial em labels de categorias selecionadas
     */
    function highlightActiveCategories() {
        checkboxes.forEach(checkbox => {
            const label = checkbox.nextElementSibling;
            if (checkbox.checked) {
                label.style.fontWeight = '600';
                label.style.color = 'var(--bs-primary)';
            } else {
                label.style.fontWeight = '400';
                label.style.color = '';
            }
        });
    }

    highlightActiveCategories();
    checkboxes.forEach(cb => {
        cb.addEventListener('change', highlightActiveCategories);
    });

    // ========== MÁSCARA DE PREÇO (OPCIONAL) ==========

    /**
     * Formata input de preço ao digitar
     */
    function formatPriceInput(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value;

            // Remove caracteres não numéricos exceto ponto
            value = value.replace(/[^\d.]/g, '');

            // Garante apenas um ponto decimal
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }

            e.target.value = value;
        });
    }

    if (priceMinInput) formatPriceInput(priceMinInput);
    if (priceMaxInput) formatPriceInput(priceMaxInput);

    // ========== LOG DE DEBUG (Remover em produção) ==========

    console.log('✅ Catalog Filters JS carregado com sucesso!');
    console.log(`📊 Filtros ativos detectados: ${document.querySelectorAll('.filter-checkbox:checked').length}`);

});