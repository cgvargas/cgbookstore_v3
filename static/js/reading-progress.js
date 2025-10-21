/**
 * Reading Progress Manager - CGBookStore v3
 *
 * Gerencia a atualização de progresso de leitura, prazos e
 * interações na página de detalhes do livro.
 */
const ReadingProgressManager = (function() {
    'use strict';

    // Função auxiliar para obter o CSRF token
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

    // Função para mostrar notificações (usa o Toast do LibraryManager, se disponível)
    function showToast(message, type = 'info') {
        if (window.LibraryManager && typeof window.LibraryManager.showToast === 'function') {
            window.LibraryManager.showToast(message, type);
        } else {
            // Fallback simples se o LibraryManager não estiver disponível
            console.log(`[Toast][${type}]: ${message}`);
            alert(message);
        }
    }

    /**
     * Salva o progresso de leitura atual.
     */
    async function updateProgress() {
        const container = document.getElementById('readingProgressWidget');
        if (!container) return; // Se o widget não está na página, não faz nada

        const bookId = container.dataset.bookId;
        const currentPageInput = document.getElementById('currentPage');
        const totalPages = parseInt(document.getElementById('totalPages').textContent, 10);
        const updateBtn = document.getElementById('updateProgressBtn');

        const currentPage = parseInt(currentPageInput.value, 10);

        // Validação
        if (isNaN(currentPage) || currentPage < 0) {
            showToast('Por favor, insira um número de página válido.', 'error');
            return;
        }
        if (currentPage > totalPages) {
            showToast(`A página atual não pode ser maior que o total (${totalPages}).`, 'warning');
            currentPageInput.value = totalPages; // Corrige o valor para o máximo
            return;
        }

        // Estado de loading do botão
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Salvando...';

        try {
            const response = await fetch('/api/reading/update-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ book_id: bookId, current_page: currentPage })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
                // Atualizar a UI com os novos dados retornados pela API
                const newPercentage = data.progress.percentage;
                document.getElementById('progress-bar-inner').style.width = newPercentage + '%';
                document.getElementById('progress-bar-inner').setAttribute('aria-valuenow', newPercentage);
                document.getElementById('progress-percentage').textContent = newPercentage + '%';
            } else {
                showToast(data.message || 'Erro ao salvar o progresso.', 'error');
            }

        } catch (error) {
            console.error('Erro de rede ao salvar progresso:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        } finally {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="fas fa-save me-2"></i>Salvar Progresso';
        }
    }

    /**
     * Mostra o modal para definir o prazo de leitura.
     */
    async function showDeadlineModal() {
        const container = document.getElementById('readingProgressWidget');
        if (!container) return;

        const bookId = container.dataset.bookId;
        const currentDeadline = container.dataset.deadline || new Date().toISOString().split('T')[0];

        // Usa SweetAlert2, que é uma dependência esperada no projeto
        if (typeof Swal === 'undefined') {
            showToast('Componente de modal (SweetAlert2) não carregado.', 'error');
            return;
        }

        const { value: newDeadline } = await Swal.fire({
            title: 'Definir Prazo de Leitura',
            html: `<p class="mb-2">Escolha uma data para terminar este livro.</p>
                   <input type="date" id="deadline-input" class="swal2-input" value="${currentDeadline}">`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: '<i class="fas fa-check me-2"></i>Definir Prazo',
            cancelButtonText: 'Cancelar',
            preConfirm: () => {
                const dateValue = document.getElementById('deadline-input').value;
                if (!dateValue) {
                    Swal.showValidationMessage('Por favor, selecione uma data.');
                    return false;
                }
                if (new Date(dateValue) < new Date().setHours(0,0,0,0)) {
                    Swal.showValidationMessage('O prazo não pode ser uma data passada.');
                    return false;
                }
                return dateValue;
            }
        });

        if (newDeadline) {
            setDeadline(bookId, newDeadline);
        }
    }

    /**
     * Envia o novo prazo para a API.
     */
    async function setDeadline(bookId, deadline) {
        try {
            const response = await fetch('/api/reading/set-deadline/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ book_id: bookId, deadline: deadline })
            });

            const data = await response.json();

            if (data.success) {
                showToast(data.message, 'success');
                // Atualizar a UI
                const deadlineDisplay = document.getElementById('deadline-display');
                const deadlineBtn = document.getElementById('setDeadlineBtn');
                const formattedDate = new Date(deadline + 'T00:00:00').toLocaleDateString('pt-BR');

                if (deadlineDisplay) {
                    deadlineDisplay.innerHTML = `<strong>Prazo:</strong> ${formattedDate}`;
                }
                if(deadlineBtn) {
                    deadlineBtn.innerHTML = '<i class="fas fa-calendar-alt me-2"></i>Alterar Prazo';
                }
                // Atualizar o data-attribute para a próxima vez que o modal for aberto
                document.getElementById('readingProgressWidget').dataset.deadline = deadline;

            } else {
                showToast(data.message || 'Erro ao definir o prazo.', 'error');
            }
        } catch (error) {
            console.error('Erro de rede ao definir prazo:', error);
            showToast('Erro de conexão. Tente novamente.', 'error');
        }
    }

    /**
     * Inicializa os event listeners do widget.
     */
    function init() {
        const widget = document.getElementById('readingProgressWidget');
        // Só inicializa se o widget estiver presente na página
        if (!widget) {
            return;
        }

        console.log('📚 Reading Progress Manager inicializado para a página de detalhes.');

        const updateBtn = document.getElementById('updateProgressBtn');
        const deadlineBtn = document.getElementById('setDeadlineBtn');
        const currentPageInput = document.getElementById('currentPage');

        if (updateBtn) {
            updateBtn.addEventListener('click', updateProgress);
        }

        if (deadlineBtn) {
            deadlineBtn.addEventListener('click', showDeadlineModal);
        }

        // Permite salvar pressionando Enter no campo da página
        if (currentPageInput) {
            currentPageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault(); // Impede o envio de formulário
                    updateBtn.click(); // Simula o clique no botão de salvar
                }
            });
        }
    }

    return { init: init };
})();

// Auto-inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', ReadingProgressManager.init);