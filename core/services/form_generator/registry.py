"""
Registry central de geradores de formulário de contribuição.

Para adicionar um novo tipo de formulário:
  1. Crie um arquivo MyFormGenerator em core/services/form_generator/
  2. Importe a classe aqui
  3. Adicione a entrada no FORM_REGISTRY

Nenhuma outra alteração é necessária no sistema.
"""

from .article_form import ArticleFormGenerator
from .book_form import BookFormGenerator

# ──────────────────────────────────────────────────────────────────────────
# Registry Principal
# Mapeia form_type (usado na URL) → classe geradora
# ──────────────────────────────────────────────────────────────────────────
FORM_REGISTRY = {
    'article': ArticleFormGenerator,
    'book': BookFormGenerator,

    # ── Extensível: adicione novos tipos aqui ─────────────────────────────
    # 'event': EventFormGenerator,
    # 'quiz': QuizFormGenerator,
    # 'author': AuthorFormGenerator,
    # 'review': ReviewFormGenerator,
}

# Metadados para exibição em interfaces (labels amigáveis para cada tipo)
FORM_REGISTRY_META = {
    'article': {
        'label': 'Artigo / Notícia',
        'description': 'Contribuir com uma notícia, entrevista, evento ou artigo editorial.',
        'icon': '📰',
        'color': '#2E86AB',
    },
    'book': {
        'label': 'Livro',
        'description': 'Solicitar a inclusão de um novo livro no catálogo.',
        'icon': '📚',
        'color': '#8E44AD',
    },
}


def get_generator(form_type: str):
    """
    Retorna uma instância do gerador para o tipo fornecido.

    Args:
        form_type: Chave do FORM_REGISTRY (ex: 'article', 'book')

    Returns:
        Instância do gerador correspondente.

    Raises:
        KeyError: Se form_type não estiver registrado.
    """
    generator_class = FORM_REGISTRY[form_type]
    return generator_class()


def get_available_types() -> list:
    """Retorna lista de tipos disponíveis com seus metadados."""
    result = []
    for form_type, meta in FORM_REGISTRY_META.items():
        if form_type in FORM_REGISTRY:
            result.append({
                'type': form_type,
                **meta
            })
    return result
