/**
 * BACKGROUND MANAGER - Sistema de Background Personalizado PREMIUM
 * CGBookStore v3
 *
 * Funcionalidades:
 * - Upload de imagem de background
 * - Preview em tempo real
 * - Ajuste de estilo (cover, contain, repeat)
 * - Controle de opacidade do overlay
 * - Remoção de background
 */

(function() {
    'use strict';

    // ============================================
    // CONFIGURAÇÕES
    // ============================================

    const CONFIG = {
        MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
        ALLOWED_TYPES: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
        API_ENDPOINTS: {
            UPLOAD: '/accounts/profile/upload-background/',
            UPDATE_SETTINGS: '/accounts/profile/update-background-settings/',
            REMOVE: '/accounts/profile/remove-background/'
        }
    };
    // ============================================
    // ELEMENTOS DO DOM
    // ============================================

    let elements = {};

    function initElements() {
        elements = {
            modal: document.getElementById('backgroundModal'),
            uploadInput: document.getElementById('backgroundUploadInput'),
            uploadBtn: document.getElementById('btnUploadBackground'),
            previewContainer: document.getElementById('backgroundPreview'),
            previewImage: document.getElementById('backgroundPreviewImage'),

            // Controles
            styleSelect: document.getElementById('backgroundStyle'),
            opacitySlider: document.getElementById('backgroundOpacity'),
            opacityValue: document.getElementById('opacityValue'),

            // Botões de ação
            btnSave: document.getElementById('btnSaveBackground'),
            btnRemove: document.getElementById('btnRemoveBackground'),
            btnCancel: document.getElementById('btnCancelBackground'),

            // Feedback
            feedbackMessage: document.getElementById('backgroundFeedbackMessage'),
            feedbackText: document.getElementById('backgroundFeedbackText'),

            // Container da biblioteca (para aplicar background)
            libraryContainer: document.querySelector('.library-container')
        };
    }

    // ============================================
    // INICIALIZAÇÃO
    // ============================================

    document.addEventListener('DOMContentLoaded', function() {
        initElements();

        if (!elements.modal) return; // Sair se modal não existir

        setupEventListeners();
        loadCurrentSettings();
    });

    // ============================================
    // EVENT LISTENERS
    // ============================================

    function setupEventListeners() {
        // ✅ CORREÇÃO: Atualizar o estado do botão sempre que o modal for aberto
        if (elements.modal) {
            elements.modal.addEventListener('show.bs.modal', function() {
                loadCurrentSettings();
            });
        }

        // Upload de arquivo
        if (elements.uploadBtn) {
            elements.uploadBtn.addEventListener('click', () => elements.uploadInput.click());
        }

        if (elements.uploadInput) {
            elements.uploadInput.addEventListener('change', handleFileSelect);
        }

        // Controles de estilo
        if (elements.styleSelect) {
            elements.styleSelect.addEventListener('change', updatePreview);
        }

        if (elements.opacitySlider) {
            elements.opacitySlider.addEventListener('input', function() {
                elements.opacityValue.textContent = this.value + '%';
                updatePreview();
            });
        }

        // Botões de ação
        if (elements.btnSave) {
            elements.btnSave.addEventListener('click', saveBackgroundSettings);
        }

        if (elements.btnRemove) {
            elements.btnRemove.addEventListener('click', removeBackground);
        }

        if (elements.btnCancel) {
            elements.btnCancel.addEventListener('click', closeModal);
        }
    }

    // ============================================
    // CARREGAR CONFIGURAÇÕES ATUAIS
    // ============================================

    function loadCurrentSettings() {
        const container = elements.libraryContainer;
        if (!container) return;

        const currentBg = container.dataset.customBackground;
        const currentStyle = container.dataset.backgroundStyle || 'cover';
        const currentOpacity = container.dataset.backgroundOpacity || '20';

        // ✅ LÓGICA CORRIGIDA PARA O BOTÃO REMOVER
        if (elements.btnRemove) {
            elements.btnRemove.style.display = 'inline-block'; // Sempre visível

            if (currentBg && currentBg !== 'None' && currentBg !== '') {
                // Se existe background, o botão está HABILITADO
                elements.btnRemove.disabled = false;
                elements.btnRemove.classList.remove('disabled');
                elements.btnRemove.title = 'Remover background atual';
            } else {
                // Se NÃO existe background, o botão está DESABILITADO
                elements.btnRemove.disabled = true;
                elements.btnRemove.classList.add('disabled');
                elements.btnRemove.title = 'Nenhum background para remover';
            }
        }

        // Atualizar controles
        if (elements.styleSelect) {
            elements.styleSelect.value = currentStyle;
        }

        if (elements.opacitySlider) {
            elements.opacitySlider.value = currentOpacity;
            elements.opacityValue.textContent = currentOpacity + '%';
        }

        // Se houver um background, mostre o preview com a imagem atual
        if (currentBg && currentBg !== 'None' && currentBg !== '') {
            elements.previewImage.src = currentBg;
            elements.previewContainer.style.display = 'block';
        } else {
            elements.previewImage.src = '';
            elements.previewContainer.style.display = 'none';
        }
    }

    // ============================================
    // SELEÇÃO E VALIDAÇÃO DE ARQUIVO
    // ============================================

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!CONFIG.ALLOWED_TYPES.includes(file.type)) {
            showFeedback('Tipo de arquivo não permitido. Use JPG, PNG ou WebP.', 'danger');
            return;
        }

        if (file.size > CONFIG.MAX_FILE_SIZE) {
            showFeedback('Arquivo muito grande. Tamanho máximo: 10MB.', 'danger');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            elements.previewImage.src = e.target.result;
            elements.previewContainer.style.display = 'block';
            updatePreview();
        };
        reader.readAsDataURL(file);

        uploadBackground(file);
    }

    // ============================================
    // UPLOAD DE BACKGROUND
    // ============================================

    async function uploadBackground(file) {
        const formData = new FormData();
        formData.append('background', file);

        elements.btnSave.disabled = true;
        elements.btnSave.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';

        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.UPLOAD, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showFeedback(data.message, 'success');
                elements.previewImage.src = data.background_url;

                // ✅ Habilitar botão de remover após novo upload
                if (elements.btnRemove) {
                    elements.btnRemove.disabled = false;
                    elements.btnRemove.classList.remove('disabled');
                    elements.btnRemove.title = 'Remover background atual';
                }

                applyBackgroundToPage(data.background_url);
            } else {
                showFeedback(data.error, 'danger');
                if (data.requires_premium) {
                    showPremiumRequired();
                }
            }
        } catch (error) {
            showFeedback('Erro ao enviar imagem. Tente novamente.', 'danger');
            console.error('Upload error:', error);
        } finally {
            elements.btnSave.disabled = false;
            elements.btnSave.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Configurações';
        }
    }

    // ============================================
    // ATUALIZAR PREVIEW
    // ============================================

    function updatePreview() {
        const style = elements.styleSelect.value;
        const opacity = elements.opacitySlider.value;

        elements.previewImage.style.objectFit = style === 'repeat' ? 'none' : style;
        elements.previewImage.style.backgroundRepeat = style === 'repeat' ? 'repeat' : 'no-repeat';

        const overlay = elements.previewContainer.querySelector('.preview-overlay');
        if (overlay) {
            overlay.style.background = `rgba(0,0,0, ${opacity / 100})`;
        }
    }

    // ============================================
    // SALVAR CONFIGURAÇÕES
    // ============================================

    async function saveBackgroundSettings() {
        const style = elements.styleSelect.value;
        const opacity = elements.opacitySlider.value;

        elements.btnSave.disabled = true;
        elements.btnSave.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Salvando...';

        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.UPDATE_SETTINGS, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    background_style: style,
                    background_opacity: opacity
                })
            });

            const data = await response.json();

            if (data.success) {
                showFeedback(data.message, 'success');
                applySettingsToPage(style, opacity);
                setTimeout(() => {
                    closeModal();
                    window.location.reload();
                }, 1500);
            } else {
                showFeedback(data.error, 'danger');
            }
        } catch (error) {
            showFeedback('Erro ao salvar configurações. Tente novamente.', 'danger');
            console.error('Save error:', error);
        } finally {
            elements.btnSave.disabled = false;
            elements.btnSave.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Configurações';
        }
    }

    // ============================================
    // REMOVER BACKGROUND
    // ============================================

    async function removeBackground() {
        if (!confirm('Tem certeza que deseja remover o background personalizado?')) {
            return;
        }

        elements.btnRemove.disabled = true;
        elements.btnRemove.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Removendo...';

        try {
            const response = await fetch(CONFIG.API_ENDPOINTS.REMOVE, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.success) {
                showFeedback(data.message, 'success');

                // ✅ Limpar preview e desabilitar o botão
                elements.previewImage.src = '';
                elements.previewContainer.style.display = 'none';
                elements.btnRemove.disabled = true;
                elements.btnRemove.classList.add('disabled');
                elements.btnRemove.title = 'Nenhum background para remover';

                removeBackgroundFromPage();

                setTimeout(() => {
                    closeModal();
                    window.location.reload();
                }, 1500);
            } else {
                showFeedback(data.error, 'danger');
            }
        } catch (error) {
            showFeedback('Erro ao remover background. Tente novamente.', 'danger');
            console.error('Remove error:', error);
        } finally {
            elements.btnRemove.disabled = false;
            elements.btnRemove.innerHTML = '<i class="fas fa-trash me-2"></i>Remover Background';
        }
    }

    // ... (resto do arquivo permanece igual)

    // ============================================
    // APLICAR BACKGROUND NA PÁGINA
    // ============================================

    function applyBackgroundToPage(url) {
        if (!elements.libraryContainer) return;

        elements.libraryContainer.style.backgroundImage = `url('${url}')`;
        elements.libraryContainer.dataset.customBackground = url;
    }

    function applySettingsToPage(style, opacity) {
        if (!elements.libraryContainer) return;

        elements.libraryContainer.style.backgroundSize = style;
        elements.libraryContainer.style.backgroundRepeat = style === 'repeat' ? 'repeat' : 'no-repeat';

        const overlay = document.querySelector('.library-bg-overlay');
        if (overlay) {
            overlay.style.background = `rgba(0, 0, 0, ${opacity / 100})`;
        }
    }

    function removeBackgroundFromPage() {
        if (!elements.libraryContainer) return;

        elements.libraryContainer.style.backgroundImage = 'none';
        delete elements.libraryContainer.dataset.customBackground;
    }

    // ============================================
    // MODAL
    // ============================================

    function closeModal() {
        const modalInstance = bootstrap.Modal.getInstance(elements.modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    }

    // ============================================
    // FEEDBACK
    // ============================================

    function showFeedback(message, type) {
        elements.feedbackMessage.className = `alert alert-${type} alert-dismissible fade show`;
        elements.feedbackText.textContent = message;
        elements.feedbackMessage.style.display = 'block';

        setTimeout(() => {
            elements.feedbackMessage.style.display = 'none';
        }, 5000);
    }

    function showPremiumRequired() {
        const premiumMsg = `
            <div class="alert alert-warning" role="alert">
                <h5><i class="fas fa-crown me-2"></i>Recurso Premium</h5>
                <p>Backgrounds personalizados são exclusivos para membros Premium.</p>
                <a href="#" class="btn btn-warning btn-sm">
                    <i class="fas fa-star me-2"></i>Assinar Premium
                </a>
            </div>
        `;

        elements.previewContainer.innerHTML = premiumMsg;
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

})();