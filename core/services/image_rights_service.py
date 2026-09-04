# core/services/image_rights_service.py
"""
Serviço para verificação de procedência de imagens, cálculo de badges de auditoria 🟢 🟡 🔴 ⚠️,
detecção de troca por Checksum (SHA-256) e mapa de conformidade corporativo por modelo.
"""

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.html import format_html

from core.models.image_rights import ImageRightsRecord


class ImageRightsAuditService:
    """
    Serviço central de auxílio e auditoria de direitos de imagens para admins e mapa de conformidade.
    """

    # Mapeamento de modelos auditáveis e seus campos visuais.
    # Lista centralizada: edite aqui para adicionar/remover modelos da auditoria.
    AUDITABLE_MODELS_CONFIG = [
        # (app_label, model_name, [campos_visuais])
        ('core', 'Book', ['cover_image']),
        ('core', 'Author', ['photo']),
        ('core', 'Video', ['thumbnail_image', 'video_file']),
        ('core', 'Banner', ['image', 'video_file']),
        ('core', 'LiteraryUniverse', ['logo', 'hero_banner_image', 'og_image']),
        ('core', 'Event', ['banner_image', 'thumbnail_image']),
        ('core', 'Section', ['banner_image', 'container_background_image']),
        ('core', 'FeaturedAuthorSettings', ['home_banner_image', 'page_banner_image']),
        ('core', 'WeeklyChronicle', ['featured_image', 'secondary_image', 'gallery_image_1', 'gallery_image_2', 'gallery_image_3']),
        ('core', 'UniverseContentItem', ['thumbnail']),
        ('core', 'UniverseBanner', ['image', 'image_mobile']),
        ('core', 'UniverseTimelineEvent', ['image']),
        ('core', 'UniverseCharacter', ['image']),
        ('core', 'UniverseCollection', ['cover_image']),
        ('news', 'Article', ['featured_image']),
        ('news', 'Quiz', ['featured_image']),
        ('new_authors', 'EmergingAuthor', ['photo']),
        ('new_authors', 'AuthorBook', ['cover_image']),
        ('new_authors', 'PublisherProfile', ['logo']),
        ('partners', 'AffiliatePartner', ['logo']),
    ]

    DEFAULT_MODEL_PURPOSES = {
        'book': ('review_debate', 'fair_use_art46'),
        'author': ('author_bio', 'fair_use_art46'),
        'video': ('review_debate', 'fair_use_art46'),
        'banner': ('institutional', 'own_production'),
        'section': ('institutional', 'own_production'),
        'featuredauthorsettings': ('institutional', 'own_production'),
        'literaryuniverse': ('adaptation_info', 'fair_use_art46'),
        'event': ('event_publicity', 'express_consent'),
        'weeklychronicle': ('review_debate', 'fair_use_art46'),
        'universecontentitem': ('adaptation_info', 'fair_use_art46'),
        'universebanner': ('adaptation_info', 'fair_use_art46'),
        'universetimelineevent': ('adaptation_info', 'fair_use_art46'),
        'universecharacter': ('adaptation_info', 'fair_use_art46'),
        'universecollection': ('adaptation_info', 'fair_use_art46'),
        'article': ('review_debate', 'fair_use_art46'),
        'quiz': ('review_debate', 'fair_use_art46'),
        'emergingauthor': ('author_bio', 'express_consent'),
        'authorbook': ('review_debate', 'express_consent'),
        'publisherprofile': ('institutional', 'express_consent'),
        'affiliatepartner': ('partner_ad', 'express_consent'),
    }

    @classmethod
    def get_auditable_models(cls):
        """
        Retorna a lista de modelos auditáveis como classes Django.
        Usa AUDITABLE_MODELS_CONFIG como fonte centralizada.
        """
        from django.apps import apps
        result = []
        for app_label, model_name, _fields in cls.AUDITABLE_MODELS_CONFIG:
            try:
                model_cls = apps.get_model(app_label, model_name)
                result.append(model_cls)
            except LookupError:
                pass
        return result

    @classmethod
    def get_image_fields_for_model(cls, model_cls):
        """
        Retorna a lista de nomes de campos visuais configurados para um dado model.
        Se não há configuração explícita, usa introspecção via _meta.
        """
        app_label = model_cls._meta.app_label
        model_name = model_cls.__name__
        for cfg_app, cfg_model, fields in cls.AUDITABLE_MODELS_CONFIG:
            if cfg_app == app_label and cfg_model == model_name:
                return fields
        # Fallback via introspecção
        return [
            f.name for f in model_cls._meta.get_fields()
            if isinstance(f, (models.ImageField, models.FileField))
        ]

    @classmethod
    def get_default_purpose_and_legal_basis(cls, model_name):
        """Retorna sugestões padrão de finalidade do uso e suporte jurídico com base no nome do modelo."""
        model_name = model_name.lower()
        return cls.DEFAULT_MODEL_PURPOSES.get(model_name, ('other', 'fair_use_art46'))

    @classmethod
    def sync_file_metadata(cls, rights_record, file_attr, performed_by=None, source='command'):
        """Sincroniza automaticamente dimensões, peso em KB e checksum do arquivo no registro e gera log de auditoria."""
        if not rights_record or not file_attr:
            return False

        from core.services.image_rights_history_service import ImageRightsHistoryService

        meta = ImageRightsRecord.extract_file_metadata(file_attr)
        updated = False
        old_checksum = rights_record.image_checksum

        if meta['checksum'] and rights_record.image_checksum != meta['checksum']:
            rights_record.image_checksum = meta['checksum']
            updated = True

        if meta['width'] and rights_record.image_width_px != meta['width']:
            rights_record.image_width_px = meta['width']
            rights_record.image_height_px = meta['height']
            updated = True

        if meta['size_kb'] and rights_record.file_size_kb != meta['size_kb']:
            rights_record.file_size_kb = meta['size_kb']
            updated = True

        if meta['width'] and meta['height']:
            dim_str = f"{meta['width']}x{meta['height']}px ({meta['size_kb']} KB)"
            if rights_record.display_dimensions != dim_str:
                rights_record.display_dimensions = dim_str
                updated = True

        if updated:
            rights_record.save()
            if old_checksum != rights_record.image_checksum:
                ImageRightsHistoryService.log_checksum_updated(
                    record=rights_record,
                    old_checksum=old_checksum,
                    new_checksum=rights_record.image_checksum,
                    performed_by=performed_by,
                    source=source
                )

        return updated

    @classmethod
    def get_field_audit_status(cls, obj, field_name):
        """
        Avalia o estado da auditoria de um determinado campo de imagem em um objeto.

        DISTINÇÃO ARQUITETURAL:
        1. Diagnóstico Técnico de Integridade: verifica a existência do arquivo, do registro
           correspondente, divergência de Checksum (SHA-256) e consistência documental.
        2. Decisão Administrativa de Governança (audit_status): estado registrado pelo administrador
           (not_audited, under_review, regularized, pending, contested, restricted).

        Retornos possíveis:
        - 'no_image': Sem arquivo enviado no campo
        - 'missing': Imagem enviada sem nenhum ImageRightsRecord associado
        - 'divergent': Checksum atual diferente do SHA-256 original cadastrado
        - 'contested': 🔴 Ativo formalmente contestado ou sob disputa
        - 'restricted': ⛔ Uso restrito ou suspenso administrativamente
        - 'not_audited': ⚪ Registro existente, porém ainda não auditado administrativamente
        - 'under_review': 🔵 Registro sob análise de conformidade
        - 'pending': 🟡 Informações incompletas ou pendência documental detectada
        - 'regularized': 🟢 Regularizado administrativamente e tecnicamente consistente
        """
        if not obj or not getattr(obj, 'pk', None):
            return 'no_image', None

        from core.services.image_rights_history_service import ImageRightsHistoryService

        file_attr = getattr(obj, field_name, None)
        if not file_attr or not hasattr(file_attr, 'name') or not file_attr.name:
            return 'no_image', None

        ct = ContentType.objects.get_for_model(obj)
        rights_record = ImageRightsRecord.objects.filter(
            content_type=ct,
            object_id=obj.pk,
            image_field_name=field_name
        ).first()

        if not rights_record:
            return 'missing', None

        # Sincronizar metadados do arquivo se necessário
        if file_attr:
            cls.sync_file_metadata(rights_record, file_attr)

        # 1. Checagem técnica de integridade: Checksum SHA-256
        if rights_record.image_checksum:
            current_checksum = ImageRightsRecord.calculate_file_checksum(file_attr)
            if current_checksum and current_checksum != rights_record.image_checksum:
                # Registrar evento na trilha de auditoria com proteção anti-duplicação
                ImageRightsHistoryService.log_integrity_divergence(
                    record=rights_record,
                    expected_checksum=rights_record.image_checksum,
                    detected_checksum=current_checksum,
                    source='system'
                )
                return 'divergent', rights_record

        # 2. Respeito às decisões administrativas restritivas / contestações e suspensão preventiva
        if not rights_record.public_display_allowed or rights_record.audit_status == 'restricted':
            return 'restricted', rights_record

        # Verificar se existe takedown ativo bloqueando o ativo
        has_blocking_takedown = rights_record.takedown_requests.filter(
            status__in=['temporarily_suspended', 'resolved_removed']
        ).exists()
        if has_blocking_takedown:
            return 'restricted', rights_record

        has_active_takedown = rights_record.takedown_requests.filter(
            status__in=['received', 'under_review', 'awaiting_information']
        ).exists()
        if rights_record.audit_status == 'contested' or has_active_takedown:
            return 'contested', rights_record

        if rights_record.audit_status == 'under_review':
            return 'under_review', rights_record

        if rights_record.audit_status == 'not_audited':
            return 'not_audited', rights_record

        # 3. Verificação de completude técnica da licença e enquadramento jurídico
        has_technical_pending = False

        if not rights_record.license_type and not rights_record.legal_basis:
            has_technical_pending = True

        # Creative Commons exige URL oficial da licença e URL da fonte
        if rights_record.license_type == 'cc' and (not rights_record.license_url or not rights_record.source_url):
            has_technical_pending = True

        # Licenciada ou Autorização Expressa exige documento anexado ou notas internas
        if rights_record.license_type == 'licensed' and not rights_record.permission_document and not rights_record.usage_notes:
            has_technical_pending = True
        if rights_record.legal_basis == 'express_consent' and not rights_record.permission_document and not rights_record.usage_notes:
            has_technical_pending = True

        # Enquadramento em Limitação Legal (Art. 46) exige finalidade e atribuição (criador/autor ou fonte)
        if rights_record.legal_basis == 'fair_use_art46':
            has_author_or_source = bool(rights_record.creator_name or rights_record.credit_name or rights_record.source_url)
            if not rights_record.usage_purpose or not has_author_or_source:
                has_technical_pending = True

        if has_technical_pending or rights_record.audit_status == 'pending':
            return 'pending', rights_record

        # Se audit_status for 'regularized' e não houver pendência técnica
        if rights_record.audit_status == 'regularized':
            return 'regularized', rights_record

        return 'pending', rights_record

    @classmethod
    def get_field_audit_badge_html(cls, obj, field_name):
        """Retorna a badge HTML formatada para exibição em formulários/listagens do admin."""
        status, record = cls.get_field_audit_status(obj, field_name)
        if status == 'no_image':
            return ''
        elif status == 'regularized':
            return format_html('<span style="background:#27ae60; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🟢 Regularizada</span>')
        elif status == 'under_review':
            return format_html('<span style="background:#2980b9; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🔵 Em Análise</span>')
        elif status == 'pending':
            return format_html('<span style="background:#f39c12; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🟡 Pendente</span>')
        elif status == 'not_audited':
            return format_html('<span style="background:#7f8c8d; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">⚪ Não Auditada</span>')
        elif status == 'contested':
            return format_html('<span style="background:#c0392b; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🔴 Contestada</span>')
        elif status == 'restricted':
            return format_html('<span style="background:#d63031; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">⛔ Uso Restrito / Suspenso</span>')
        elif status == 'divergent':
            return format_html('<span style="background:#e67e22; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">⚠️ Checksum Divergente</span>')
        else:
            return format_html('<span style="background:#c0392b; color:#fff; padding:3px 8px; border-radius:10px; font-size:0.75rem; font-weight:600;">🔴 Sem Registro</span>')

    @classmethod
    def can_display_publicly(cls, obj, field_name=None):
        """
        Verifica de forma centralizada e segura se um ativo visual pode ser exibido publicamente.
        Se obj for uma instância de ImageRightsRecord, consulta diretamente sua property.
        Se obj for um model de conteúdo, localiza o ImageRightsRecord associado e verifica can_display_publicly.
        Retorna True caso não haja restrições ou contestações impeditivas.
        """
        if not obj:
            return True

        # Se o objeto já é o ImageRightsRecord
        if isinstance(obj, ImageRightsRecord):
            return obj.can_display_publicly

        if not getattr(obj, 'pk', None) or not field_name:
            return True

        try:
            ct = ContentType.objects.get_for_model(obj)
            record = ImageRightsRecord.objects.filter(
                content_type=ct,
                object_id=obj.pk,
                image_field_name=field_name
            ).first()
            if not record:
                return True
            return record.can_display_publicly
        except Exception:
            return True

    @classmethod
    def suspend_image_asset(cls, record, request_user=None, notes=None, takedown_request=None, source='service'):
        """
        Executa a suspensão preventiva de exibição pública de forma atômica e coordenada.
        Define public_display_allowed=False e audit_status='restricted', registrando evento na trilha de auditoria.
        """
        from django.db import transaction
        from core.services.image_rights_history_service import ImageRightsHistoryService

        with transaction.atomic():
            record.public_display_allowed = False
            record.audit_status = 'restricted'
            if notes:
                record.usage_notes = f"{record.usage_notes}\n[SUSPENSÃO PREVENTIVA]: {notes}".strip()
            record.save()

            # Registrar na trilha histórica de auditoria de forma atômica
            ImageRightsHistoryService.log_suspension(
                record=record,
                performed_by=request_user,
                source=source,
                notes=notes,
                takedown_request=takedown_request
            )
            return True, "Exibição pública suspensa preventivamente."

    @classmethod
    def restore_image_asset(cls, record, request_user=None, takedown_request=None, source='service'):
        """
        Restaura a exibição pública de um ativo visual de forma atômica.
        Impede a restauração se houver qualquer contestação com status impeditivo ativo.
        Registra o evento na trilha de auditoria.
        """
        from django.db import transaction
        from core.services.image_rights_history_service import ImageRightsHistoryService

        with transaction.atomic():
            # Verificação de segurança: não permite restaurar se houver contestação suspensa ou removida
            blocking_takedowns = record.takedown_requests.filter(
                status__in=['temporarily_suspended', 'resolved_removed']
            )
            if blocking_takedowns.exists():
                count = blocking_takedowns.count()
                return False, f"Impossível restaurar exibição: existe(m) {count} contestação(ões) com suspensão preventiva ativa ou remoção definitiva vinculada(s) a este ativo."

            record.public_display_allowed = True
            # Se estava com status restrito, ajusta para under_review ou pending (não regulariza automaticamente)
            if record.audit_status == 'restricted':
                record.audit_status = 'under_review' if record.takedown_requests.filter(status='under_review').exists() else 'pending'
            record.save()

            # Registrar na trilha histórica de auditoria de forma atômica
            ImageRightsHistoryService.log_restoration(
                record=record,
                performed_by=request_user,
                source=source,
                takedown_request=takedown_request
            )
            return True, "Exibição pública restaurada com sucesso."

    @classmethod
    def resolve_takedown_atomic(cls, takedown, resolution_type, request_user=None, resolution_notes='', source='service'):
        """
        Resolve uma ocorrência de contestação/takedown de forma coordenada e atômica.
        Suporta:
        - 'keep': resolve mantendo a imagem (se não houver outra contestação impeditiva, permite restauração de public_display_allowed).
        - 'remove': resolve retirando a imagem (força public_display_allowed=False e audit_status='restricted').
        Gera eventos na trilha histórica de auditoria dentro da mesma transação.
        """
        from django.db import transaction
        from django.utils import timezone
        from core.services.image_rights_history_service import ImageRightsHistoryService

        with transaction.atomic():
            record = takedown.image_rights_record
            takedown.resolved_at = timezone.now()
            takedown.resolved_by = request_user
            if resolution_notes:
                takedown.resolution_notes = resolution_notes

            if resolution_type == 'remove':
                takedown.status = 'resolved_removed'
                takedown.save()
                if record:
                    record.public_display_allowed = False
                    record.audit_status = 'restricted'
                    record.save(update_fields=['public_display_allowed', 'audit_status'])
                    ImageRightsHistoryService.log_takedown_resolution(
                        takedown=takedown,
                        resolution_type='remove',
                        performed_by=request_user,
                        source=source,
                        notes=resolution_notes
                    )
                return True, "Contestação resolvida com RETIRADA DA IMAGEM. Exibição pública bloqueada e histórico preservado."

            elif resolution_type == 'keep':
                takedown.status = 'resolved_keep'
                takedown.save()
                if record:
                    # Verificar se há OUTRA contestação com suspensão impeditiva
                    other_blocking = record.takedown_requests.exclude(pk=takedown.pk).filter(
                        status__in=['temporarily_suspended', 'resolved_removed']
                    ).exists()
                    if other_blocking:
                        # Mantém suspenso devido à outra ocorrência pendente
                        record.public_display_allowed = False
                        record.audit_status = 'restricted'
                        record.save(update_fields=['public_display_allowed', 'audit_status'])
                        ImageRightsHistoryService.log_takedown_resolution(
                            takedown=takedown,
                            resolution_type='keep',
                            performed_by=request_user,
                            source=source,
                            notes=resolution_notes
                        )
                        return True, "Contestação resolvida mantendo uso. NOTA: O ativo visual permanece SUSPENSO porque há outra contestação impeditiva ativa associada."
                    else:
                        # Nenhuma outra ocorrência impede a exibição
                        record.public_display_allowed = True
                        if record.audit_status == 'restricted':
                            record.audit_status = 'under_review' if record.takedown_requests.filter(status='under_review').exists() else 'pending'
                        record.save(update_fields=['public_display_allowed', 'audit_status'])
                        ImageRightsHistoryService.log_takedown_resolution(
                            takedown=takedown,
                            resolution_type='keep',
                            performed_by=request_user,
                            source=source,
                            notes=resolution_notes
                        )
                return True, "Contestação resolvida com MANUTENÇÃO DA IMAGEM. Exibição pública restaurada."

            return False, "Tipo de resolução não reconhecido."

    @classmethod
    def audit_model_admin_save(cls, request, obj):
        """
        Executado no save_model dos admins principais.
        Verifica os campos de imagem e exibe avisos educativos não-bloqueantes.
        """
        if not obj or not obj.pk:
            return

        model_cls = obj.__class__

        for field in model_cls._meta.get_fields():
            if isinstance(field, (models.ImageField, models.FileField)):
                status, record = cls.get_field_audit_status(obj, field.name)
                if status == 'missing':
                    messages.warning(
                        request,
                        f"⚠️ Auditoria de Imagens: O campo '{field.verbose_name}' possui imagem enviada sem registro de procedência. Preencha na seção 'Direitos Autorais e Procedência'."
                    )
                elif status == 'divergent':
                    messages.warning(
                        request,
                        f"⚠️ Alerta Checksum: O arquivo do campo '{field.verbose_name}' foi alterado no disco. Atualize os direitos autorais deste ativo visual!"
                    )
                elif status == 'contested':
                    messages.error(
                        request,
                        f"🔴 Alerta Jurídico: O ativo visual do campo '{field.verbose_name}' está marcado como CONTESTADO. Revise a legitimidade do uso."
                    )

    @classmethod
    def get_model_compliance_stats(cls, model_cls):
        """
        Calcula as estatísticas e a taxa percentual de conformidade de mídias para um modelo específico.
        """
        ct = ContentType.objects.get_for_model(model_cls)
        image_field_names = [
            f.name for f in model_cls._meta.get_fields()
            if isinstance(f, (models.ImageField, models.FileField))
        ]

        if not image_field_names:
            return {
                'model_name': model_cls._meta.verbose_name_plural.title(),
                'total_images': 0,
                'regularized': 0,
                'under_review': 0,
                'not_audited': 0,
                'pending': 0,
                'contested': 0,
                'restricted': 0,
                'missing': 0,
                'divergent': 0,
                'rate': 100.0
            }

        total_images = 0
        regularized = 0
        under_review = 0
        not_audited = 0
        pending = 0
        contested = 0
        restricted = 0
        missing = 0
        divergent = 0

        # Iterar sobre as instâncias do modelo que possuem arquivo
        for obj in model_cls.objects.all():
            for field_name in image_field_names:
                status, record = cls.get_field_audit_status(obj, field_name)
                if status != 'no_image':
                    total_images += 1
                    if status == 'regularized':
                        regularized += 1
                    elif status == 'under_review':
                        under_review += 1
                    elif status == 'not_audited':
                        not_audited += 1
                    elif status == 'pending':
                        pending += 1
                    elif status == 'contested':
                        contested += 1
                    elif status == 'restricted':
                        restricted += 1
                    elif status == 'divergent':
                        divergent += 1
                    elif status == 'missing':
                        missing += 1

        rate = round((regularized / total_images * 100), 1) if total_images > 0 else 100.0
        return {
            'model_name': model_cls._meta.verbose_name_plural.title(),
            'total_images': total_images,
            'regularized': regularized,
            'under_review': under_review,
            'not_audited': not_audited,
            'pending': pending,
            'contested': contested,
            'restricted': restricted,
            'missing': missing,
            'divergent': divergent,
            'rate': rate
        }

