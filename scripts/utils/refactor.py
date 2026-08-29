import re

with open('templates/core/book_detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Extract "Conteúdos Relacionados" block
art_match = re.search(r'(\s*{# ===== SEÇÃO: CONTEÚDOS RELACIONADOS \(Artigos e Notícias\) ===== #}.*?{% endif %}\n)', html, re.DOTALL)
articles_block = art_match.group(1) if art_match else ""

# 2. Remove "Adaptações e Vídeos" new block and "Conteúdos Relacionados" block from their current position
vid_match = re.search(r'(\s*{# ===== SEÇÃO: ADAPTAÇÕES E VÍDEOS ===== #}.*?{% endif %}\n)', html, re.DOTALL)

if vid_match:
    html = html.replace(vid_match.group(1), "")
if art_match:
    html = html.replace(articles_block, "")

# 3. Read old video section
with open('extracted.txt', 'r', encoding='utf-8') as f:
    old_video_section = f.read()

# 4. Insert old video section and articles block at the bottom
# The bottom of col-lg-9 after "Livros Relacionados" is:
#                 {% endfor %}
#             </div>
#             {% endif %}
#         </div>

insert_target = r'(                {% endfor %}\s*</div>\s*{% endif %}\s*</div>)'
replacement = old_video_section + "\n" + articles_block + "\n\\1"
html = re.sub(insert_target, replacement, html)

# 5. Insert old CSS
with open('extracted_css.txt', 'r', encoding='utf-8') as f:
    old_css = f.read()

css_target = r'(<style>)'
css_replacement = r'\1\n' + old_css
html = re.sub(css_target, css_replacement, html, count=1)

with open('templates/core/book_detail.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done")
