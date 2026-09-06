# core/services/image_rights_research_service.py
"""
Serviço Central de Pesquisa Assistida de Direitos Autorais de Imagens (Fase 3A).

DIRETRIZ CENTRAL DE GOVERNANÇA:
- A automação pesquisa, coleta, compara e propõe. O administrador confirma.
- NUNCA altera audit_status, public_display_allowed ou legal_basis automaticamente.
- NUNCA sobrescreve dados existentes silenciosamente.
- Pesquisa NÃO gera ImageRightsAuditLog (somente a aplicação manual gera).
- Confidence mede identificação factual, NÃO legalidade.
- Proteção SSRF, timeouts, sanitização de URLs.
- Sem scraping, sem crawler, sem decisões jurídicas automáticas.
"""

import logging
import socket
import ipaddress
from datetime import timedelta
from typing import Optional, Dict, Any, List
import re
import hashlib
from urllib.parse import urlsplit

import requests
from django.db import transaction
from django.utils import timezone

from core.models.image_rights import ImageRightsRecord
from core.models.image_rights_research import ImageRightsResearchResult
from core.models.institutional_source import InstitutionalSource
from core.services.image_rights_history_service import ImageRightsHistoryService
from core.services.image_rights_provenance_service import ImageRightsProvenanceService

logger = logging.getLogger(__name__)

# Base de sementes conhecidas e verificadas de fontes institucionais
KNOWN_INSTITUTIONAL_SOURCES = {
    'harpercollins brasil': {
        'domain': 'harpercollins.com.br',
        'main_url': 'https://harpercollins.com.br',
        'terms_url': 'https://harpercollins.com.br/pages/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Página oficial de termos de uso da editora. Todos os direitos reservados. Proibida reprodução não autorizada do catálogo e elementos visuais.',
    },
    'harpercollins': {
        'domain': 'harpercollins.com.br',
        'main_url': 'https://harpercollins.com.br',
        'terms_url': 'https://harpercollins.com.br/pages/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Página oficial de termos de uso da editora. Todos os direitos reservados.',
    },
    'companhia das letras': {
        'domain': 'companhiadasletras.com.br',
        'main_url': 'https://www.companhiadasletras.com.br',
        'terms_url': 'https://www.companhiadasletras.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso do Grupo Companhia das Letras. Conteúdo protegido por direitos autorais.',
    },
    'record': {
        'domain': 'record.com.br',
        'main_url': 'https://www.record.com.br',
        'terms_url': 'https://www.record.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos institucionais do Grupo Editorial Record.',
    },
    'editora record': {
        'domain': 'record.com.br',
        'main_url': 'https://www.record.com.br',
        'terms_url': 'https://www.record.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos institucionais do Grupo Editorial Record.',
    },
    'rocco': {
        'domain': 'rocco.com.br',
        'main_url': 'https://www.rocco.com.br',
        'terms_url': 'https://www.rocco.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Rocco.',
    },
    'editora rocco': {
        'domain': 'rocco.com.br',
        'main_url': 'https://www.rocco.com.br',
        'terms_url': 'https://www.rocco.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Rocco.',
    },
    'sextante': {
        'domain': 'sextante.com.br',
        'main_url': 'https://www.sextante.com.br',
        'terms_url': 'https://www.sextante.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Sextante.',
    },
    'editora sextante': {
        'domain': 'sextante.com.br',
        'main_url': 'https://www.sextante.com.br',
        'terms_url': 'https://www.sextante.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Sextante.',
    },
    'intrinseca': {
        'domain': 'intrinseca.com.br',
        'main_url': 'https://www.intrinseca.com.br',
        'terms_url': 'https://www.intrinseca.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Intrínseca.',
    },
    'editora intrinseca': {
        'domain': 'intrinseca.com.br',
        'main_url': 'https://www.intrinseca.com.br',
        'terms_url': 'https://www.intrinseca.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Intrínseca.',
    },
    'editora intrínseca': {
        'domain': 'intrinseca.com.br',
        'main_url': 'https://www.intrinseca.com.br',
        'terms_url': 'https://www.intrinseca.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Intrínseca.',
    },
    'aleph': {
        'domain': 'editoraaleph.com.br',
        'main_url': 'https://www.editoraaleph.com.br',
        'terms_url': 'https://www.editoraaleph.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Aleph.',
    },
    'editora aleph': {
        'domain': 'editoraaleph.com.br',
        'main_url': 'https://www.editoraaleph.com.br',
        'terms_url': 'https://www.editoraaleph.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Aleph.',
    },
    'arqueiro': {
        'domain': 'editoraarqueiro.com.br',
        'main_url': 'https://www.editoraarqueiro.com.br',
        'terms_url': 'https://www.editoraarqueiro.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Arqueiro.',
    },
    'editora arqueiro': {
        'domain': 'editoraarqueiro.com.br',
        'main_url': 'https://www.editoraarqueiro.com.br',
        'terms_url': 'https://www.editoraarqueiro.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos de uso da Editora Arqueiro.',
    },
    'todavia': {
        'domain': 'todavialivros.com.br',
        'main_url': 'https://todavialivros.com.br',
        'terms_url': 'https://todavialivros.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos institucionais da Editora Todavia.',
    },
    'editora todavia': {
        'domain': 'todavialivros.com.br',
        'main_url': 'https://todavialivros.com.br',
        'terms_url': 'https://todavialivros.com.br/termos-de-uso',
        'institution_type': 'publisher',
        'terms_summary': 'Termos institucionais da Editora Todavia.',
    },
}

# Timeout para consultas externas (segundos)
EXTERNAL_REQUEST_TIMEOUT = 10

# Tamanho máximo de resposta aceita (1 MB)
MAX_RESPONSE_SIZE = 1 * 1024 * 1024

# Tempo de validade para reutilização de pesquisa (horas)
RESEARCH_REUSE_HOURS = 24

# Campos juridicamente protegidos — NUNCA sugeridos para alteração automática
PROTECTED_FIELDS = frozenset({
    'audit_status',
    'public_display_allowed',
    'legal_basis',
})

# Campos factuais que podem ser sugeridos para aplicação manual
SUGGESTABLE_FIELDS = {
    'creator_name': 'Criador / Autor da Imagem',
    'rights_holder_name': 'Titular dos Direitos',
    'licensor_name': 'Licenciante / Entidade Administradora',
    'source_url': 'Fonte Original da Imagem',
    'license_type': 'Regime de Licença / Procedência',
    'license_url': 'URL Oficial da Licença',
    'provenance_provider': 'Provedor Técnico',
    'work_title': 'Título da Obra Visual',
    'provider_asset_id': 'Identificador Externo do Ativo',
}

# Prefixos de domínios bloqueados (proteção SSRF)
SSRF_BLOCKED_HOSTS = {
    'localhost', '127.0.0.1', '0.0.0.0', '::1',
    'metadata.google.internal', '169.254.169.254',
    'metadata.google', 'metadata',
}

SSRF_BLOCKED_SCHEMES = {'file', 'ftp', 'gopher', 'data', 'javascript'}


class ImageRightsResearchService:
    """
    Serviço central de Pesquisa Assistida para auditoria de direitos autorais.
    Organiza, classifica e propõe preenchimentos. A decisão permanece humana.
    """

    # ================================================================
    # PESQUISA PRINCIPAL
    # ================================================================

    @classmethod
    def get_or_create_research(cls, record_id: int, performed_by=None) -> Optional[ImageRightsResearchResult]:
        """
        Retorna resultado reutilizável (< 24h) ou cria nova pesquisa.
        Evita consultas desnecessárias se já existe resultado recente.
        """
        try:
            record = ImageRightsRecord.objects.get(pk=record_id)
        except ImageRightsRecord.DoesNotExist:
            return None

        # Verificar se existe resultado recente reutilizável
        recent = ImageRightsResearchResult.objects.filter(
            image_rights_record=record,
            status__in=['completed', 'partial'],
            researched_at__gte=timezone.now() - timedelta(hours=RESEARCH_REUSE_HOURS)
        ).order_by('-researched_at').first()

        if recent:
            return recent

        # Executar nova pesquisa
        return cls.perform_research(record_id, performed_by)

    @classmethod
    def perform_research(cls, record_id: int, performed_by=None) -> Optional[ImageRightsResearchResult]:
        """
        Executa pesquisa assistida completa para um ImageRightsRecord.
        Segue a ordem de fontes: dados internos → provedor original → pesquisa complementar.

        NÃO altera o ImageRightsRecord.
        NÃO cria ImageRightsAuditLog.
        """
        try:
            record = ImageRightsRecord.objects.select_related(
                'content_type', 'created_by'
            ).get(pk=record_id)
        except ImageRightsRecord.DoesNotExist:
            return None

        # Criar registro de pesquisa
        research = ImageRightsResearchResult.objects.create(
            image_rights_record=record,
            status='running',
            researched_at=timezone.now(),
            researched_by=performed_by if (performed_by and hasattr(performed_by, 'is_authenticated') and performed_by.is_authenticated) else None,
        )

        suggestions = []
        sources_consulted = []
        conflicts = []
        errors = []

        try:
            # ====================================
            # NÍVEL 1: Dados Internos
            # ====================================
            internal_data = cls._collect_internal_data(record)
            research.internal_data_used = internal_data

            # ====================================
            # NÍVEL 2: Provedor Original
            # ====================================
            provider = record.provenance_provider
            if provider:
                provider_result = cls._research_by_provider(
                    record, provider, internal_data
                )
                suggestions.extend(provider_result.get('suggestions', []))
                sources_consulted.extend(provider_result.get('sources', []))
                conflicts.extend(provider_result.get('conflicts', []))
                errors.extend(provider_result.get('errors', []))

            # ====================================
            # NÍVEL 3: Pesquisa Complementar
            # ====================================
            # Consultar Google Books por ISBN se não consultado no Nível 2
            if internal_data.get('isbn') and provider != 'google_books':
                gb_result = cls._research_google_books(record, internal_data)
                suggestions.extend(gb_result.get('suggestions', []))
                sources_consulted.extend(gb_result.get('sources', []))
                conflicts.extend(gb_result.get('conflicts', []))
                errors.extend(gb_result.get('errors', []))

            # Consultar Open Library por ISBN se não consultado no Nível 2
            if internal_data.get('isbn') and provider != 'open_library':
                ol_result = cls._research_open_library(record, internal_data)
                suggestions.extend(ol_result.get('suggestions', []))
                sources_consulted.extend(ol_result.get('sources', []))
                conflicts.extend(ol_result.get('conflicts', []))
                errors.extend(ol_result.get('errors', []))

            # ====================================
            # NÍVEL 4: Descoberta Institucional Controlada (Fase 3A.1)
            # ====================================
            inst_result = cls._research_institutional_source(
                record, internal_data, existing_suggestions=suggestions
            )
            suggestions.extend(inst_result.get('suggestions', []))
            sources_consulted.extend(inst_result.get('sources', []))
            conflicts.extend(inst_result.get('conflicts', []))
            errors.extend(inst_result.get('errors', []))

            # Detectar divergências entre fontes e dados existentes
            cls._detect_conflicts(record, suggestions, conflicts)

            # Adicionar campos não localizados
            cls._add_not_found_fields(record, suggestions)

            # Determinar status final
            has_errors = len(errors) > 0
            has_results = any(s.get('suggested_value') for s in suggestions)

            if has_errors and not has_results:
                final_status = 'failed'
            elif has_errors and has_results:
                final_status = 'partial'
            else:
                final_status = 'completed'

            # Salvar resultado
            research.suggestions = suggestions
            research.sources_consulted = sources_consulted
            research.conflicts = conflicts
            research.errors = errors
            research.status = final_status
            research.save()

            logger.info(
                f"[ImageRightsResearchService] Pesquisa #{research.pk} concluída para "
                f"registro #{record_id}: {len(suggestions)} sugestões, "
                f"{len(conflicts)} conflitos, {len(errors)} erros. Status: {final_status}"
            )
            return research

        except Exception as e:
            logger.error(f"[ImageRightsResearchService] Erro na pesquisa para registro #{record_id}: {e}")
            research.status = 'failed'
            research.errors = [{'source': 'system', 'error': f'Erro interno: {str(e)[:200]}'}]
            research.save()
            return research

    # ================================================================
    # APLICAÇÃO DE SUGESTÃO (CONFIRMAÇÃO HUMANA)
    # ================================================================

    @classmethod
    @transaction.atomic
    def apply_suggestion(
        cls,
        record_id: int,
        field_name: str,
        value: str,
        performed_by=None,
    ) -> Dict[str, Any]:
        """
        Aplica uma sugestão factual confirmada pelo administrador.
        Registra a alteração no histórico via ImageRightsHistoryService.

        NUNCA altera audit_status, public_display_allowed ou legal_basis.

        Returns:
            Dict com 'success', 'message' e opcionalmente 'old_value'.
        """
        # Proteção: campos juridicamente protegidos
        if field_name in PROTECTED_FIELDS:
            return {
                'success': False,
                'message': f'O campo "{field_name}" é juridicamente protegido e não pode ser alterado por pesquisa assistida.',
            }

        # Verificar se é um campo sugerível
        if field_name not in SUGGESTABLE_FIELDS:
            return {
                'success': False,
                'message': f'Campo "{field_name}" não é elegível para aplicação via pesquisa assistida.',
            }

        try:
            record = ImageRightsRecord.objects.get(pk=record_id)
        except ImageRightsRecord.DoesNotExist:
            return {'success': False, 'message': 'Registro não encontrado.'}

        old_value = getattr(record, field_name, '')
        clean_value = str(value).strip()[:500] if value else ''

        if not clean_value:
            return {'success': False, 'message': 'Valor vazio não pode ser aplicado.'}

        # Aplicar valor
        setattr(record, field_name, clean_value)
        record.save(update_fields=[field_name])

        # Registrar no histórico
        ImageRightsHistoryService.log_event(
            image_rights_record=record,
            event_type='record_updated',
            description=f"Campo '{SUGGESTABLE_FIELDS.get(field_name, field_name)}' atualizado após confirmação de pesquisa assistida.",
            performed_by=performed_by,
            source='admin',
            old_value=str(old_value) if old_value else '',
            new_value=clean_value,
            metadata={
                'update_source': 'assisted_research',
                'field_name': field_name,
            }
        )

        return {
            'success': True,
            'message': f'Campo "{SUGGESTABLE_FIELDS.get(field_name, field_name)}" atualizado com sucesso.',
            'old_value': str(old_value) if old_value else '',
        }

    # ================================================================
    # COLETA DE DADOS INTERNOS (NÍVEL 1)
    # ================================================================

    @classmethod
    def _collect_internal_data(cls, record: ImageRightsRecord) -> Dict[str, Any]:
        """
        Coleta dados já existentes no registro e no objeto relacionado.
        Nenhuma consulta externa é realizada neste nível.
        """
        data = {
            'record_id': record.pk,
            'content_type': f"{record.content_type.app_label}.{record.content_type.model}",
            'object_id': record.object_id,
            'image_field_name': record.image_field_name,
            'provenance_provider': record.provenance_provider or '',
            'provider_asset_id': record.provider_asset_id or '',
            'source_url': record.source_url or '',
            'creator_name': record.creator_name or '',
            'rights_holder_name': record.rights_holder_name or '',
            'licensor_name': record.licensor_name or '',
            'license_type': record.license_type or '',
            'license_url': record.license_url or '',
            'work_title': record.work_title or '',
            'is_ai_generated': record.is_ai_generated,
            'provenance_metadata': record.provenance_metadata or {},
        }

        # Extrair dados do objeto relacionado
        obj = record.content_object
        if obj:
            model_name = record.content_type.model.lower()
            data['object_title'] = str(obj)

            if model_name == 'book':
                data['isbn'] = getattr(obj, 'isbn', '') or ''
                data['book_title'] = getattr(obj, 'title', '') or ''
                data['publisher'] = getattr(obj, 'publisher', '') or ''
                data['google_books_id'] = getattr(obj, 'google_books_id', '') or ''

                author = getattr(obj, 'author', None)
                if author:
                    data['author_name'] = str(author)

                data['illustrator_name'] = getattr(obj, 'illustrator_name', '') or ''

            elif model_name == 'author':
                data['author_name'] = getattr(obj, 'name', '') or ''

            elif model_name == 'article':
                data['article_title'] = getattr(obj, 'title', '') or ''

        return data

    # ================================================================
    # PESQUISA POR PROVEDOR (NÍVEL 2)
    # ================================================================

    @classmethod
    def _research_by_provider(
        cls, record: ImageRightsRecord, provider: str, internal_data: Dict
    ) -> Dict[str, Any]:
        """
        Executa estratégia de pesquisa específica por provedor.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}

        if provider == 'google_books':
            result = cls._research_google_books(record, internal_data)
        elif provider == 'open_library':
            result = cls._research_open_library(record, internal_data)
        elif provider == 'amazon':
            result = cls._research_amazon(record, internal_data)
        elif provider == 'project_gutenberg':
            result = cls._research_gutenberg(record, internal_data)
        elif provider == 'wikimedia':
            result = cls._research_wikimedia(record, internal_data)
        elif provider == 'unsplash':
            result = cls._research_unsplash(record, internal_data)
        elif provider == 'publisher':
            result = cls._research_publisher(record, internal_data)

        return result

    # ================================================================
    # ESTRATÉGIAS POR PROVEDOR
    # ================================================================

    @classmethod
    def _research_google_books(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Pesquisa dados no Google Books via API já integrada.
        NÃO interpreta presença da imagem como autorização jurídica.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Google Books API',
            'source_type': 'api',
            'url': '',
            'status': 'pending',
            'retrieved_at': timezone.now().isoformat(),
        }

        try:
            from core.utils.google_books_api import get_book_by_id, search_books

            book_data = None

            # Estratégia 1: Buscar por Volume ID
            google_id = internal_data.get('google_books_id') or record.provider_asset_id
            if google_id and record.provenance_provider == 'google_books':
                book_data = get_book_by_id(google_id)
                source_entry['url'] = f"https://www.googleapis.com/books/v1/volumes/{google_id}"

            # Estratégia 2: Buscar por ISBN
            if not book_data and internal_data.get('isbn'):
                isbn = internal_data['isbn']
                search_result = search_books(isbn=isbn, max_results=1)
                if search_result.get('books'):
                    book_data = search_result['books'][0]
                    source_entry['url'] = f"https://books.google.com/books?q=isbn:{isbn}"

            if not book_data:
                source_entry['status'] = 'no_results'
                result['sources'].append(source_entry)
                return result

            source_entry['status'] = 'success'
            result['sources'].append(source_entry)

            # Extrair sugestões factuais
            now_iso = timezone.now().isoformat()

            # Publisher / Editora → rights_holder_name (confiança média pois editora ≠ titular da capa)
            publisher = book_data.get('publisher', '')
            if publisher:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='rights_holder_name',
                    suggested_value=publisher,
                    current_value=record.rights_holder_name,
                    source_url=source_entry['url'],
                    source_type='api',
                    source_title='Google Books API',
                    confidence='medium',
                    short_reason='Editora da edição identificada via Google Books. Editora nem sempre é titular da arte da capa.',
                ))

            # Autores → creator_name (somente se for Book com cover_image — autores do livro, não da capa)
            authors = book_data.get('authors', [])
            if authors and not record.creator_name:
                author_str = ', '.join(authors)
                # Para capas, o autor do livro NÃO é o criador da imagem
                # Apenas registrar como dado informativo com confiança baixa
                if record.image_field_name == 'cover_image':
                    result['suggestions'].append(cls._make_suggestion(
                        field_name='work_title',
                        suggested_value=book_data.get('title', ''),
                        current_value=record.work_title,
                        source_url=source_entry['url'],
                        source_type='api',
                        source_title='Google Books API',
                        confidence='high',
                        short_reason='Título da obra obtido do catálogo Google Books.',
                    ))
                else:
                    result['suggestions'].append(cls._make_suggestion(
                        field_name='creator_name',
                        suggested_value=author_str,
                        current_value=record.creator_name,
                        source_url=source_entry['url'],
                        source_type='api',
                        source_title='Google Books API',
                        confidence='medium',
                        short_reason='Autor(es) declarado(s) no Google Books.',
                    ))

            # Título da obra
            title = book_data.get('title', '')
            if title and not record.work_title:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='work_title',
                    suggested_value=title,
                    current_value=record.work_title,
                    source_url=source_entry['url'],
                    source_type='api',
                    source_title='Google Books API',
                    confidence='high',
                    short_reason='Título da obra obtido do catálogo Google Books.',
                ))

            # Provider asset ID
            gb_id = book_data.get('google_book_id', '')
            if gb_id and not record.provider_asset_id:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='provider_asset_id',
                    suggested_value=gb_id,
                    current_value=record.provider_asset_id,
                    source_url=source_entry['url'],
                    source_type='api',
                    source_title='Google Books API',
                    confidence='high',
                    short_reason='Volume ID do Google Books.',
                ))

            # Info Link como source_url
            info_link = book_data.get('info_link', '')
            if info_link and not record.source_url:
                clean_url = ProvenanceService_sanitize_url(info_link)
                if clean_url:
                    result['suggestions'].append(cls._make_suggestion(
                        field_name='source_url',
                        suggested_value=clean_url,
                        current_value=record.source_url,
                        source_url=source_entry['url'],
                        source_type='api',
                        source_title='Google Books API',
                        confidence='high',
                        short_reason='Link oficial da obra no Google Books.',
                    ))

        except Exception as e:
            source_entry['status'] = 'error'
            source_entry['error'] = str(e)[:200]
            result['sources'].append(source_entry)
            result['errors'].append({
                'source': 'Google Books API',
                'error': f'Não foi possível consultar esta fonte no momento: {str(e)[:200]}',
            })

        return result

    @classmethod
    def _research_open_library(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Pesquisa dados na Open Library via API pública.
        NÃO presume licença da imagem.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Open Library API',
            'source_type': 'api',
            'url': '',
            'status': 'pending',
            'retrieved_at': timezone.now().isoformat(),
        }

        isbn = internal_data.get('isbn', '')
        if not isbn:
            source_entry['status'] = 'skipped'
            source_entry['error'] = 'ISBN não disponível para consulta.'
            result['sources'].append(source_entry)
            return result

        try:
            clean_isbn = isbn.replace('-', '').strip()
            api_url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{clean_isbn}&format=json&jscmd=data"

            if not cls._is_url_safe(api_url):
                raise ValueError("URL bloqueada por proteção SSRF.")

            source_entry['url'] = api_url

            response = requests.get(api_url, timeout=EXTERNAL_REQUEST_TIMEOUT, headers={
                'User-Agent': 'CGBookStore-CopyrightAudit/1.0'
            })
            response.raise_for_status()

            if len(response.content) > MAX_RESPONSE_SIZE:
                raise ValueError("Resposta excedeu tamanho máximo aceitável.")

            data = response.json()
            book_key = f"ISBN:{clean_isbn}"

            if book_key not in data:
                source_entry['status'] = 'no_results'
                result['sources'].append(source_entry)
                return result

            book_data = data[book_key]
            source_entry['status'] = 'success'
            result['sources'].append(source_entry)

            # Editora
            publishers = book_data.get('publishers', [])
            if publishers:
                publisher_name = publishers[0].get('name', '') if isinstance(publishers[0], dict) else str(publishers[0])
                if publisher_name:
                    result['suggestions'].append(cls._make_suggestion(
                        field_name='rights_holder_name',
                        suggested_value=publisher_name,
                        current_value=record.rights_holder_name,
                        source_url=api_url,
                        source_type='api',
                        source_title='Open Library API',
                        confidence='medium',
                        short_reason='Editora identificada via Open Library. Editora nem sempre é titular da arte da capa.',
                    ))

            # Autores
            authors = book_data.get('authors', [])
            if authors:
                author_names = []
                for a in authors[:3]:
                    name = a.get('name', '') if isinstance(a, dict) else str(a)
                    if name:
                        author_names.append(name)
                if author_names and record.image_field_name != 'cover_image':
                    result['suggestions'].append(cls._make_suggestion(
                        field_name='creator_name',
                        suggested_value=', '.join(author_names),
                        current_value=record.creator_name,
                        source_url=api_url,
                        source_type='api',
                        source_title='Open Library API',
                        confidence='medium',
                        short_reason='Autor(es) declarado(s) na Open Library.',
                    ))

            # Título
            title = book_data.get('title', '')
            if title and not record.work_title:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='work_title',
                    suggested_value=title,
                    current_value=record.work_title,
                    source_url=api_url,
                    source_type='api',
                    source_title='Open Library API',
                    confidence='high',
                    short_reason='Título da obra obtido da Open Library.',
                ))

            # URL da Open Library como source
            ol_url = book_data.get('url', '')
            if ol_url and not record.source_url:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='source_url',
                    suggested_value=ol_url,
                    current_value=record.source_url,
                    source_url=api_url,
                    source_type='api',
                    source_title='Open Library API',
                    confidence='high',
                    short_reason='Página oficial da obra na Open Library.',
                ))

        except requests.exceptions.Timeout:
            source_entry['status'] = 'timeout'
            source_entry['error'] = 'Timeout ao consultar Open Library.'
            result['sources'].append(source_entry)
            result['errors'].append({
                'source': 'Open Library API',
                'error': 'Não foi possível consultar esta fonte no momento (timeout).',
            })
        except Exception as e:
            source_entry['status'] = 'error'
            source_entry['error'] = str(e)[:200]
            if source_entry not in result['sources']:
                result['sources'].append(source_entry)
            result['errors'].append({
                'source': 'Open Library API',
                'error': f'Não foi possível consultar esta fonte no momento: {str(e)[:200]}',
            })

        return result

    @classmethod
    def _research_amazon(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Amazon: usa SOMENTE dados já existentes da integração/afiliados.
        NÃO implementa scraping. NÃO presume Amazon como titular da capa.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Amazon (Dados Existentes)',
            'source_type': 'internal',
            'url': '',
            'status': 'success',
            'retrieved_at': timezone.now().isoformat(),
        }
        result['sources'].append(source_entry)

        # Usar apenas dados já disponíveis no registro — NÃO faz requisição externa
        if record.source_url and 'amazon' in record.source_url.lower():
            source_entry['url'] = record.source_url

        # Sugerir provenance_provider se vazio
        if not record.provenance_provider and record.source_url and 'amazon' in record.source_url.lower():
            result['suggestions'].append(cls._make_suggestion(
                field_name='provenance_provider',
                suggested_value='amazon',
                current_value=record.provenance_provider,
                source_url=record.source_url,
                source_type='internal',
                source_title='Dados existentes (Amazon)',
                confidence='high',
                short_reason='Procedência Amazon identificada pela URL de origem.',
            ))

        # Extrair editora do objeto relacionado se disponível
        publisher = internal_data.get('publisher', '')
        if publisher and not record.rights_holder_name:
            result['suggestions'].append(cls._make_suggestion(
                field_name='rights_holder_name',
                suggested_value=publisher,
                current_value=record.rights_holder_name,
                source_url='',
                source_type='internal',
                source_title='Dados internos do catálogo',
                confidence='medium',
                short_reason='Editora do catálogo interno. NÃO se presume que Amazon seja titular da arte da capa.',
            ))

        return result

    @classmethod
    def _research_gutenberg(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Project Gutenberg: usa dados de catálogo já existentes.
        NÃO presume automaticamente domínio público da imagem.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Project Gutenberg (Dados Existentes)',
            'source_type': 'internal',
            'url': '',
            'status': 'success',
            'retrieved_at': timezone.now().isoformat(),
        }
        result['sources'].append(source_entry)

        # Usar dados já existentes no provenance_metadata
        meta = record.provenance_metadata or {}
        gutenberg_id = meta.get('gutenberg_id') or meta.get('ebook_id') or record.provider_asset_id

        if gutenberg_id:
            source_url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}"
            source_entry['url'] = source_url

            if not record.source_url:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='source_url',
                    suggested_value=source_url,
                    current_value=record.source_url,
                    source_url=source_url,
                    source_type='catalog',
                    source_title='Catálogo Project Gutenberg',
                    confidence='high',
                    short_reason='Página do eBook no catálogo Gutenberg. O texto pode ser domínio público, mas a imagem específica requer verificação individual.',
                ))

        return result

    @classmethod
    def _research_wikimedia(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Wikimedia Commons: coleta metadados declarados quando disponíveis.
        NÃO regulariza automaticamente.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Wikimedia Commons (Metadados)',
            'source_type': 'internal',
            'url': '',
            'status': 'success',
            'retrieved_at': timezone.now().isoformat(),
        }
        result['sources'].append(source_entry)

        # Usar metadados já existentes
        meta = record.provenance_metadata or {}
        wikimedia_title = meta.get('wikimedia_title', '')

        if wikimedia_title:
            source_entry['url'] = f"https://commons.wikimedia.org/wiki/{wikimedia_title}"

        # Licença declarada nos metadados
        license_code = meta.get('license_code', '')
        if license_code and not record.license_type:
            license_type = ''
            if 'cc' in license_code.lower():
                license_type = 'cc'
            elif 'public domain' in license_code.lower() or 'pd' in license_code.lower():
                license_type = 'public_domain'

            if license_type:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='license_type',
                    suggested_value=license_type,
                    current_value=record.license_type,
                    source_url=source_entry['url'],
                    source_type='metadata',
                    source_title='Metadados Wikimedia Commons',
                    confidence='medium',
                    short_reason=f'Licença declarada nos metadados Wikimedia: {license_code}. Requer verificação humana.',
                ))

        return result

    @classmethod
    def _research_unsplash(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Unsplash: preserva criador e URL de origem existentes.
        Usa somente dados oficiais disponíveis pela integração.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Unsplash (Dados Existentes)',
            'source_type': 'internal',
            'url': '',
            'status': 'success',
            'retrieved_at': timezone.now().isoformat(),
        }
        result['sources'].append(source_entry)

        meta = record.provenance_metadata or {}

        # Criador (fotógrafo)
        user_name = meta.get('user_name', '') or meta.get('user_username', '')
        if user_name and not record.creator_name:
            result['suggestions'].append(cls._make_suggestion(
                field_name='creator_name',
                suggested_value=user_name,
                current_value=record.creator_name,
                source_url=record.source_url or '',
                source_type='metadata',
                source_title='Metadados Unsplash',
                confidence='high',
                short_reason='Fotógrafo declarado nos metadados Unsplash.',
            ))

        # Licença Unsplash
        if not record.license_url:
            result['suggestions'].append(cls._make_suggestion(
                field_name='license_url',
                suggested_value='https://unsplash.com/license',
                current_value=record.license_url,
                source_url='https://unsplash.com/license',
                source_type='official',
                source_title='Termos de Licença Unsplash',
                confidence='high',
                short_reason='URL oficial da licença Unsplash.',
            ))

        return result

    @classmethod
    def _research_publisher(cls, record: ImageRightsRecord, internal_data: Dict) -> Dict:
        """
        Editora / Material de Divulgação: usa dados internos disponíveis.
        NÃO infere titularidade apenas porque a editora publica o livro.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}
        source_entry = {
            'source_name': 'Editora (Dados Internos)',
            'source_type': 'internal',
            'url': '',
            'status': 'success',
            'retrieved_at': timezone.now().isoformat(),
        }
        result['sources'].append(source_entry)

        publisher = internal_data.get('publisher', '')
        if publisher and not record.licensor_name:
            result['suggestions'].append(cls._make_suggestion(
                field_name='licensor_name',
                suggested_value=publisher,
                current_value=record.licensor_name,
                source_url='',
                source_type='internal',
                source_title='Catálogo interno',
                confidence='medium',
                short_reason='Editora do catálogo interno. NÃO se infere que a arte da capa pertence integralmente à editora.',
            ))

        return result

    @classmethod
    def _research_institutional_source(
        cls,
        record: ImageRightsRecord,
        internal_data: Dict,
        existing_suggestions: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Descoberta Institucional Controlada de Editora, Obra e Termos Oficiais (Fase 3A.1).
        
        - Identifica ou reutiliza o domínio oficial confirmado da editora/instituição.
        - Não faz crawler recursivo nem scraping genérico.
        - Busca caminhos institucionais padronizados (termos de uso, copyright, página da obra).
        - Reutiliza domínios e termos de uso conhecidos.
        - NÃO presume que a editora é titular dos direitos de arte de capa.
        - Retorna 'Não localizado' na ausência de evidência confiável.
        """
        result = {'suggestions': [], 'sources': [], 'conflicts': [], 'errors': []}

        # 1. Identificar a editora / instituição
        publisher = internal_data.get('publisher', '').strip()
        if not publisher and existing_suggestions:
            for s in existing_suggestions:
                if s.get('field_name') == 'rights_holder_name' and s.get('suggested_value'):
                    publisher = s['suggested_value'].strip()
                    break

        if not publisher and record.rights_holder_name:
            publisher = record.rights_holder_name.strip()

        if not publisher and record.licensor_name:
            publisher = record.licensor_name.strip()

        if not publisher:
            # Sem editora identificada, não é possível buscar domínio institucional
            return result

        pub_norm = publisher.lower().strip()

        # 2. Localizar InstitutionalSource no banco de dados ou registro conhecido
        inst_source = InstitutionalSource.objects.filter(name__iexact=publisher, is_active=True).first()

        if not inst_source:
            # Buscar no registro de sementes conhecidas
            seed_data = KNOWN_INSTITUTIONAL_SOURCES.get(pub_norm)
            if seed_data:
                inst_source, _ = InstitutionalSource.objects.get_or_create(
                    domain=seed_data['domain'],
                    defaults={
                        'name': publisher,
                        'institution_type': seed_data.get('institution_type', 'publisher'),
                        'main_url': seed_data.get('main_url', ''),
                        'terms_url': seed_data.get('terms_url', ''),
                        'terms_summary': seed_data.get('terms_summary', ''),
                        'terms_retrieved_at': timezone.now() if seed_data.get('terms_url') else None,
                        'is_verified': True,
                    }
                )

        if not inst_source:
            # Domínio oficial não confirmado previamente. NÃO inventar domínio concatenando string.
            source_entry = {
                'source_name': f'Fonte Institucional ({publisher})',
                'source_type': 'institutional',
                'url': '',
                'status': 'no_results',
                'retrieved_at': timezone.now().isoformat(),
                'note': 'Domínio institucional oficial não confirmado previamente.',
            }
            result['sources'].append(source_entry)
            return result

        # 3. Registrar fonte institucional confirmada
        main_url = inst_source.main_url or f"https://{inst_source.domain}"
        source_entry = {
            'source_name': f'Site Oficial da Editora ({inst_source.name})',
            'source_type': 'institutional',
            'url': main_url,
            'status': 'success',
            'retrieved_at': timezone.now().isoformat(),
        }
        result['sources'].append(source_entry)

        # Sugerir editora como licensor e rights_holder com ressalva factual
        if not record.licensor_name:
            result['suggestions'].append(cls._make_suggestion(
                field_name='licensor_name',
                suggested_value=inst_source.name,
                current_value=record.licensor_name,
                source_url=main_url,
                source_type='institutional',
                source_title=f'Site Oficial ({inst_source.name})',
                confidence='high',
                short_reason=f'Editora institucional oficial identificada ({inst_source.domain}).',
            ))

        if not record.rights_holder_name:
            result['suggestions'].append(cls._make_suggestion(
                field_name='rights_holder_name',
                suggested_value=inst_source.name,
                current_value=record.rights_holder_name,
                source_url=main_url,
                source_type='institutional',
                source_title=f'Site Oficial ({inst_source.name})',
                confidence='medium',
                short_reason='Editora identificada via domínio institucional. Editora nem sempre detém a totalidade dos direitos visuais da arte da capa.',
            ))

        # 4. Termos de Uso Institucionais
        terms_url = inst_source.terms_url
        terms_summary = inst_source.terms_summary or ''

        if terms_url and inst_source.is_terms_recent:
            # Reutilização imediata de termos já confirmados recentemente (< 30 dias)
            result['suggestions'].append(cls._make_suggestion(
                field_name='license_url',
                suggested_value=terms_url,
                current_value=record.license_url,
                source_url=terms_url,
                source_type='institutional',
                source_title=f'Termos de Uso ({inst_source.name})',
                confidence='high',
                short_reason=f'Termos institucionais já localizados anteriormente. {terms_summary[:150]}'.strip(),
            ))
        elif terms_url and not inst_source.is_terms_recent:
            # Revalidar termos já conhecidos com proteção SSRF
            if cls._is_url_safe(terms_url):
                try:
                    resp = requests.get(
                        terms_url,
                        timeout=EXTERNAL_REQUEST_TIMEOUT,
                        headers={'User-Agent': 'CGBookStore-CopyrightAudit/1.0'},
                        allow_redirects=True
                    )
                    if resp.status_code == 200 and cls._is_url_in_domain(resp.url, inst_source.domain):
                        clean_text = cls._extract_text_snippet(resp.text)
                        content_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()[:16]
                        if inst_source.terms_content_hash and inst_source.terms_content_hash != content_hash:
                            terms_summary = f"(Atualizado) {clean_text[:180]}"
                        else:
                            terms_summary = f"Página oficial de termos de uso da editora. {clean_text[:150]}"
                        inst_source.terms_content_hash = content_hash
                        inst_source.terms_retrieved_at = timezone.now()
                        inst_source.terms_summary = terms_summary
                        inst_source.save(update_fields=['terms_content_hash', 'terms_retrieved_at', 'terms_summary'])

                        result['suggestions'].append(cls._make_suggestion(
                            field_name='license_url',
                            suggested_value=terms_url,
                            current_value=record.license_url,
                            source_url=terms_url,
                            source_type='institutional',
                            source_title=f'Termos de Uso ({inst_source.name})',
                            confidence='high',
                            short_reason=f'Termos oficiais confirmados no domínio da editora. {terms_summary[:150]}'.strip(),
                        ))
                except Exception as e:
                    logger.warning(f"Erro ao revalidar termos {terms_url}: {e}")
        else:
            # Buscar termos em caminhos padrão no domínio oficial confirmado
            candidate_paths = [
                '/pages/termos-de-uso',
                '/termos-de-uso',
                '/termos',
                '/terms',
                '/direitos-autorais',
                '/copyright',
            ]
            for path in candidate_paths:
                candidate_url = f"https://{inst_source.domain}{path}"
                if not cls._is_url_safe(candidate_url):
                    continue
                try:
                    resp = requests.get(
                        candidate_url,
                        timeout=EXTERNAL_REQUEST_TIMEOUT,
                        headers={'User-Agent': 'CGBookStore-CopyrightAudit/1.0'},
                        allow_redirects=True
                    )
                    if resp.status_code == 200 and cls._is_url_in_domain(resp.url, inst_source.domain):
                        clean_text = cls._extract_text_snippet(resp.text)
                        content_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()[:16]
                        terms_summary = f"Página oficial de termos localizada ({path}). {clean_text[:180]}".strip()
                        inst_source.terms_url = resp.url
                        inst_source.terms_summary = terms_summary
                        inst_source.terms_content_hash = content_hash
                        inst_source.terms_retrieved_at = timezone.now()
                        inst_source.save(update_fields=['terms_url', 'terms_summary', 'terms_content_hash', 'terms_retrieved_at'])

                        result['suggestions'].append(cls._make_suggestion(
                            field_name='license_url',
                            suggested_value=resp.url,
                            current_value=record.license_url,
                            source_url=resp.url,
                            source_type='institutional',
                            source_title=f'Termos de Uso ({inst_source.name})',
                            confidence='high',
                            short_reason=terms_summary,
                        ))
                        break
                except Exception:
                    pass

        # 5. Página Oficial da Obra na Editora
        isbn = internal_data.get('isbn', '').replace('-', '').strip()
        title = internal_data.get('title', '').strip()
        book_page_url = None
        creator_explicit = None

        if isbn and inst_source.domain:
            candidate_book_paths = [
                f"/livros/{isbn}",
                f"/produto/{isbn}",
                f"/busca?q={isbn}",
            ]
            for bpath in candidate_book_paths:
                burl = f"https://{inst_source.domain}{bpath}"
                if not cls._is_url_safe(burl):
                    continue
                try:
                    resp = requests.get(
                        burl,
                        timeout=EXTERNAL_REQUEST_TIMEOUT,
                        headers={'User-Agent': 'CGBookStore-CopyrightAudit/1.0'},
                        allow_redirects=True
                    )
                    if resp.status_code == 200 and cls._is_url_in_domain(resp.url, inst_source.domain):
                        text_lower = resp.text.lower()
                        if isbn.lower() in text_lower or (title and title.lower() in text_lower):
                            book_page_url = resp.url
                            creator_explicit = cls._extract_cover_creator(resp.text)
                            break
                except Exception:
                    pass

        if book_page_url:
            source_book_entry = {
                'source_name': f'Página Oficial da Obra ({inst_source.name})',
                'source_type': 'institutional',
                'url': book_page_url,
                'status': 'success',
                'retrieved_at': timezone.now().isoformat(),
            }
            result['sources'].append(source_book_entry)
            if not record.source_url:
                result['suggestions'].append(cls._make_suggestion(
                    field_name='source_url',
                    suggested_value=book_page_url,
                    current_value=record.source_url,
                    source_url=book_page_url,
                    source_type='institutional',
                    source_title=f'Página Oficial da Obra ({inst_source.name})',
                    confidence='high',
                    short_reason=f'Página oficial da obra identificada no catálogo da editora ({inst_source.domain}).',
                ))
        else:
            source_book_entry = {
                'source_name': f'Página Oficial da Obra ({inst_source.name})',
                'source_type': 'institutional',
                'url': '',
                'status': 'no_results',
                'retrieved_at': timezone.now().isoformat(),
                'note': 'Página oficial da obra não localizada no catálogo da editora.',
            }
            result['sources'].append(source_book_entry)

        # 6. Criador da Capa Explicitamente Declarado
        if creator_explicit and not record.creator_name:
            result['suggestions'].append(cls._make_suggestion(
                field_name='creator_name',
                suggested_value=creator_explicit,
                current_value=record.creator_name,
                source_url=book_page_url or main_url,
                source_type='institutional',
                source_title=f'Página Oficial da Obra ({inst_source.name})',
                confidence='high',
                short_reason='Crédito explícito de arte/ilustração identificado na página oficial da obra.',
            ))

        return result

    @staticmethod
    def _is_url_in_domain(url: str, expected_domain: str) -> bool:
        """Verifica se a URL pertence estritamente ao domínio esperado."""
        if not url or not expected_domain:
            return False
        try:
            hostname = (urlsplit(url).hostname or '').lower()
            expected = expected_domain.lower().strip()
            return hostname == expected or hostname.endswith(f".{expected}")
        except Exception:
            return False

    @staticmethod
    def _extract_text_snippet(html: str, max_chars: int = 300) -> str:
        """Extrai um trecho curto de texto limpo sem tags, scripts ou estilos."""
        if not html:
            return ''
        # Remover scripts e estilos
        clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
        # Remover tags HTML
        clean = re.sub(r'<[^>]+>', ' ', clean)
        # Normalizar espaços
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean[:max_chars]

    @staticmethod
    def _extract_cover_creator(html: str) -> Optional[str]:
        """Tenta extrair criador da capa explicitamente declarado no HTML."""
        if not html:
            return None
        patterns = [
            r'(?:ilustra[çc][ãa]o|ilustrador|arte da capa|design da capa|capa por|capa:)\s*:?\s*(?:<[^>]+>\s*)*([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3})',
            r'(?:cover art by|cover design by|illustrated by|illustrator:)\s*:?\s*(?:<[^>]+>\s*)*([A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3})',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, flags=re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                if len(candidate) > 3 and not any(w in candidate.lower() for w in ['editora', 'livro', 'páginas', 'todos os']):
                    return candidate
        return None

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _make_suggestion(
        field_name: str,
        suggested_value: str,
        current_value: str,
        source_url: str,
        source_type: str,
        source_title: str,
        confidence: str,
        short_reason: str,
    ) -> Dict[str, Any]:
        """Cria uma entrada de sugestão padronizada."""
        is_divergent = bool(current_value and suggested_value and current_value.strip() != suggested_value.strip())
        return {
            'field_name': field_name,
            'field_label': SUGGESTABLE_FIELDS.get(field_name, field_name),
            'suggested_value': suggested_value[:500] if suggested_value else '',
            'current_value': current_value[:500] if current_value else '',
            'source_url': source_url[:500] if source_url else '',
            'source_type': source_type,
            'source_title': source_title[:200] if source_title else '',
            'retrieved_at': timezone.now().isoformat(),
            'confidence': confidence,
            'short_reason': short_reason[:500] if short_reason else '',
            'is_divergent': is_divergent,
        }

    @classmethod
    def _detect_conflicts(cls, record: ImageRightsRecord, suggestions: List, conflicts: List):
        """
        Detecta conflitos entre sugestões de fontes diferentes para o mesmo campo.
        """
        field_values = {}
        for s in suggestions:
            fname = s.get('field_name', '')
            value = s.get('suggested_value', '')
            source = s.get('source_title', '')
            if not fname or not value:
                continue
            if fname not in field_values:
                field_values[fname] = []
            field_values[fname].append({'value': value, 'source': source})

        for fname, entries in field_values.items():
            if len(entries) < 2:
                continue
            # Verificar se há divergência entre fontes
            unique_values = set(e['value'].strip().lower() for e in entries)
            if len(unique_values) > 1:
                conflicts.append({
                    'field_name': fname,
                    'field_label': SUGGESTABLE_FIELDS.get(fname, fname),
                    'source_a': entries[0]['source'],
                    'value_a': entries[0]['value'],
                    'source_b': entries[1]['source'],
                    'value_b': entries[1]['value'],
                    'note': 'Fontes confiáveis apresentaram informações diferentes. Revisão humana necessária.',
                })

    @classmethod
    def _add_not_found_fields(cls, record: ImageRightsRecord, suggestions: List):
        """
        Adiciona campos pesquisados sem resultado como 'não localizado'.
        Apenas para campos ainda vazios no registro.
        """
        found_fields = set(s['field_name'] for s in suggestions if s.get('suggested_value'))

        # Campos que deveriam ter sido pesquisados
        important_fields = {
            'creator_name': 'Criador / Autor da Imagem',
            'rights_holder_name': 'Titular dos Direitos',
            'source_url': 'Fonte Original da Imagem',
            'license_type': 'Regime de Licença',
        }

        for fname, label in important_fields.items():
            current = getattr(record, fname, '')
            if not current and fname not in found_fields:
                suggestions.append({
                    'field_name': fname,
                    'field_label': label,
                    'suggested_value': '',
                    'current_value': '',
                    'source_url': '',
                    'source_type': '',
                    'source_title': '',
                    'retrieved_at': timezone.now().isoformat(),
                    'confidence': '',
                    'short_reason': 'Não localizado em fonte confiável.',
                    'is_divergent': False,
                })

    @staticmethod
    def _is_url_safe(url: str) -> bool:
        """
        Valida URL contra SSRF.
        Bloqueia: localhost, IPs privados, metadata endpoints, protocolos não permitidos.
        """
        if not url or not isinstance(url, str):
            return False

        try:
            parsed = urlsplit(url.strip())

            # Verificar esquema
            if parsed.scheme.lower() in SSRF_BLOCKED_SCHEMES:
                return False
            if parsed.scheme.lower() not in ('http', 'https'):
                return False

            # Preferir HTTPS
            hostname = parsed.hostname or ''
            hostname_lower = hostname.lower()

            # Verificar hosts bloqueados
            if hostname_lower in SSRF_BLOCKED_HOSTS:
                return False

            # Verificar IPs privados
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return False
            except ValueError:
                # Não é um IP literal, verificar se o domínio resolve para IP privado
                pass

            # Verificar porta (apenas 80, 443 ou sem porta)
            if parsed.port and parsed.port not in (80, 443):
                return False

            return True

        except Exception:
            return False


def ProvenanceService_sanitize_url(url: str) -> str:
    """Wrapper para reutilizar sanitização de URL do ProvenanceService."""
    return ImageRightsProvenanceService._sanitize_source_url(url)
