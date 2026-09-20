# core/services/book_cover_resolution_service.py
"""
Serviço Centralizado de Resolução e Hierarquia de Capas de Livros (Fase 1 - Open Library Covers API).

HIERARQUIA OFICIAL DE RESOLUÇÃO MULTI-TIER:
1. Imagem local fornecida por autor ou editora (Book.cover_image).
   - Se existir arquivo local e for permitida pela governança de direitos autorais
     (ImageRightsAuditService.can_display_publicly == True), tem precedência absoluta.
   - Caso o arquivo local exista mas esteja sob contestação ou suspensão preventiva,
     retorna None para respeitar imediatamente a decisão jurídica (sem vazamento).
2. Open Library Covers API (exibição remota oficial).
   - Se o livro possui ISBN e não há imagem local, consulta a existência de capa
     na Open Library Covers API via OpenLibraryCoverService.
   - Caso confirmada a existência, registra a proveniência técnica de forma segura
     (audit_status='not_audited', provenance_provider='open_library', license_type='', legal_basis='')
     e retorna a URL canônica remota oficial.
3. Amazon Associates / Creators API (se disponível).
4. Wikimedia Commons / Domínio Público / Licenças Abertas (se previamente registradas).
5. Fallback visual: retorna None (permitindo ao template exibir static/images/no-cover-placeholder.svg).
"""

import logging
from typing import Optional
from django.templatetags.static import static
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


class BookCoverResolutionService:
    """
    Coordena a resolução hierárquica e a governança de capas de livros da CG.BookStore.
    """

    PLACEHOLDER_STATIC_PATH = 'images/no-cover-placeholder.svg'

    @classmethod
    def get_cover_url(cls, book, size: str = 'L') -> Optional[str]:
        """
        Resolve a URL da capa para o livro especificado segundo a hierarquia de fontes oficial.

        Args:
            book: Instância do model Book.
            size: Tamanho desejado para capas remotas ('S', 'M', 'L'). Padrão: 'L'.

        Returns:
            URL da capa (com cache-buster se local, URL HTTPS se remota) ou None caso não
            haja capa disponível ou a mesma esteja suspensa administrativamente.
        """
        if not book or not getattr(book, 'pk', None):
            return None

        from core.services.image_rights_service import ImageRightsAuditService
        from core.models.image_rights import ImageRightsRecord
        from core.services.open_library_cover_service import OpenLibraryCoverService

        # -----------------------------------------------------------------
        # TIER 1: Imagem local fornecida por autor ou editora (Book.cover_image)
        # -----------------------------------------------------------------
        has_local_file = bool(book.cover_image and hasattr(book.cover_image, 'name') and book.cover_image.name)
        if has_local_file:
            # Verificar se a imagem local está permitida para exibição pública
            if ImageRightsAuditService.can_display_publicly(book, 'cover_image'):
                version = int(book.updated_at.timestamp()) if hasattr(book, 'updated_at') and book.updated_at else 1
                return f"{book.cover_image.url}?v={version}"
            else:
                # Decisão jurídica ou suspensão administrativa: interrompe a cadeia
                # para não contornar decisão do auditor com fontes externas
                return None

        # -----------------------------------------------------------------
        # TIER 2: Open Library Covers API (Exibição remota oficial)
        # -----------------------------------------------------------------
        isbn = getattr(book, 'isbn', None)
        if isbn:
            clean_isbn = OpenLibraryCoverService.normalize_isbn(isbn)
            if clean_isbn:
                # Verificar se já existe um ImageRightsRecord para este livro
                ct = ContentType.objects.get_for_model(book)
                rights_record = ImageRightsRecord.objects.filter(
                    content_type=ct,
                    object_id=book.pk,
                    image_field_name='cover_image'
                ).first()

                if rights_record:
                    # Se o registro existe mas a exibição pública foi restrita/suspensa
                    if not rights_record.can_display_publicly or rights_record.audit_status == 'restricted':
                        return None

                    # Se já for um registro de proveniência Open Library com source_url
                    # (compatível tanto com novo padrão provenance_provider='open_library'
                    # quanto com legado license_type='open_library')
                    is_open_library_record = (
                        rights_record.provenance_provider == 'open_library'
                        or rights_record.license_type == 'open_library'
                    )
                    if is_open_library_record and rights_record.source_url:
                        # Retornar a URL canônica correspondente ao tamanho solicitado
                        return OpenLibraryCoverService.get_canonical_url(clean_isbn, size=size)

                # Se não há registro impeditivo, consultar e registrar via OpenLibraryCoverService
                remote_url = OpenLibraryCoverService.resolve_and_register_book_cover(book, size=size)
                if remote_url:
                    return remote_url

        # -----------------------------------------------------------------
        # TIER 3: Amazon Associates / Parceiros (reservado para futuras expansões)
        # -----------------------------------------------------------------

        # -----------------------------------------------------------------
        # TIER 4: Wikimedia Commons / Domínio Público (se registrado em source_url)
        # -----------------------------------------------------------------

        # -----------------------------------------------------------------
        # TIER 5: Fallback — Sem capa disponível
        # -----------------------------------------------------------------
        return None

    @classmethod
    def has_valid_cover(cls, book) -> bool:
        """
        Indica se o livro possui uma capa válida e autorizada para exibição.
        """
        return cls.get_cover_url(book) is not None

    @classmethod
    def get_cover_source_type(cls, book) -> str:
        """
        Identifica o tipo de fonte da capa ativa do livro.
        Retornos: 'local', 'open_library', 'other_remote', 'none'.
        """
        if not book:
            return 'none'

        from core.services.image_rights_service import ImageRightsAuditService
        has_local_file = bool(book.cover_image and hasattr(book.cover_image, 'name') and book.cover_image.name)
        if has_local_file and ImageRightsAuditService.can_display_publicly(book, 'cover_image'):
            return 'local'

        url = cls.get_cover_url(book)
        if not url:
            return 'none'

        if 'openlibrary.org' in url:
            return 'open_library'

        return 'other_remote'

    @classmethod
    def get_display_cover_or_placeholder(cls, book, size: str = 'L') -> str:
        """
        Retorna a URL da capa resolvida ou a URL estática do placeholder padrão do sistema.
        """
        resolved_url = cls.get_cover_url(book, size=size)
        if resolved_url:
            return resolved_url
        return static(cls.PLACEHOLDER_STATIC_PATH)
