import re

with open('templates/core/book_detail.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Read old video section
with open('extracted.txt', 'r', encoding='utf-8') as f:
    old_video_section = f.read()

articles_block = """            {# ===== SEÇÃO: CONTEÚDOS RELACIONADOS (Artigos e Notícias) ===== #}
            {% if book_articles %}
            <div class="related-content-section mb-4 mt-4">
                <h5 class="related-content-title mb-3">
                    <i class="fas fa-newspaper me-2"></i>Conteúdos Relacionados
                </h5>
                <div class="row g-3">

                    {# --- Cards de Artigos/Notícias --- #}
                    {% for article in book_articles %}
                    <div class="col-lg-4 col-md-6 col-12">
                        <a href="{{ article.get_absolute_url }}"
                           class="related-card-link text-decoration-none"
                           title="{{ article.title }}">
                            <div class="related-card">
                                <div class="related-card-image">
                                    {% if article.featured_image %}
                                    <img src="{{ article.featured_image.url }}"
                                         alt="{{ article.title }}"
                                         loading="lazy">
                                    {% else %}
                                    <div class="related-card-placeholder">
                                        <i class="fas fa-newspaper fa-3x"></i>
                                    </div>
                                    {% endif %}
                                    <div class="related-card-overlay"></div>
                                    <span class="related-card-badge related-card-badge--article">
                                        <i class="fas fa-newspaper me-1"></i>{{ article.get_content_type_display }}
                                    </span>
                                </div>
                                <div class="related-card-body">
                                    <h6 class="related-card-title">{{ article.title }}</h6>
                                    {% if article.published_at %}
                                    <span class="related-card-meta">
                                        <i class="fas fa-calendar-alt me-1"></i>{{ article.published_at|date:"d/m/Y" }}
                                    </span>
                                    {% endif %}
                                </div>
                            </div>
                        </a>
                    </div>
                    {% endfor %}

                </div>

                {# Link "Ver todas as notícias" #}
                <div class="d-flex flex-wrap gap-3 mt-3">
                    <a href="{% url 'news:home' %}" class="related-content-viewall">
                        <i class="fas fa-newspaper me-1"></i>Ver todas as notícias
                        <i class="fas fa-arrow-right ms-1"></i>
                    </a>
                </div>
            </div>
            {% endif %}"""

# Insert at the bottom, just after related_books ends.
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
