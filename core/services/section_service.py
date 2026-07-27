"""
core/services/section_service.py

Serviço centralizado para rotação e automação de inclusão de itens (livros, notícias, etc.)
nas seções dinâmicas da Home Page.

Comportamento:
- Insere o item como o 1º card (ordem 0) da seção especificada.
- Incrementa a ordem dos itens existentes em +1 (shift down).
- Remove os itens excedentes caso a quantidade de itens ativos ultrapasse o limite max_items da seção (FIFO rotation).
- Invalida o cache da Home Page para refletir as alterações instantaneamente.
"""
import logging
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

logger = logging.getLogger(__name__)


def insert_book_into_section(book, section, custom_title='', custom_description=''):
    """
    Insere um livro no início (ordem 0) de uma seção dinâmica da home.

    Args:
        book (Book): Instância do livro a ser inserido.
        section (Section): Instância da seção de destino.
        custom_title (str, optional): Título customizado para o card na seção.
        custom_description (str, optional): Descrição customizada para o card na seção.

    Returns:
        tuple (bool, str): (Sucesso, Mensagem descritiva do resultado)
    """
    if not book or not section:
        return False, "Livro ou Seção inválidos."

    try:
        from core.models import SectionItem

        book_ct = ContentType.objects.get_for_model(book)

        # 1. Verificar se o livro já existe na seção
        existing_item = SectionItem.objects.filter(
            section=section,
            content_type=book_ct,
            object_id=book.id
        ).first()

        if existing_item:
            # Se já existir e estiver no topo (order 0 e ativo), não faz nada
            if existing_item.order == 0 and existing_item.active:
                logger.info(f"[SECTION SERVICE] Livro '{book.title}' já é o 1º item da seção '{section.title}'.")
                return True, f"O livro '{book.title}' já é o primeiro item da seção '{section.title}'."

            # Se já existir em outra posição, reposiciona para o topo (re-ordenação)
            logger.info(f"[SECTION SERVICE] Reposicionando livro '{book.title}' para o topo da seção '{section.title}'.")
            existing_item.delete()

        # 2. Incrementar a ordem de todos os itens ativos existentes (+1)
        SectionItem.objects.filter(
            section=section,
            active=True
        ).update(order=F('order') + 1)

        # 3. Criar o novo SectionItem como o primeiro (order=0)
        SectionItem.objects.create(
            section=section,
            content_type=book_ct,
            object_id=book.id,
            order=0,
            active=True,
            custom_title=custom_title,
            custom_description=custom_description
        )

        logger.info(
            f"[SECTION SERVICE] ✅ Livro '{book.title}' inserido com sucesso no topo da seção '{section.title}' (order=0)."
        )

        # 4. Verificar limite max_items e remover itens excedentes (do final)
        max_items = getattr(section, 'max_items', 6) or 6
        active_items = list(
            SectionItem.objects.filter(section=section, active=True).order_by('order')
        )

        removed_count = 0
        if len(active_items) > max_items:
            # Os itens que excederem o limite (a partir do índice max_items) serão removidos
            excess_items = active_items[max_items:]
            for item in excess_items:
                item_title = item.get_display_title()
                item.delete()
                removed_count += 1
                logger.info(
                    f"[SECTION SERVICE] 🗑️ Item excedente '{item_title}' (id={item.id}) removido da seção '{section.title}' (limite={max_items})."
                )

        # 5. Invalidar o cache da Home Page
        cache.delete('home_full_context')
        logger.info(f"[SECTION SERVICE] Cache 'home_full_context' invalidado após inserção do livro na seção.")

        msg = f"Livro '{book.title}' adicionado ao topo da seção '{section.title}'."
        if removed_count > 0:
            msg += f" ({removed_count} item(ns) antigo(s) removido(s) pelo limite de {max_items} itens)."
        return True, msg

    except Exception as e:
        logger.error(f"[SECTION SERVICE] Erro ao inserir livro '{book.title}' na seção '{section.title}': {e}", exc_info=True)
        return False, f"Erro ao adicionar livro na seção: {e}"


def auto_detect_and_insert_book_section(book):
    """
    Detecta automaticamente se o livro pertence à seção 'Lançamentos'
    (baseado na categoria do livro) e faz a inserção se aplicável.

    Returns:
        tuple (bool, str): (Processado, Mensagem)
    """
    if not book or not book.category:
        return False, "Livro sem categoria definida."

    category_name = (book.category.name or '').lower()
    category_slug = (book.category.slug or '').lower()

    # Verificar se a categoria remete a Lançamentos
    is_release_category = 'lançamento' in category_name or 'lancamento' in category_name or 'lancamento' in category_slug or 'lançamento' in category_slug

    if not is_release_category:
        return False, "Categoria do livro não é de Lançamentos."

    from core.models import Section

    # Buscar seção ativa de Lançamentos
    release_section = Section.objects.filter(
        active=True,
        content_type__in=['books', 'mixed']
    ).filter(
        title__icontains='lançamento'
    ).first()

    if not release_section:
        # Fallback: tentar por slug ou título contendo 'lancamento'
        release_section = Section.objects.filter(
            active=True,
            content_type__in=['books', 'mixed']
        ).filter(
            title__icontains='lancamento'
        ).first()

    if not release_section:
        logger.warning(f"[SECTION SERVICE] Categoria do livro '{book.title}' é Lançamentos, mas nenhuma seção de Lançamentos ativa foi encontrada.")
        return False, "Nenhuma seção de Lançamentos ativa foi encontrada na Home."

    return insert_book_into_section(book, release_section)
