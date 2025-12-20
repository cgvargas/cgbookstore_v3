/**
 * PROFILE MANAGER - Gerenciamento de uploads e edições de perfil
 * Biblioteca Pessoal 2.0
 */

class ProfileManager {
    constructor() {
        this.maxAvatarSize = 5 * 1024 * 1024; // 5MB
        this.maxBannerSize = 5 * 1024 * 1024; // 5MB
        this.initEventListeners();
    }

    initEventListeners() {
        // Upload de Avatar
        const avatarForm = document.getElementById('avatarUploadForm');
        if (avatarForm) {
            avatarForm.addEventListener('submit', (e) => this.handleAvatarUpload(e));
        }

        // Upload de Banner
        const bannerForm = document.getElementById('bannerUploadForm');
        if (bannerForm) {
            bannerForm.addEventListener('submit', (e) => this.handleBannerUpload(e));
        }

        // Click no avatar para trocar
        const avatarFrame = document.querySelector('.avatar-frame');
        if (avatarFrame) {
            avatarFrame.style.cursor = 'pointer';
            avatarFrame.addEventListener('click', () => this.openAvatarUpload());
        }
    }

    /**
     * Valida o tamanho e tipo do arquivo
     */
    validateFile(file, maxSize, fileType = 'image') {
        // Verificar se é imagem
        if (!file.type.startsWith(fileType + '/')) {
            this.showToast('Erro: O arquivo deve ser uma imagem', 'error');
            return false;
        }

        // Verificar tamanho
        if (file.size > maxSize) {
            const maxSizeMB = maxSize / (1024 * 1024);
            this.showToast(`Erro: O arquivo deve ter no máximo ${maxSizeMB}MB`, 'error');
            return false;
        }

        return true;
    }

    /**
     * Upload de Avatar via AJAX
     */
    async handleAvatarUpload(event) {
        event.preventDefault();

        const form = event.target;
        const fileInput = form.querySelector('#avatarFile');
        const file = fileInput.files[0];

        // Validar arquivo
        if (!this.validateFile(file, this.maxAvatarSize)) {
            return;
        }

        // Criar FormData
        const formData = new FormData();
        formData.append('avatar', file);
        formData.append('csrfmiddlewaretoken', form.querySelector('[name="csrfmiddlewaretoken"]').value);

        // Mostrar loading
        this.setLoadingState(form, true);

        try {
            const response = await fetch('/profile/upload-avatar/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Avatar atualizado com sucesso!', 'success');

                // Atualizar imagem na página
                const avatarImg = document.querySelector('.avatar-frame img');
                if (avatarImg) {
                    avatarImg.src = data.avatar_url + '?t=' + Date.now(); // Cache bust
                }

                // Fechar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('avatarUploadModal'));
                modal.hide();

                // Limpar form
                form.reset();
                document.getElementById('avatarPreview').style.display = 'none';
            } else {
                this.showToast('Erro: ' + (data.error || 'Não foi possível fazer upload'), 'error');
            }
        } catch (error) {
            console.error('Erro no upload:', error);
            this.showToast('Erro ao fazer upload. Tente novamente.', 'error');
        } finally {
            this.setLoadingState(form, false);
            // Esconder o loader global (pode ter sido ativado pelo submit do form)
            if (window.PageLoader) window.PageLoader.hide();
        }
    }

    /**
     * Upload de Banner via AJAX
     */
    async handleBannerUpload(event) {
        event.preventDefault();

        const form = event.target;
        const fileInput = form.querySelector('#bannerFile');
        const file = fileInput.files[0];

        // Validar arquivo
        if (!this.validateFile(file, this.maxBannerSize)) {
            return;
        }

        // Criar FormData
        const formData = new FormData();
        formData.append('banner', file);
        formData.append('csrfmiddlewaretoken', form.querySelector('[name="csrfmiddlewaretoken"]').value);

        // Mostrar loading
        this.setLoadingState(form, true);

        try {
            const response = await fetch('/profile/upload-banner/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Banner atualizado com sucesso!', 'success');

                // Atualizar imagem na página
                const bannerImg = document.querySelector('.profile-banner');
                if (bannerImg) {
                    if (bannerImg.tagName === 'IMG') {
                        bannerImg.src = data.banner_url + '?t=' + Date.now(); // Cache bust
                    } else {
                        // Substituir div por img
                        const newImg = document.createElement('img');
                        newImg.src = data.banner_url;
                        newImg.alt = 'Banner';
                        newImg.className = 'profile-banner';
                        bannerImg.parentNode.replaceChild(newImg, bannerImg);
                    }
                }

                // Fechar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('bannerUploadModal'));
                modal.hide();

                // Limpar form
                form.reset();
                document.getElementById('bannerPreview').style.display = 'none';
            } else {
                this.showToast('Erro: ' + (data.error || 'Não foi possível fazer upload'), 'error');
            }
        } catch (error) {
            console.error('Erro no upload:', error);
            this.showToast('Erro ao fazer upload. Tente novamente.', 'error');
        } finally {
            this.setLoadingState(form, false);
            // Esconder o loader global (pode ter sido ativado pelo submit do form)
            if (window.PageLoader) window.PageLoader.hide();
        }
    }

    /**
     * Atualiza tema visual via AJAX
     */
    async updateTheme(themeName) {
        try {
            const response = await fetch('/profile/update-theme/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ theme: themeName })
            });

            const data = await response.json();

            if (data.success) {
                // Atualizar classe do avatar
                const avatarFrame = document.querySelector('.avatar-frame');
                if (avatarFrame) {
                    // Remover todas as classes de tema
                    avatarFrame.className = avatarFrame.className.split(' ').filter(c => !c.startsWith('theme-')).join(' ');
                    // Adicionar novo tema
                    avatarFrame.classList.add(themeName);
                }

                this.showToast('Tema atualizado!', 'success');
            }
        } catch (error) {
            console.error('Erro ao atualizar tema:', error);
            this.showToast('Erro ao atualizar tema', 'error');
        }
    }

    /**
     * Abre modal de upload de avatar
     */
    openAvatarUpload() {
        const modal = new bootstrap.Modal(document.getElementById('avatarUploadModal'));
        modal.show();
    }

    /**
     * Define estado de loading no formulário
     */
    setLoadingState(form, isLoading) {
        const submitBtn = form.querySelector('button[type="submit"]');

        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando...';
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-upload"></i> Fazer Upload';
        }
    }

    /**
     * Toast de notificação
     */
    showToast(message, type = 'info') {
        // Reutiliza o sistema de toast do LibraryManager
        if (window.libraryManager && window.libraryManager.showToast) {
            window.libraryManager.showToast(message, type);
        } else {
            // Fallback
            alert(message);
        }
    }

    /**
     * Pega cookie CSRF
     */
    getCookie(name) {
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
     * Comprime imagem antes do upload (opcional - para otimização futura)
     */
    async compressImage(file, maxWidth = 1200, quality = 0.9) {
        return new Promise((resolve) => {
            const reader = new FileReader();

            reader.onload = (e) => {
                const img = new Image();

                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    let width = img.width;
                    let height = img.height;

                    // Redimensionar mantendo proporção
                    if (width > maxWidth) {
                        height = (height * maxWidth) / width;
                        width = maxWidth;
                    }

                    canvas.width = width;
                    canvas.height = height;

                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);

                    canvas.toBlob((blob) => {
                        resolve(new File([blob], file.name, {
                            type: 'image/jpeg',
                            lastModified: Date.now()
                        }));
                    }, 'image/jpeg', quality);
                };

                img.src = e.target.result;
            };

            reader.readAsDataURL(file);
        });
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
});