/**
 * ========================================
 * THEME SWITCHER - CGBookStore v3
 * Autor: cgvargas
 * Data: 02/10/2025
 * Versão: 1.0
 * ========================================
 *
 * Sistema de alternância entre temas:
 * - Claro (light)
 * - Escuro (dark)
 * - Sistema (auto - detecta preferência do SO)
 */

(function() {
    'use strict';

    // Chave para salvar preferência no localStorage
    const THEME_STORAGE_KEY = 'cgbookstore-theme-preference';

    // Classe/atributo para aplicar no HTML
    const THEME_ATTRIBUTE = 'data-theme';

    /**
     * Obtém a preferência de tema do sistema operacional
     * @returns {string} 'dark' ou 'light'
     */
    function getSystemThemePreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    /**
     * Obtém o tema salvo no localStorage
     * @returns {string|null} 'light', 'dark', 'auto' ou null
     */
    function getSavedTheme() {
        try {
            return localStorage.getItem(THEME_STORAGE_KEY);
        } catch (e) {
            console.warn('Não foi possível acessar localStorage:', e);
            return null;
        }
    }

    /**
     * Salva o tema no localStorage
     * @param {string} theme - 'light', 'dark' ou 'auto'
     */
    function saveTheme(theme) {
        try {
            localStorage.setItem(THEME_STORAGE_KEY, theme);
        } catch (e) {
            console.warn('Não foi possível salvar no localStorage:', e);
        }
    }

    /**
     * Aplica o tema no documento
     * @param {string} theme - 'light', 'dark' ou 'auto'
     */
    function applyTheme(theme) {
        const root = document.documentElement;

        if (theme === 'auto') {
            // Remove atributo para usar media query CSS
            root.removeAttribute(THEME_ATTRIBUTE);

            // Aplica baseado na preferência do sistema
            const systemTheme = getSystemThemePreference();
            root.setAttribute(THEME_ATTRIBUTE, systemTheme);
        } else {
            // Aplica tema específico (light ou dark)
            root.setAttribute(THEME_ATTRIBUTE, theme);
        }

        // Atualiza ícone ativo no switcher
        updateThemeSwitcherIcon(theme);
    }

    /**
     * Atualiza o ícone ativo no botão do theme switcher
     * @param {string} activeTheme - 'light', 'dark' ou 'auto'
     */
    function updateThemeSwitcherIcon(activeTheme) {
        // Remove classe 'active' de todos os itens
        document.querySelectorAll('.theme-option').forEach(item => {
            item.classList.remove('active');
        });

        // Adiciona 'active' no tema atual
        const activeItem = document.querySelector(`.theme-option[data-theme="${activeTheme}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }

        // Atualiza ícone no botão principal
        const themeSwitcherBtn = document.getElementById('themeSwitcherBtn');
        if (themeSwitcherBtn) {
            let iconClass = 'fa-circle-half-stroke'; // auto (padrão)

            if (activeTheme === 'light') {
                iconClass = 'fa-sun';
            } else if (activeTheme === 'dark') {
                iconClass = 'fa-moon';
            }

            const icon = themeSwitcherBtn.querySelector('i');
            if (icon) {
                icon.className = `fas ${iconClass}`;
            }
        }
    }

    /**
     * Alterna para um tema específico
     * @param {string} theme - 'light', 'dark' ou 'auto'
     */
    function setTheme(theme) {
        // Valida o tema
        if (!['light', 'dark', 'auto'].includes(theme)) {
            console.warn('Tema inválido:', theme);
            theme = 'auto';
        }

        // Aplica e salva
        applyTheme(theme);
        saveTheme(theme);

        // Dispatch evento customizado para outros scripts reagirem
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme }
        }));
    }

    /**
     * Inicializa o theme switcher
     */
    function initThemeSwitcher() {
        // 1. Determinar tema inicial
        let initialTheme = getSavedTheme();

        if (!initialTheme) {
            // Se não há tema salvo, usa 'auto'
            initialTheme = 'auto';
            saveTheme(initialTheme);
        }

        // 2. Aplicar tema inicial
        applyTheme(initialTheme);

        // 3. Adicionar listeners nos botões de tema
        document.querySelectorAll('.theme-option').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const theme = this.getAttribute('data-theme');
                setTheme(theme);
            });
        });

        // 4. Listener para mudanças na preferência do sistema
        if (window.matchMedia) {
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

            // Listener moderno
            if (darkModeQuery.addEventListener) {
                darkModeQuery.addEventListener('change', function(e) {
                    const currentTheme = getSavedTheme();
                    if (currentTheme === 'auto') {
                        // Reaplica tema auto quando sistema muda
                        applyTheme('auto');
                    }
                });
            }
            // Fallback para navegadores antigos
            else if (darkModeQuery.addListener) {
                darkModeQuery.addListener(function(e) {
                    const currentTheme = getSavedTheme();
                    if (currentTheme === 'auto') {
                        applyTheme('auto');
                    }
                });
            }
        }

        console.log('🎨 Theme Switcher inicializado com tema:', initialTheme);
    }

    // Inicializa quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeSwitcher);
    } else {
        initThemeSwitcher();
    }

    // Expõe funções globalmente para uso em outros scripts
    window.CGBookStore = window.CGBookStore || {};
    window.CGBookStore.ThemeSwitcher = {
        setTheme: setTheme,
        getTheme: getSavedTheme,
        getSystemTheme: getSystemThemePreference
    };

})();