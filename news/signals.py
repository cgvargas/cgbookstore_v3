"""
news/signals.py

Signal que automatiza a inserção de novos artigos publicados
nas seções de notícias da home page.

Comportamento:
- Quando um artigo é publicado (is_published=True), este signal:
  1. Encontra todas as Seções com content_type='news' na home
  2. Insere o novo artigo no INÍCIO da seção (primeiro card)
  3. Empurra os cards existentes para frente
  4. Remove o card mais antigo se a seção ultrapassar max_items
  5. Invalida o cache da home page para refletir as mudanças
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


@receiver(post_save, sender='news.Article')
def auto_insert_article_in_news_sections(sender, instance, created, **kwargs):
    """
    Signal disparado após salvar um Article.

    Quando o artigo é publicado (is_published=True), ele é automaticamente
    inserido no início (primeiro card) de todas as seções de notícias ativas
    na home page. O último card é removido se a seção atingir o limite.

    Este signal é acionado tanto na criação quanto na atualização de artigos,
    mas só processa quando is_published=True e o artigo não está ainda na seção.
    """
    # Processar apenas artigos publicados
    if not instance.is_published:
        return

    try:
        # Importações dentro da função para evitar circular imports
        from core.models import Section, SectionItem

        # Obter ContentType do Article
        article_ct = ContentType.objects.get_for_model(instance)

        # Encontrar todas as seções de notícias ativas
        news_sections = list(Section.objects.filter(
            content_type='news',
            active=True
        ))

        if not news_sections:
            logger.debug("[NEWS SIGNAL] Nenhuma seção de notícias ativa encontrada.")
            return

        modified = False
        for section in news_sections:
            if _insert_article_at_start(section, instance, article_ct):
                modified = True

        # Invalidar cache da home page apenas se algo foi modificado
        if modified:
            cache.delete('home_full_context')
            logger.info(
                f"[NEWS SIGNAL] Cache da home invalidado após publicação: '{instance.title}'"
            )

    except Exception as e:
        # Nunca deixar o signal quebrar o fluxo de salvamento do artigo
        logger.error(
            f"[NEWS SIGNAL] Erro ao processar artigo '{instance.title}': {e}",
            exc_info=True
        )


def _insert_article_at_start(section, article, article_ct):
    """
    Insere um artigo no início de uma seção de notícias.

    Estratégia de ordenação:
    - Todos os itens existentes têm sua order incrementada em 1
    - O novo artigo recebe order=0 (primeiro card)
    - Se a seção ultrapassar max_items, o item com maior order é removido

    Args:
        section: instância de Section (content_type='news')
        article: instância de Article recém-publicado
        article_ct: ContentType do model Article

    Returns:
        bool: True se o artigo foi inserido, False se já existia na seção
    """
    from core.models import SectionItem

    # Verificar se o artigo já está nesta seção (evitar duplicatas)
    already_exists = SectionItem.objects.filter(
        section=section,
        content_type=article_ct,
        object_id=article.id
    ).exists()

    if already_exists:
        logger.debug(
            f"[NEWS SIGNAL] Artigo '{article.title}' já está na seção '{section.title}'. Ignorando."
        )
        return False

    # Determinar o limite máximo de itens
    # Usa campo max_items se existir no model Section, senão usa padrão de 6 itens
    max_items = getattr(section, 'max_items', None) or 6

    # Passo 1: Incrementar a order de TODOS os itens existentes (+1)
    # Isso "empurra" todos os cards para a direita/final
    SectionItem.objects.filter(
        section=section,
        active=True
    ).update(order=F('order') + 1)

    # Passo 2: Inserir o novo artigo como o primeiro item (order=0)
    SectionItem.objects.create(
        section=section,
        content_type=article_ct,
        object_id=article.id,
        order=0,
        active=True,
    )

    logger.info(
        f"[NEWS SIGNAL] ✅ Artigo '{article.title}' inserido no início "
        f"da seção '{section.title}' (order=0)."
    )

    # Passo 3: Verificar se ultrapassou o limite e remover o último item (mais antigo)
    total_after = SectionItem.objects.filter(section=section, active=True).count()

    if total_after > max_items:
        # Remover o item com maior order (o mais antigo / último na visualização)
        last_item = SectionItem.objects.filter(
            section=section,
            active=True
        ).order_by('-order').first()

        if last_item:
            removed_article_id = last_item.object_id
            removed_order = last_item.order
            last_item.delete()
            logger.info(
                f"[NEWS SIGNAL] 🗑️ Item removido da seção '{section.title}' "
                f"(Article ID={removed_article_id}, order={removed_order}) "
                f"— limite de {max_items} itens atingido."
            )

    return True
