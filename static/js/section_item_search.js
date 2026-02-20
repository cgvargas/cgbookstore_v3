/**
 * Sistema de busca para SectionItem no Django Admin
 * Permite buscar livros e autores por nome ao invés de digitar ID
 */

(function ($) {
    'use strict';

    $(document).ready(function () {
        // Adicionar botão de busca ao lado do campo object_id
        addSearchButtons();
    });

    function addSearchButtons() {
        // Encontrar todos os campos object_id
        $('input[name$="object_id"]').each(function () {
            const $input = $(this);
            const $row = $input.closest('tr, .form-row');

            // Evitar adicionar botão múltiplas vezes
            if ($row.find('.search-object-btn').length > 0) {
                return;
            }

            // Criar botão de busca
            const $searchBtn = $('<button>', {
                type: 'button',
                class: 'search-object-btn',
                html: '🔍 Buscar',
                css: {
                    marginLeft: '10px',
                    padding: '5px 15px',
                    background: '#417690',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '13px'
                }
            });

            // Adicionar hover effect
            $searchBtn.hover(
                function () { $(this).css('background', '#2e5266'); },
                function () { $(this).css('background', '#417690'); }
            );

            // Inserir botão após o input
            $input.after($searchBtn);

            // Adicionar evento de clique
            $searchBtn.on('click', function () {
                openSearchModal($input, $row);
            });
        });
    }

    function openSearchModal($input, $row) {
        // Encontrar o content_type selecionado
        const $contentTypeSelect = $row.find('select[name$="content_type"]');
        const contentTypeId = $contentTypeSelect.val();

        if (!contentTypeId) {
            alert('Por favor, selecione o tipo de conteúdo (Content Type) primeiro.');
            return;
        }

        // Determinar qual modelo foi selecionado
        const contentTypeText = $contentTypeSelect.find('option:selected').text().toLowerCase();
        let searchUrl = '';
        let modelName = '';

        if (contentTypeText.includes('book') || contentTypeText.includes('livro')) {
            searchUrl = '/admin/core/book/';
            modelName = 'Livro';
        } else if (contentTypeText.includes('author') || contentTypeText.includes('autor')) {
            searchUrl = '/admin/core/author/';
            modelName = 'Autor';
        } else if (contentTypeText.includes('video') || contentTypeText.includes('vídeo')) {
            searchUrl = '/admin/core/video/';
            modelName = 'Vídeo';
        } else if (contentTypeText.includes('news') || contentTypeText.includes('notícia') || contentTypeText.includes('article') || contentTypeText.includes('artigo')) {
            searchUrl = '/admin/news/article/';
            modelName = 'Notícia/Artigo';
        } else {
            alert('Tipo de conteúdo não suportado para busca.');
            return;
        }

        // Abrir em nova janela
        const searchWindow = window.open(
            searchUrl,
            'searchWindow',
            'width=1000,height=600,scrollbars=yes,resizable=yes'
        );

        // Mostrar instrução
        showInstruction(modelName);
    }

    function showInstruction(modelName) {
        // Remover instrução anterior se existir
        $('.search-instruction').remove();

        // Criar instrução
        const $instruction = $('<div>', {
            class: 'search-instruction',
            html: `
                <strong>📋 Instruções:</strong><br>
                1. Na janela que abriu, busque o ${modelName} desejado<br>
                2. Clique no ${modelName} para abrir seus detalhes<br>
                3. Copie o <strong>ID</strong> que aparece na URL (ex: /book/<strong>123</strong>/change/)<br>
                4. Cole o ID no campo "Object ID" abaixo<br>
                5. Salve o formulário
            `,
            css: {
                background: '#fff3cd',
                border: '1px solid #ffc107',
                borderRadius: '4px',
                padding: '15px',
                marginTop: '10px',
                fontSize: '13px',
                lineHeight: '1.6'
            }
        });

        // Adicionar instrução no topo do formulário
        $('.module').first().prepend($instruction);

        // Remover após 30 segundos
        setTimeout(function () {
            $instruction.fadeOut(500, function () {
                $(this).remove();
            });
        }, 30000);
    }

})(django.jQuery);