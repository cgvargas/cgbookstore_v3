/**
 * Admin Quiz Tree - JavaScript para visualização em árvore
 * Agrupa perguntas por Quiz com separadores visuais
 */

document.addEventListener('DOMContentLoaded', function () {
    // Só executa na página de QuizQuestions
    if (!window.location.href.includes('quizquestion')) return;

    const resultList = document.querySelector('#result_list tbody');
    if (!resultList) return;

    const rows = resultList.querySelectorAll('tr');
    let lastQuizTitle = null;

    rows.forEach((row, index) => {
        // Encontra o badge do quiz na linha
        const quizBadge = row.querySelector('.quiz-folder-badge');
        if (!quizBadge) return;

        const currentQuizTitle = quizBadge.textContent.trim();

        // Se mudou de quiz, adiciona separador visual
        if (lastQuizTitle !== null && currentQuizTitle !== lastQuizTitle) {
            row.style.borderTop = '3px solid #3498db';
            row.style.marginTop = '10px';
        }

        lastQuizTitle = currentQuizTitle;
    });

    // Adiciona contagem de perguntas no filtro lateral
    const filterList = document.querySelector('#changelist-filter');
    if (filterList) {
        const quizLinks = filterList.querySelectorAll('a');
        quizLinks.forEach(link => {
            // Conta quantas linhas há para cada quiz quando clicado
            link.addEventListener('click', function () {
                console.log('Quiz filter clicked:', this.textContent);
            });
        });
    }

    console.log('Quiz Tree View initialized');
});
