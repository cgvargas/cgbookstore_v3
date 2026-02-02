"""
Admin para Author com autocomplete para associar livros existentes.
"""
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from core.models import Author, Book


class BookInlineForm(forms.ModelForm):
    """Formulário para o inline de livros com autocomplete."""
    
    class Meta:
        model = Book
        fields = ['title', 'isbn', 'publication_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se for um livro novo (sem pk), apenas mostra campo de busca
        if not self.instance.pk:
            # Limpar campos para não permitir criação
            for field in self.fields:
                self.fields[field].required = False


class BookInline(admin.TabularInline):
    """
    Inline para exibir e associar livros ao autor.
    
    - Livros existentes: mostrados como somente leitura
    - Adicionar: usa autocomplete para buscar livros existentes
    """

    model = Book
    extra = 1  # Mostra 1 formulário extra para adicionar
    can_delete = True  # Permite remover associação (não deleta o livro)
    show_change_link = True
    verbose_name = "Livro do Autor"
    verbose_name_plural = "Livros do Autor"
    
    # Usa autocomplete para o campo title (na verdade seleciona livro existente)
    autocomplete_fields = []  # Não funciona para o próprio modelo
    
    fields = ['cover_thumbnail', 'title', 'isbn', 'publication_date']
    readonly_fields = ['cover_thumbnail']
    
    def cover_thumbnail(self, obj):
        """Miniatura da capa do livro."""
        if obj and obj.pk and obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 35px; object-fit: cover; border-radius: 4px;" />',
                obj.cover_image.url
            )
        return "-"
    cover_thumbnail.short_description = "Capa"
    
    def get_readonly_fields(self, request, obj=None):
        """Livros existentes são somente leitura."""
        if obj:  # Editando autor existente
            return ['cover_thumbnail', 'title', 'isbn', 'publication_date']
        return ['cover_thumbnail']
    
    def has_delete_permission(self, request, obj=None):
        """Permite 'deletar' que na verdade remove a associação."""
        return True
    
    def delete_queryset(self, request, queryset):
        """Ao deletar, apenas remove a associação com o autor."""
        queryset.update(author=None)
    
    def delete_model(self, request, obj):
        """Ao deletar um livro do inline, apenas remove a associação."""
        obj.author = None
        obj.save()


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administração de Autores com inline de livros."""

    list_display = ['name', 'photo_preview', 'books_count', 'social_media_display', 'created_at']
    search_fields = ['name', 'bio']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'photo_preview', 'associate_books_widget']
    date_hierarchy = 'created_at'
    inlines = [BookInline]

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'slug', 'bio')
        }),
        ('Foto', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Redes Sociais', {
            'classes': ('collapse',),
            'fields': ('website', 'twitter', 'instagram')
        }),
        ('📚 Buscar e Associar Livros Existentes', {
            'fields': ('associate_books_widget',),
            'description': 'Use a busca abaixo para encontrar e associar livros existentes a este autor.'
        }),
        ('Metadados', {
            'classes': ('collapse',),
            'fields': ('created_at',)
        })
    )
    
    def associate_books_widget(self, obj):
        """Widget de busca e associação de livros."""
        if not obj or not obj.pk:
            return "Salve o autor primeiro para poder associar livros."
        
        # Widget com busca AJAX de livros
        return format_html('''
            <div id="book-search-container" style="margin-bottom: 20px;">
                <input type="text" id="book-search-input" 
                       placeholder="🔍 Digite o título do livro para buscar..." 
                       style="width: 100%; padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;"
                       autocomplete="off">
                <div id="book-search-results" 
                     style="display: none; border: 1px solid #417690; border-radius: 4px; max-height: 300px; overflow-y: auto; background: #fff; margin-top: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                </div>
                <p style="margin-top: 10px; color: #666; font-size: 12px;">
                    <strong>Dica:</strong> Após selecionar um livro, a página será recarregada com o livro associado.
                </p>
            </div>
            
            <script>
            (function() {{
                var input = document.getElementById('book-search-input');
                var results = document.getElementById('book-search-results');
                var timeout = null;
                var authorId = {author_id};
                
                input.addEventListener('input', function() {{
                    clearTimeout(timeout);
                    var query = this.value;
                    
                    if (query.length < 2) {{
                        results.style.display = 'none';
                        return;
                    }}
                    
                    timeout = setTimeout(function() {{
                        fetch('/admin-tools/book-search/?q=' + encodeURIComponent(query) + '&exclude_author=' + authorId)
                            .then(function(r) {{ return r.json(); }})
                            .then(function(data) {{
                                results.innerHTML = '';
                                if (data.results.length === 0) {{
                                    results.innerHTML = '<div style="padding: 15px; color: #666;">Nenhum livro encontrado</div>';
                                }} else {{
                                    data.results.forEach(function(book) {{
                                        var div = document.createElement('div');
                                        div.style.cssText = 'padding: 10px 15px; cursor: pointer; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 10px;';
                                        div.innerHTML = '<span style="font-weight: bold;">' + book.title + '</span>' +
                                                       (book.author ? '<span style="color: #888; font-size: 12px;">(' + book.author + ')</span>' : '<span style="color: #28a745; font-size: 12px;">(sem autor)</span>');
                                        div.addEventListener('mouseover', function() {{ this.style.background = '#e6f3ff'; }});
                                        div.addEventListener('mouseout', function() {{ this.style.background = '#fff'; }});
                                        div.addEventListener('click', function() {{
                                            if (confirm('Associar "' + book.title + '" a este autor?')) {{
                                                fetch('/admin-tools/associate-book/', {{
                                                    method: 'POST',
                                                    headers: {{
                                                        'Content-Type': 'application/json',
                                                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                                    }},
                                                    body: JSON.stringify({{ book_id: book.id, author_id: authorId }})
                                                }})
                                                .then(function(r) {{ return r.json(); }})
                                                .then(function(data) {{
                                                    if (data.success) {{
                                                        location.reload();
                                                    }} else {{
                                                        alert('Erro: ' + data.error);
                                                    }}
                                                }});
                                            }}
                                        }});
                                        results.appendChild(div);
                                    }});
                                }}
                                results.style.display = 'block';
                            }});
                    }}, 300);
                }});
                
                document.addEventListener('click', function(e) {{
                    if (!e.target.closest('#book-search-container')) {{
                        results.style.display = 'none';
                    }}
                }});
            }})();
            </script>
        ''', author_id=obj.pk)
    
    associate_books_widget.short_description = "Buscar Livros"

    def photo_preview(self, obj):
        """Preview da foto do autor."""
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 50%;" />',
                obj.photo.url
            )
        return "Sem foto"

    photo_preview.short_description = "Preview"

    def books_count(self, obj):
        """Quantidade de livros do autor."""
        count = obj.books.count()
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} livros</span>',
                count
            )
        return mark_safe('<span style="color: gray;">0 livros</span>')

    books_count.short_description = "Livros"

    def social_media_display(self, obj):
        """Indica se tem redes sociais cadastradas."""
        if obj.website or obj.twitter or obj.instagram:
            return mark_safe('<span style="color: green;">✓</span>')
        return mark_safe('<span style="color: gray;">✗</span>')

    social_media_display.short_description = "Redes Sociais"