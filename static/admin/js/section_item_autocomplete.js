/**
 * Autocomplete para SectionItem no Django Admin
 * Busca livros, autores e vídeos por nome via AJAX
 * 
 * Usa event delegation para funcionar com elementos dinâmicos (inlines adicionados)
 */
(function ($) {
    'use strict';

    // Armazenar timeouts por input
    var timeouts = {};

    $(document).ready(function () {
        // Usando event delegation no document para capturar todos os inputs,
        // incluindo os adicionados dinamicamente

        // Handler para input - usando delegation
        $(document).on('input', 'input.section-item-autocomplete, input[name$="-search_item"]', function () {
            var $input = $(this);
            var inputId = $input.attr('id') || $input.attr('name');

            // Limpar timeout anterior para este input
            if (timeouts[inputId]) {
                clearTimeout(timeouts[inputId]);
            }

            var query = $input.val();
            var $row = $input.closest('tr, .inline-related, .form-row');
            var $contentTypeSelect = $row.find('select[name$="-content_type"]');
            var $objectIdInput = $row.find('input[name$="-object_id"]');

            // Encontrar ou criar o container de resultados
            var $results = $input.next('.autocomplete-results-container');
            if ($results.length === 0) {
                $results = $('<div class="autocomplete-results-container"></div>').css({
                    position: 'absolute',
                    zIndex: 9999,
                    backgroundColor: '#ffffff',
                    border: '1px solid #417690',
                    borderRadius: '4px',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    display: 'none',
                    width: '300px',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.3)'
                });
                $input.after($results);
            }

            if (query.length < 2) {
                $results.hide();
                return;
            }

            // Obter o content_type selecionado
            var contentType = $contentTypeSelect.find('option:selected').text().toLowerCase();

            // Mapear content_type para tipo
            var type = '';
            if (contentType.includes('livro') || contentType.includes('book')) {
                type = 'book';
            } else if (contentType.includes('autor') || contentType.includes('author')) {
                type = 'author';
            } else if (contentType.includes('vídeo') || contentType.includes('video')) {
                type = 'video';
            }

            if (!type) {
                $results.html('<div style="padding:10px;color:#333;background:#fff5cc;border-left:3px solid #ffc107;">⚠️ Selecione um tipo primeiro</div>').show();
                return;
            }

            // Debounce - aguardar 300ms antes de fazer a requisição
            timeouts[inputId] = setTimeout(function () {
                $.ajax({
                    url: '/admin-tools/section-autocomplete/',
                    data: { q: query, content_type: type },
                    success: function (data) {
                        $results.empty();
                        if (data.results.length === 0) {
                            $results.html('<div style="padding:10px;color:#333;background:#ffe6e6;">Nenhum resultado encontrado</div>').show();
                        } else {
                            data.results.forEach(function (item) {
                                var $item = $('<div></div>')
                                    .css({
                                        padding: '10px',
                                        cursor: 'pointer',
                                        borderBottom: '1px solid #ddd',
                                        color: '#333',
                                        background: '#ffffff'
                                    })
                                    .text(item.text)
                                    .data('id', item.id)
                                    .hover(
                                        function () { $(this).css({ background: '#e6f3ff', color: '#000' }); },
                                        function () { $(this).css({ background: '#ffffff', color: '#333' }); }
                                    )
                                    .on('click', function () {
                                        $input.val(item.text);
                                        $objectIdInput.val(item.id);
                                        $results.hide();
                                    });
                                $results.append($item);
                            });
                            $results.show();
                        }
                    },
                    error: function () {
                        $results.html('<div style="padding:10px;color:#333;background:#ffe6e6;">Erro ao buscar</div>').show();
                    }
                });
            }, 300);
        });

        // Handler para fechar resultados ao clicar fora - usando delegation
        $(document).on('click', function (e) {
            var $target = $(e.target);
            // Se clicou fora de um input de autocomplete e fora de resultados
            if (!$target.closest('input.section-item-autocomplete, input[name$="-search_item"], .autocomplete-results-container').length) {
                $('.autocomplete-results-container').hide();
            }
        });

        // Também esconder ao pressionar Escape
        $(document).on('keydown', function (e) {
            if (e.key === 'Escape') {
                $('.autocomplete-results-container').hide();
            }
        });
    });
})(django.jQuery);
