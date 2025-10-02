(function($) {
    $(document).ready(function() {
        // Esconder/mostrar campos baseado no content_type selecionado
        $('select[name$="-content_type"]').on('change', function() {
            const $row = $(this).closest('tr');
            const selected = $(this).find('option:selected').text().toLowerCase();

            // Esconder todos primeiro
            $row.find('.field-book, .field-author, .field-video').hide();

            // Mostrar o relevante
            if (selected.includes('book') || selected.includes('livro')) {
                $row.find('.field-book').show();
            } else if (selected.includes('author') || selected.includes('autor')) {
                $row.find('.field-author').show();
            } else if (selected.includes('video') || selected.includes('vídeo')) {
                $row.find('.field-video').show();
            }
        }).trigger('change');
    });
})(django.jQuery);