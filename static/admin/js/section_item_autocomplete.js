/**
 * Autocomplete para SectionItem no Django Admin
 * Busca livros, autores e vídeos por nome via AJAX
 */
(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Inicializar autocomplete em todos os campos de busca
        initializeAutocomplete();
        
        // Re-inicializar quando um novo inline é adicionado
        $(document).on('formset:added', function(event, $row, formsetName) {
            if (formsetName === 'items') {
                initializeAutocomplete($row);
            }
        });
    });
    
    function initializeAutocomplete($context) {
        $context = $context || $(document);
        
        $context.find('input[name$="-search_item"]').each(function() {
            var $input = $(this);
            var $row = $input.closest('tr, .inline-related');
            var $contentTypeSelect = $row.find('select[name$="-content_type"]');
            var $objectIdInput = $row.find('input[name$="-object_id"]');
            
            // Evitar inicializar duas vezes
            if ($input.data('autocomplete-initialized')) return;
            $input.data('autocomplete-initialized', true);
            
            // Container para resultados
            var $results = $('<div class="autocomplete-results"></div>').css({
                position: 'absolute',
                zIndex: 9999,
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: '4px',
                maxHeight: '200px',
                overflowY: 'auto',
                display: 'none',
                width: $input.outerWidth() + 'px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            });
            
            $input.after($results);
            
            // Debounce para evitar muitas requisições
            var searchTimeout = null;
            
            $input.on('input', function() {
                clearTimeout(searchTimeout);
                var query = $(this).val();
                var contentType = $contentTypeSelect.find('option:selected').text().toLowerCase();
                
                if (query.length < 2) {
                    $results.hide();
                    return;
                }
                
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
                    $results.html('<div style="padding: 8px; color: #666;">Selecione um tipo primeiro</div>').show();
                    return;
                }
                
                searchTimeout = setTimeout(function() {
                    $.ajax({
                        url: '/admin-tools/section-autocomplete/',
                        data: { q: query, content_type: type },
                        success: function(data) {
                            $results.empty();
                            if (data.results.length === 0) {
                                $results.html('<div style="padding: 8px; color: #999;">Nenhum resultado</div>').show();
                            } else {
                                data.results.forEach(function(item) {
                                    var $item = $('<div style="padding: 8px; cursor: pointer; border-bottom: 1px solid #eee;"></div>')
                                        .text(item.text)
                                        .data('id', item.id)
                                        .hover(
                                            function() { $(this).css('background', '#f0f0f0'); },
                                            function() { $(this).css('background', '#fff'); }
                                        )
                                        .on('click', function() {
                                            $input.val(item.text);
                                            $objectIdInput.val(item.id);
                                            $results.hide();
                                        });
                                    $results.append($item);
                                });
                                $results.show();
                            }
                        }
                    });
                }, 300);
            });
            
            // Esconder resultados ao clicar fora
            $(document).on('click', function(e) {
                if (!$(e.target).closest($input.add($results)).length) {
                    $results.hide();
                }
            });
        });
    }
})(django.jQuery);
