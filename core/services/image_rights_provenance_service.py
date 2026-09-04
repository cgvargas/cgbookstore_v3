from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import logging
from typing import Optional, Dict, Any
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from core.models.image_rights import ImageRightsRecord
from core.models.image_rights_audit_log import ImageRightsAuditLog
from core.services.image_rights_history_service import ImageRightsHistoryService

logger = logging.getLogger(__name__)


class ImageRightsProvenanceService:
    """
    Serviço centralizado para registro e atualização segura de proveniência técnica de ativos visuais
    provenientes de serviços, APIs, feeds e fontes externas (Google Books, Open Library, Unsplash, Wikimedia, etc.).

    DIRETRIZ CENTRAL DE GOVERNANÇA:
    - Procedência técnica NÃO é licença nem autorização de uso.
    - Registros criados por integrações externas SEMPRE nascem com audit_status='not_audited'.
    - Nenhuma proveniência infere automaticamente regularização jurídica, titularidade ou fundamento legal.
    - Idempotência: chamadas repetidas não duplicam ImageRightsRecord.
    - Proteção estrita contra sobrescrita: uma nova importação JAMAIS sobrescreve dados jurídicos ou
      decisões administrativas de registros que já foram manualmente auditados (regularized, pending, contested, restricted).
    """

    # Provedores conhecidos catalogados
    PROVIDER_GOOGLE_BOOKS = 'google_books'
    PROVIDER_OPEN_LIBRARY = 'open_library'
    PROVIDER_PROJECT_GUTENBERG = 'project_gutenberg'
    PROVIDER_UNSPLASH = 'unsplash'
    PROVIDER_WIKIMEDIA = 'wikimedia'
    PROVIDER_PUBLISHER = 'publisher'
    PROVIDER_AMAZON = 'amazon'
    PROVIDER_INTERNAL_AI = 'internal_ai'
    PROVIDER_OTHER = 'other'

    # Semântica Oficial de `provider_asset_id` por Integração:
    # - google_books: Volume ID do Google Books (ex: 'zyTCAlFPjgYC'). Não usar ISBN quando o Volume ID estiver disponível.
    # - open_library: Work ID (ex: 'OL45804W') ou Cover ID (ex: '10528432') na Open Library.
    # - project_gutenberg: eBook ID numérico no catálogo Gutenberg (ex: '1342').
    # - unsplash: ID único da fotografia na API do Unsplash (ex: 'rDEOVtE7vOs').
    # - wikimedia: Page ID ou Título canônico do arquivo no Wikimedia Commons (ex: 'File:Machado_de_Assis_1896.jpg').
    # - publisher: Código ou SKU do catálogo promocional da editora.
    # - amazon: ASIN da obra (quando proveniente de endpoint oficial de parceiro/afiliado).

    @classmethod
    @transaction.atomic
    def register_external_provenance(
        cls,
        target_obj: Any,
        image_field_name: str,
        provider: str,
        source_url: str = '',
        creator_name: str = '',
        rights_holder_name: str = '',
        licensor_name: str = '',
        license_type: str = '',
        license_url: str = '',
        provider_asset_id: str = '',
        provenance_method: str = 'api_download',
        safe_metadata: Optional[Dict[str, Any]] = None,
        performed_by: Any = None,
        source: str = 'integration',
        is_ai_generated: bool = False,
    ) -> Optional[ImageRightsRecord]:
        """
        Registra ou atualiza a proveniência técnica de um ativo visual vinculado a um model Django.

        Args:
            target_obj: Instância do model que possui a imagem (ex: Book, Article, Author).
            image_field_name: Nome do campo da imagem no model (ex: 'cover_image', 'featured_image').
            provider: Identificador técnico do provedor/origem (ex: 'google_books', 'unsplash', 'open_library').
            source_url: URL original da imagem/página de origem na fonte externa.
            creator_name: Nome do criador/fotógrafo explicitamente fornecido pela fonte (opcional).
            rights_holder_name: Titular dos direitos declarado pela fonte (opcional).
            licensor_name: Licenciante declarado pela fonte (opcional).
            license_type: Regime de licença declarado pela fonte (ex: 'cc', 'public_domain', 'google_books').
            license_url: Link oficial da licença declarada pela fonte.
            provider_asset_id: ID do ativo no provedor externo (ex: Google Book ID, Unsplash Photo ID).
            provenance_method: Método técnico de aquisição (ex: 'api_download', 'api_reference', 'rss_sync').
            safe_metadata: Dicionário estritamente higienizado de metadados técnicos seguros (sem tokens ou PII).
            performed_by: Usuário autenticado que disparou a importação (se houver).
            source: Origem do evento ('integration', 'command', 'admin', 'service').
            is_ai_generated: Flag indicando se a imagem foi gerada por IA.

        Returns:
            Instância de ImageRightsRecord (criada ou atualizada com segurança).
        """
        if not target_obj or not target_obj.pk or not image_field_name:
            logger.warning("register_external_provenance invocado com argumentos inválidos.")
            return None

        # Higienizar e normalizar URL de origem (remover tokens, chaves temporárias e basic auth)
        clean_source_url = cls._sanitize_source_url(source_url)

        # Normalizar provedor técnico
        normalized_provider = provider.strip() if provider else ''
        if normalized_provider in ['gutenberg', 'gutendex']:
            normalized_provider = cls.PROVIDER_PROJECT_GUTENBERG
        elif not normalized_provider and clean_source_url:
            if 'gutenberg.org' in clean_source_url:
                normalized_provider = cls.PROVIDER_PROJECT_GUTENBERG
            elif 'openlibrary.org' in clean_source_url:
                normalized_provider = cls.PROVIDER_OPEN_LIBRARY
            elif 'books.google' in clean_source_url:
                normalized_provider = cls.PROVIDER_GOOGLE_BOOKS
            elif 'unsplash.com' in clean_source_url:
                normalized_provider = cls.PROVIDER_UNSPLASH
            elif 'wikimedia.org' in clean_source_url:
                normalized_provider = cls.PROVIDER_WIKIMEDIA
            else:
                normalized_provider = cls.PROVIDER_OTHER

        ct = ContentType.objects.get_for_model(target_obj)
        file_attr = getattr(target_obj, image_field_name, None)

        # Extrair metadados técnicos se o arquivo existir através da abstração de storage
        file_meta = {'checksum': '', 'width': None, 'height': None, 'size_kb': None}
        image_file_name = ''
        if file_attr and hasattr(file_attr, 'name') and file_attr.name:
            image_file_name = file_attr.name
            try:
                file_meta = ImageRightsRecord.extract_file_metadata(file_attr)
            except Exception as e:
                logger.warning(f"Não foi possível extrair metadados do arquivo {file_attr.name}: {e}")

        # Higienizar metadata de proveniência (garantir que seja dict e livre de dados sensíveis)
        cleaned_metadata = cls._sanitize_provenance_metadata(safe_metadata)

        # Buscar se já existe registro para este ativo
        record = ImageRightsRecord.objects.filter(
            content_type=ct,
            object_id=target_obj.pk,
            image_field_name=image_field_name
        ).first()

        now = timezone.now()

        if not record:
            # 1. CRIAÇÃO DE NOVO REGISTRO DE DIREITOS E PROVENIÊNCIA
            # Regra Inegociável: Sempre nasce como 'not_audited' e SEM presunção de autorização jurídica
            record = ImageRightsRecord.objects.create(
                content_type=ct,
                object_id=target_obj.pk,
                image_field_name=image_field_name,
                image_file_name=image_file_name,
                image_checksum=file_meta.get('checksum', ''),
                image_width_px=file_meta.get('width'),
                image_height_px=file_meta.get('height'),
                file_size_kb=file_meta.get('size_kb'),
                display_dimensions=f"{file_meta['width']}x{file_meta['height']}px ({file_meta['size_kb']} KB)" if file_meta.get('width') else '',
                # Procedência Técnica
                provenance_provider=normalized_provider,
                provenance_method=provenance_method,
                provenance_imported_at=now,
                provider_asset_id=str(provider_asset_id or ''),
                is_auto_imported=True,
                provenance_metadata=cleaned_metadata,
                source_url=clean_source_url or '',
                # Metadados declarados pela fonte (sem presunção jurídica)
                creator_name=creator_name or '',
                rights_holder_name=rights_holder_name or '',
                licensor_name=licensor_name or '',
                license_type=license_type or '',
                license_url=license_url or '',
                legal_basis='',  # NUNCA preencher fundamento legal automaticamente
                audit_status='not_audited',  # SEMPRE not_audited
                public_display_allowed=True,
                is_ai_generated=is_ai_generated,
                usage_notes=f"Importado automaticamente via integração [{normalized_provider}] em {now.strftime('%d/%m/%Y %H:%M')}. Procedência técnica pendente de auditoria documental.",
                created_by=performed_by if (performed_by and performed_by.is_authenticated) else None
            )

            # Registrar evento na trilha de auditoria
            ImageRightsHistoryService.log_event(
                image_rights_record=record,
                event_type='provenance_registered',
                description=f"Proveniência técnica registrada via [{normalized_provider}] ({provenance_method}). Ativo aguardando auditoria.",
                performed_by=performed_by,
                source=source,
                new_value=f"Provedor: {normalized_provider} | ID: {provider_asset_id or 'N/A'}",
                metadata={
                    'provider': normalized_provider,
                    'method': provenance_method,
                    'provider_asset_id': provider_asset_id,
                    'source_url': clean_source_url,
                }
            )

            logger.info(f"[ImageRightsProvenanceService] Novo registro de proveniência #{record.pk} criado para {target_obj} ({normalized_provider}).")
            return record

        # 2. ATUALIZAÇÃO IDEMPOTENTE DE REGISTRO EXISTENTE
        # Regra Crítica: Preservar dados auditados manualmente
        is_manually_audited = record.audit_status in ['regularized', 'pending', 'contested', 'restricted'] or bool(record.legal_basis) or bool(record.permission_document)

        update_fields = []
        conflict_detected = False
        conflict_details = []

        # Atualizar metadados técnicos do arquivo físico se mudaram
        if image_file_name and record.image_file_name != image_file_name:
            record.image_file_name = image_file_name
            update_fields.append('image_file_name')

        if file_meta.get('checksum') and record.image_checksum != file_meta['checksum']:
            record.image_checksum = file_meta['checksum']
            record.image_width_px = file_meta.get('width')
            record.image_height_px = file_meta.get('height')
            record.file_size_kb = file_meta.get('size_kb')
            if file_meta.get('width'):
                record.display_dimensions = f"{file_meta['width']}x{file_meta['height']}px ({file_meta['size_kb']} KB)"
                update_fields.append('display_dimensions')
            update_fields.extend(['image_checksum', 'image_width_px', 'image_height_px', 'file_size_kb'])

        # Atualizar proveniência técnica não conflitante
        if normalized_provider and record.provenance_provider != normalized_provider:
            if not record.provenance_provider:
                record.provenance_provider = normalized_provider
                update_fields.append('provenance_provider')
            else:
                conflict_detected = True
                conflict_details.append(f"Provedor existente [{record.provenance_provider}] != novo [{normalized_provider}]")

        if provider_asset_id and record.provider_asset_id != str(provider_asset_id):
            record.provider_asset_id = str(provider_asset_id)
            update_fields.append('provider_asset_id')

        if clean_source_url and not record.source_url:
            record.source_url = clean_source_url
            update_fields.append('source_url')

        if provenance_method and record.provenance_method != provenance_method:
            record.provenance_method = provenance_method
            update_fields.append('provenance_method')

        if cleaned_metadata:
            merged_meta = dict(record.provenance_metadata or {})
            merged_meta.update(cleaned_metadata)
            if merged_meta != record.provenance_metadata:
                record.provenance_metadata = merged_meta
                update_fields.append('provenance_metadata')

        record.provenance_imported_at = now
        update_fields.append('provenance_imported_at')

        # Se o registro NUNCA foi auditado manualmente (ainda está not_audited e sem doc/base legal),
        # podemos preencher metadados declarados da fonte que estavam vazios
        if not is_manually_audited:
            if creator_name and not record.creator_name:
                record.creator_name = creator_name
                update_fields.append('creator_name')
            if rights_holder_name and not record.rights_holder_name:
                record.rights_holder_name = rights_holder_name
                update_fields.append('rights_holder_name')
            if licensor_name and not record.licensor_name:
                record.licensor_name = licensor_name
                update_fields.append('licensor_name')
            if license_type and not record.license_type:
                record.license_type = license_type
                update_fields.append('license_type')
            if license_url and not record.license_url:
                record.license_url = license_url
                update_fields.append('license_url')
        else:
            # Detectar se a importação traz dados divergentes dos auditados pelo admin
            if creator_name and record.creator_name and record.creator_name != creator_name:
                conflict_details.append(f"Criador auditado [{record.creator_name}] mantido vs declarado [{creator_name}]")
            if license_type and record.license_type and record.license_type != license_type:
                conflict_details.append(f"Licença auditada [{record.license_type}] mantida vs declarada [{license_type}]")

        if update_fields:
            record.save(update_fields=list(set(update_fields)))

        # Trilha Histórica de Governança
        if conflict_details:
            ImageRightsHistoryService.log_event(
                image_rights_record=record,
                event_type='provenance_conflict_detected',
                description=f"Conflito de proveniência ({normalized_provider}): dados auditados foram preservados. " + " | ".join(conflict_details),
                performed_by=performed_by,
                source=source,
                metadata={'conflict_details': conflict_details, 'provider': normalized_provider}
            )
        elif update_fields:
            ImageRightsHistoryService.log_event(
                image_rights_record=record,
                event_type='provenance_updated',
                description=f"Proveniência técnica atualizada via integração [{normalized_provider}].",
                performed_by=performed_by,
                source=source,
                metadata={'updated_fields': list(set(update_fields)), 'provider': normalized_provider}
            )

        return record

    @staticmethod
    def _sanitize_source_url(url: str) -> str:
        """
        Higieniza URLs técnicas removendo tokens de autorização, chaves de API, credenciais
        em basic auth e assinaturas temporárias efêmeras (ex: AWS S3 presigned, Google storage signatures),
        mantendo a URL estável e representativa da origem.
        """
        if not url or not isinstance(url, str):
            return ''
        
        url_str = url.strip()
        if not (url_str.startswith('http://') or url_str.startswith('https://')):
            return url_str[:500]

        try:
            parts = urlsplit(url_str)
            # 1. Remover credenciais de basic auth do host/netloc (user:pass@host -> host)
            netloc = parts.netloc
            if '@' in netloc:
                netloc = netloc.split('@', 1)[1]

            # 2. Filtrar parâmetros de query sensíveis ou efêmeros
            query_params = parse_qsl(parts.query, keep_blank_values=True)
            sensitive_param_prefixes = (
                'token', 'access_token', 'auth', 'key', 'apikey', 'api_key',
                'secret', 'signature', 'sig', 'session', 'expires', 'expire',
                'x-amz-', 'x-goog-', 'awsaudit', 'nonce'
            )
            safe_params = []
            for k, v in query_params:
                k_clean = k.lower().strip()
                if any(k_clean.startswith(prefix) or k_clean == prefix for prefix in sensitive_param_prefixes):
                    continue
                safe_params.append((k, v))

            clean_query = urlencode(safe_params)
            clean_url = urlunsplit((parts.scheme, netloc, parts.path, clean_query, parts.fragment))
            return clean_url[:500]
        except Exception:
            return url_str[:500]

    @staticmethod
    def _sanitize_provenance_metadata(meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Garante que apenas campos técnicos seguros e não sensíveis sejam armazenados no JSONField.
        Remove tokens, credenciais, e-mails, headers de resposta ou payloads volumosos.
        """
        if not meta or not isinstance(meta, dict):
            return {}

        safe_dict = {}
        # Lista de chaves permitidas
        allowed_keys = {
            'volume_id', 'google_book_id', 'work_id', 'edition_id', 'cover_id',
            'gutenberg_id', 'ebook_id', 'photo_id', 'user_username', 'user_name',
            'width', 'height', 'color', 'format', 'download_location', 'source_page',
            'license_code', 'wikimedia_page_id', 'wikimedia_title', 'categories',
            'publisher_declared', 'published_date', 'isbn_10', 'isbn_13', 'subjects', 'source'
        }

        for k, v in meta.items():
            k_lower = str(k).lower()
            # Bloquear tokens, senhas, auth, headers
            if any(forbidden in k_lower for forbidden in ['token', 'secret', 'key', 'auth', 'pass', 'bearer', 'header', 'email', 'credential', 'sign']):
                continue
            if k_lower in allowed_keys or len(k_lower) < 30:
                # Truncar strings muito longas para evitar estourar limites
                if isinstance(v, str):
                    safe_dict[k] = v[:300]
                elif isinstance(v, (int, float, bool)):
                    safe_dict[k] = v
                elif isinstance(v, list) and len(v) <= 10:
                    safe_dict[k] = [str(item)[:100] for item in v if isinstance(item, (str, int, float))]

        return safe_dict
