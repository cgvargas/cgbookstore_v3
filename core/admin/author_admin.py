from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from core.models import Author, Book, AuthorWork


class AuthorWorkInline(admin.TabularInline):
    """Inline para gerenciar as obras lançadas pelo autor."""

    model = AuthorWork
    extra = 1
    fields = ['order', 'year', 'title', 'format', 'publisher', 'notes']
    verbose_name = "Obra Lançada"
    verbose_name_plural = "Obras Lançadas"
    ordering = ['order', 'year']

    class Media:
        css = {'all': []}



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
    readonly_fields = ['created_at', 'photo_preview', 'associate_books_widget', 'import_works_widget', 'delete_works_widget']
    date_hierarchy = 'created_at'
    inlines = [BookInline, AuthorWorkInline]

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
        ('📥 Gerenciar Obras Lançadas em Lote', {
            'fields': ('import_works_widget', 'delete_works_widget'),
            'description': 'Importe várias obras via CSV ou exclua todas de uma vez.'
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
        
        # Widget com busca AJAX de livros - compatível com tema escuro
        return format_html('''
            <style>
                #book-search-container {{
                    margin-bottom: 20px;
                }}
                #book-search-input {{
                    width: 100%;
                    padding: 10px;
                    font-size: 14px;
                    border: 1px solid var(--border-color, #ccc);
                    border-radius: 4px;
                    background: var(--body-bg, #fff);
                    color: var(--body-fg, #333);
                }}
                #book-search-input::placeholder {{
                    color: var(--body-quiet-color, #666);
                }}
                #book-search-results {{
                    display: none;
                    border: 1px solid var(--primary, #417690);
                    border-radius: 4px;
                    max-height: 300px;
                    overflow-y: auto;
                    background: var(--body-bg, #fff);
                    margin-top: 5px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }}
                .book-result-item {{
                    padding: 10px 15px;
                    cursor: pointer;
                    border-bottom: 1px solid var(--hairline-color, #eee);
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    color: var(--body-fg, #333);
                }}
                .book-result-item:hover {{
                    background: var(--darkened-bg, #e6f3ff);
                }}
                .book-result-title {{
                    font-weight: bold;
                    color: var(--body-fg, #333);
                }}
                .book-result-author {{
                    font-size: 12px;
                    color: var(--body-quiet-color, #888);
                }}
                .book-result-no-author {{
                    font-size: 12px;
                    color: var(--message-success-bg, #28a745);
                }}
                .book-search-empty {{
                    padding: 15px;
                    color: var(--body-quiet-color, #666);
                }}
                .book-search-hint {{
                    margin-top: 10px;
                    color: var(--body-quiet-color, #666);
                    font-size: 12px;
                }}
            </style>
            <div id="book-search-container">
                <input type="text" id="book-search-input" 
                       placeholder="🔍 Digite o título do livro para buscar..." 
                       autocomplete="off">
                <div id="book-search-results"></div>
                <p class="book-search-hint">
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
                                    results.innerHTML = '<div class="book-search-empty">Nenhum livro encontrado</div>';
                                }} else {{
                                    data.results.forEach(function(book) {{
                                        var div = document.createElement('div');
                                        div.className = 'book-result-item';
                                        div.innerHTML = '<span class="book-result-title">' + book.title + '</span>' +
                                                       (book.author ? '<span class="book-result-author">(' + book.author + ')</span>' : '<span class="book-result-no-author">(sem autor)</span>');
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

    def import_works_widget(self, obj):
        """Widget para importar obras lançadas em lote via CSV."""
        if not obj or not obj.pk:
            return "Salve o autor primeiro para poder importar obras."

        author_id = int(obj.pk)

        html = f"""
<div>
  <button type="button"
    onclick="document.getElementById('csv-panel').style.display='block';"
    style="background:var(--primary,#417690);color:#fff;border:none;padding:10px 20px;
           border-radius:4px;cursor:pointer;font-size:14px;font-weight:bold;">
    &#128229; Importar Obras via CSV
  </button>

  <div id="csv-panel" style="display:none;margin-top:16px;
       border:2px solid var(--primary,#417690);border-radius:8px;padding:20px;
       background:var(--body-bg,#fff);color:var(--body-fg,#333);max-width:680px;">

    <h3 style="margin:0 0 14px;font-size:16px;color:var(--body-fg,#333);">
      &#128197; Importar Obras em Lote via CSV
    </h3>

    <!-- Passo 1 -->
    <div style="margin-bottom:12px;padding:10px;background:var(--darkened-bg,#f5f5f5);
                border-left:3px solid var(--primary,#417690);border-radius:4px;">
      <strong style="display:block;margin-bottom:6px;color:var(--body-fg,#333);">
        1&#186; Baixe o modelo e preencha:
      </strong>
      <a href="/admin-tools/author-works-template/" download
         style="color:var(--primary,#417690);font-weight:bold;">
        &#11015;&#65039; Baixar Template CSV
      </a>
    </div>

    <!-- Passo 2 -->
    <div style="margin-bottom:12px;padding:10px;background:var(--darkened-bg,#f5f5f5);
                border-left:3px solid var(--primary,#417690);border-radius:4px;">
      <strong style="display:block;margin-bottom:6px;color:var(--body-fg,#333);">
        2&#186; Selecione o arquivo CSV preenchido:
      </strong>
      <input type="file" id="csv-file-input" accept=".csv"
             onchange="csvOnFileChange(this)"
             style="padding:4px;border:1px dashed var(--primary,#417690);border-radius:4px;
                    width:100%;cursor:pointer;background:var(--body-bg,#fff);color:var(--body-fg,#333);">
    </div>

    <!-- Preview -->
    <div id="csv-preview-area" style="display:none;margin-bottom:12px;">
      <strong style="color:var(--body-fg,#333);">Preview:</strong>
      <div id="csv-preview-table" style="overflow-x:auto;margin-top:6px;"></div>
      <div id="csv-info-box"
           style="margin-top:6px;padding:8px;background:var(--darkened-bg,#e8f4fd);
                  border-radius:4px;font-size:13px;color:var(--body-fg,#333);"></div>
    </div>

    <!-- Status -->
    <div id="csv-status-msg"
         style="display:none;margin-bottom:10px;padding:10px;border-radius:4px;font-size:13px;">
    </div>

    <!-- Botões -->
    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:8px;">
      <button type="button"
        onclick="document.getElementById('csv-panel').style.display='none';"
        style="background:transparent;border:1px solid var(--border-color,#ccc);
               color:var(--body-quiet-color,#555);padding:7px 16px;border-radius:4px;cursor:pointer;">
        Fechar
      </button>
      <button type="button" id="csv-confirm-btn"
        onclick="csvDoImport({author_id})"
        disabled
        style="background:var(--primary,#417690);color:#fff;border:none;
               padding:7px 18px;border-radius:4px;font-weight:bold;
               opacity:0.4;cursor:not-allowed;">
        Importar
      </button>
    </div>

  </div>
</div>

<script>
var _csvData = [];

function csvOnFileChange(input) {{
  var btn = document.getElementById('csv-confirm-btn');
  var f = input.files[0];
  if (!f) {{
    btn.disabled = true;
    btn.style.opacity = '0.4';
    btn.style.cursor = 'not-allowed';
    btn.textContent = 'Importar';
    return;
  }}
  btn.textContent = 'Lendo...';
  var reader = new FileReader();
  reader.onload = function(evt) {{
    var txt = evt.target.result;
    // Remove BOM se presente
    if (txt.charCodeAt(0) === 0xFEFF) txt = txt.slice(1);
    // Divide em linhas
    var lines = txt.split(/[\\r\\n]+/).filter(function(l) {{ return l.trim() !== ''; }});
    if (lines.length < 2) {{
      _csvMsg('Arquivo sem linhas de dados.', false);
      btn.disabled = true; btn.style.opacity = '0.4'; btn.style.cursor = 'not-allowed';
      btn.textContent = 'Importar';
      return;
    }}
    var hdr = _csvParseLine(lines[0]);
    _csvData = [];
    for (var i = 1; i < lines.length; i++) {{
      var cols = _csvParseLine(lines[i]);
      if (cols.every(function(v) {{ return v.trim() === ''; }})) continue;
      var row = {{}};
      hdr.forEach(function(h, j) {{
        row[h.trim().toLowerCase()] = (cols[j] || '').trim();
      }});
      if (row.title) _csvData.push(row);
    }}
    if (!_csvData.length) {{
      _csvMsg('Nenhuma linha com t\u00edtulo encontrada.', false);
      btn.disabled = true; btn.style.opacity = '0.4'; btn.style.cursor = 'not-allowed';
      btn.textContent = 'Importar';
      return;
    }}
    // Renderizar preview
    var cols = ['order','year','title','format','publisher','notes'];
    var ths = cols.map(function(c) {{
      return '<th style="background:var(--primary,#417690);color:#fff;padding:4px 8px;text-align:left;">' + c + '</th>';
    }}).join('');
    var trs = _csvData.slice(0, 10).map(function(row) {{
      return '<tr>' + cols.map(function(c) {{
        var v = row[c] || '';
        return '<td style="padding:3px 8px;border-bottom:1px solid var(--hairline-color,#ddd);'
             + 'max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'
             + 'color:var(--body-fg,#333);" title="' + v + '">' + v + '</td>';
      }}).join('') + '</tr>';
    }}).join('');
    document.getElementById('csv-preview-table').innerHTML =
      '<table style="width:100%;border-collapse:collapse;font-size:12px;">'
      + '<thead><tr>' + ths + '</tr></thead>'
      + '<tbody>' + trs + '</tbody></table>';
    var extra = _csvData.length > 10 ? ' (exibindo as 10 primeiras)' : '';
    document.getElementById('csv-info-box').innerHTML =
      '<strong>' + _csvData.length + ' obra(s)</strong> ser\u00e3o importadas' + extra
      + '. As j\u00e1 existentes n\u00e3o ser\u00e3o apagadas.';
    document.getElementById('csv-preview-area').style.display = 'block';
    document.getElementById('csv-status-msg').style.display = 'none';
    // Habilitar botão
    btn.disabled = false;
    btn.style.opacity = '1';
    btn.style.cursor = 'pointer';
    btn.textContent = 'Importar ' + _csvData.length + ' obra(s)';
  }};
  reader.readAsText(f, 'UTF-8');
}}

function csvDoImport(aid) {{
  var fi = document.getElementById('csv-file-input');
  if (!fi.files[0]) return;
  var btn = document.getElementById('csv-confirm-btn');
  btn.disabled = true;
  btn.style.opacity = '0.6';
  btn.style.cursor = 'not-allowed';
  btn.textContent = 'Importando...';
  var fd = new FormData();
  fd.append('csv_file', fi.files[0]);
  fd.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
  fetch('/admin-tools/import-author-works/' + aid + '/', {{method:'POST', body:fd}})
    .then(function(r) {{ return r.json(); }})
    .then(function(d) {{
      if (d.success) {{
        _csvMsg('\u2705 ' + d.message, true);
        btn.style.display = 'none';
        setTimeout(function() {{ location.reload(); }}, 1500);
      }} else {{
        _csvMsg('\u274c ' + d.error, false);
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.style.cursor = 'pointer';
        btn.textContent = 'Tentar novamente';
      }}
    }})
    .catch(function(e) {{
      _csvMsg('\u274c Erro: ' + e, false);
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.style.cursor = 'pointer';
      btn.textContent = 'Tentar novamente';
    }});
}}

function _csvMsg(msg, ok) {{
  var el = document.getElementById('csv-status-msg');
  el.innerHTML = msg;
  el.style.background = ok ? '#d4edda' : '#f8d7da';
  el.style.color      = ok ? '#155724' : '#721c24';
  el.style.border     = ok ? '1px solid #c3e6cb' : '1px solid #f5c6cb';
  el.style.display    = 'block';
}}

function _csvParseLine(line) {{
  var result = [], inQuote = false, cur = '';
  for (var i = 0; i < line.length; i++) {{
    var ch = line[i];
    if (ch === '"') {{ inQuote = !inQuote; }}
    else if (ch === ',' && !inQuote) {{ result.push(cur); cur = ''; }}
    else {{ cur += ch; }}
  }}
  result.push(cur);
  return result;
}}
</script>
"""
        return mark_safe(html)

    import_works_widget.short_description = "Importar via CSV"

    def delete_works_widget(self, obj):
        """Widget para exclusão em lote de todas as obras do autor."""
        if not obj or not obj.pk:
            return ""

        author_id = int(obj.pk)
        works_count = obj.works.count()
        if works_count == 0:
            return mark_safe('<span style="color:var(--body-quiet-color,#666);">Nenhuma obra para excluir.</span>')

        html = f"""
<div>
  <button type="button" id="delete-works-btn"
    onclick="deleteAllWorks({author_id})"
    style="background:#dc3545;color:#fff;border:none;padding:10px 20px;
           border-radius:4px;cursor:pointer;font-size:14px;font-weight:bold;">
    🗑️ Excluir Todas as Obras ({works_count})
  </button>
  <div id="delete-status-msg" style="display:none;margin-top:10px;padding:10px;border-radius:4px;font-size:13px;"></div>
</div>
<script>
function deleteAllWorks(aid) {{
  if (!confirm('Tem certeza que deseja excluir TODAS as ' + {works_count} + ' obras lançadas deste autor?\\n\\nEsta ação não pode ser desfeita!')) return;
  var btn = document.getElementById('delete-works-btn');
  btn.disabled = true;
  btn.style.opacity = '0.6';
  btn.style.cursor = 'not-allowed';
  btn.textContent = '⏳ Excluindo...';
  
  fetch('/admin-tools/delete-author-works/' + aid + '/', {{
      method: 'POST',
      headers: {{
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      }}
  }})
  .then(function(r) {{ return r.json(); }})
  .then(function(d) {{
      var msg = document.getElementById('delete-status-msg');
      msg.style.display = 'block';
      if (d.success) {{
          msg.innerHTML = '✅ ' + d.message;
          msg.style.background = '#d4edda';
          msg.style.color = '#155724';
          msg.style.border = '1px solid #c3e6cb';
          btn.style.display = 'none';
          setTimeout(function() {{ location.reload(); }}, 1500);
      }} else {{
          msg.innerHTML = '❌ Erro: ' + d.error;
          msg.style.background = '#f8d7da';
          msg.style.color = '#721c24';
          msg.style.border = '1px solid #f5c6cb';
          btn.disabled = false;
          btn.style.opacity = '1';
          btn.style.cursor = 'pointer';
          btn.textContent = 'Tentar Novamente';
      }}
  }})
  .catch(function(e) {{ 
      alert('Erro: ' + e); 
      btn.disabled=false; 
      btn.style.opacity='1'; 
      btn.style.cursor='pointer';
      btn.textContent='Tentar Novamente'; 
  }});
}}
</script>
"""
        return mark_safe(html)

    delete_works_widget.short_description = "Excluir em Lote"



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