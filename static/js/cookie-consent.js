/**
 * Cookie Consent Manager - LGPD Compliance
 * CG BookStore
 * 
 * Gerencia o consentimento de cookies do usuário de acordo com a LGPD.
 * Cookies essenciais (sessionid, csrftoken) são sempre permitidos.
 */

(function () {
    'use strict';

    const CONSENT_COOKIE_NAME = 'cgbookstore_cookie_consent';
    const CONSENT_EXPIRY_DAYS = 365;

    // Tipos de cookies
    const COOKIE_TYPES = {
        essential: {
            name: 'Essenciais',
            description: 'Necessários para o funcionamento do site (login, segurança)',
            required: true,
            cookies: ['sessionid', 'csrftoken']
        },
        preferences: {
            name: 'Preferências',
            description: 'Lembram suas escolhas como tema claro/escuro',
            required: false,
            cookies: ['theme']
        },
        analytics: {
            name: 'Analíticos',
            description: 'Ajudam-nos a entender como você usa o site',
            required: false,
            cookies: []
        }
    };

    /**
     * Obtém o consentimento salvo
     */
    function getConsent() {
        const consent = getCookie(CONSENT_COOKIE_NAME);
        if (consent) {
            try {
                return JSON.parse(consent);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    /**
     * Salva o consentimento
     */
    function saveConsent(preferences) {
        const consent = {
            timestamp: new Date().toISOString(),
            preferences: preferences
        };
        setCookie(CONSENT_COOKIE_NAME, JSON.stringify(consent), CONSENT_EXPIRY_DAYS);
        hideBanner();
        applyConsent(preferences);
    }

    /**
     * Aplica as preferências de consentimento
     */
    function applyConsent(preferences) {
        // Se analytics não foi aceito, remover cookies de analytics (se existirem)
        if (!preferences.analytics) {
            // Aqui você removeria cookies de analytics como Google Analytics
            // Por enquanto, o sistema não usa analytics externos
        }

        // Se preferences não foi aceito, remover cookie de tema
        if (!preferences.preferences) {
            deleteCookie('theme');
        }
    }

    /**
     * Aceita todos os cookies
     */
    function acceptAll() {
        saveConsent({
            essential: true,
            preferences: true,
            analytics: true
        });
    }

    /**
     * Aceita apenas cookies essenciais
     */
    function acceptEssential() {
        saveConsent({
            essential: true,
            preferences: false,
            analytics: false
        });
    }

    /**
     * Salva preferências personalizadas
     */
    function saveCustomPreferences() {
        const preferencesCheckbox = document.getElementById('cookie-pref-preferences');
        const analyticsCheckbox = document.getElementById('cookie-pref-analytics');

        saveConsent({
            essential: true,
            preferences: preferencesCheckbox ? preferencesCheckbox.checked : false,
            analytics: analyticsCheckbox ? analyticsCheckbox.checked : false
        });

        hideSettingsModal();
    }

    /**
     * Mostra o banner de cookies
     */
    function showBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.add('show');
            document.body.style.paddingBottom = banner.offsetHeight + 'px';
        }
    }

    /**
     * Esconde o banner de cookies
     */
    function hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.remove('show');
            document.body.style.paddingBottom = '0';
        }
    }

    /**
     * Mostra o modal de configurações
     */
    function showSettingsModal() {
        const modal = document.getElementById('cookie-settings-modal');
        if (modal) {
            modal.classList.add('show');

            // Preencher checkboxes com preferências atuais
            const consent = getConsent();
            if (consent && consent.preferences) {
                const prefCheckbox = document.getElementById('cookie-pref-preferences');
                const analyticsCheckbox = document.getElementById('cookie-pref-analytics');

                if (prefCheckbox) prefCheckbox.checked = consent.preferences.preferences;
                if (analyticsCheckbox) analyticsCheckbox.checked = consent.preferences.analytics;
            }
        }
    }

    /**
     * Esconde o modal de configurações
     */
    function hideSettingsModal() {
        const modal = document.getElementById('cookie-settings-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }

    // Funções auxiliares de cookies
    function setCookie(name, value, days) {
        const expires = new Date();
        expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
        document.cookie = name + '=' + encodeURIComponent(value) +
            ';expires=' + expires.toUTCString() +
            ';path=/;SameSite=Lax';
    }

    function getCookie(name) {
        const nameEQ = name + '=';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.indexOf(nameEQ) === 0) {
                return decodeURIComponent(cookie.substring(nameEQ.length));
            }
        }
        return null;
    }

    function deleteCookie(name) {
        document.cookie = name + '=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';
    }

    /**
     * Inicializa o sistema de cookies
     */
    function init() {
        const consent = getConsent();

        // Se não há consentimento, mostrar banner
        if (!consent) {
            // Aguardar DOM estar pronto
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', showBanner);
            } else {
                // Pequeno delay para garantir que o banner foi renderizado
                setTimeout(showBanner, 500);
            }
        }

        // Expor funções globalmente para os botões
        window.CookieConsent = {
            acceptAll: acceptAll,
            acceptEssential: acceptEssential,
            showSettings: showSettingsModal,
            hideSettings: hideSettingsModal,
            savePreferences: saveCustomPreferences,
            getConsent: getConsent
        };
    }

    // Inicializar
    init();

})();
