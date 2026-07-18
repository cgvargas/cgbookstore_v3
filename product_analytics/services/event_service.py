"""
EventService — Registra e valida eventos de produto.

Responsabilidade:
- Validar event_type contra a allowlist
- Filtrar metadata para manter apenas chaves permitidas
- Criar ProductEvent vinculado à sessão ativa
- Suportar 3 modos de processamento: disabled / synchronous / celery

Design:
- Nunca armazena IP, User-Agent, termos de busca literais
- Em modo síncrono: escrita protegida em try/except isolado
  (falha no analytics não interrompe a requisição principal)
- Deduplicação de page_view: não registra se último evento da sessão
  já é um page_view para a mesma página (evita refresh spam)
"""
import logging
from typing import Optional

from ..constants import (
    ALLOWED_EVENT_TYPES,
    ALLOWED_METADATA_KEYS,
    ALLOWED_OBJECT_TYPES,
)
from ..utils import get_analytics_settings
from ..models import ProductEvent, AnalyticsSession

logger = logging.getLogger(__name__)


class EventService:
    """
    Serviço para registrar eventos de produto.

    Uso típico:
        EventService.record(
            session=session,
            user=request.user,
            event_type='page_view',
            page_name='book_detail',
            object_type='book',
            object_id=42,
        )
    """

    @staticmethod
    def record(
        event_type: str,
        session=None,
        user=None,
        page_name: str = "",
        object_type: str = "",
        object_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Registra um evento de produto.

        Retorna True se registrado com sucesso, False em qualquer falha.
        NUNCA propaga exceção — analytics não deve quebrar a requisição.
        """
        cfg = get_analytics_settings()
        mode = cfg.get("PROCESSING_MODE", "synchronous")

        if mode == "disabled":
            return False

        # Valida event_type antes de qualquer I/O
        if not EventService._is_valid_event_type(event_type):
            logger.warning(
                "[ProductAnalytics] event_type inválido ignorado: '%s'",
                event_type,
            )
            return False

        # Filtra metadata contra allowlist
        clean_metadata = EventService._filter_metadata(metadata or {})

        # Valida object_type
        if object_type and object_type not in ALLOWED_OBJECT_TYPES:
            object_type = ""
            object_id = None

        if mode == "celery":
            return EventService._record_async(
                event_type=event_type,
                session_id=session.pk if session else None,
                user_id=user.pk if user and user.is_authenticated else None,
                page_name=page_name,
                object_type=object_type,
                object_id=object_id,
                metadata=clean_metadata,
            )

        # Modo síncrono (padrão)
        return EventService._record_sync(
            event_type=event_type,
            session=session,
            user=user,
            page_name=page_name,
            object_type=object_type,
            object_id=object_id,
            metadata=clean_metadata,
        )

    @staticmethod
    def _record_sync(
        event_type: str,
        session=None,
        user=None,
        page_name: str = "",
        object_type: str = "",
        object_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """
        Grava o evento de forma síncrona, protegida contra falhas.
        Impacto esperado: < 5ms em banco local / < 15ms em PostgreSQL remoto.
        """
        try:

            # Deduplicação de page_view: evita registrar refresh da mesma página
            if event_type == "page_view" and session:
                last_event = (
                    ProductEvent.objects
                    .filter(session=session, event_type="page_view")
                    .order_by("-created_at")
                    .values("page_name")
                    .first()
                )
                if last_event and last_event["page_name"] == page_name:
                    # Mesma página que o último page_view desta sessão — ignora
                    return False

            resolved_user = None
            if user and hasattr(user, "is_authenticated") and user.is_authenticated:
                resolved_user = user

            ProductEvent.objects.create(
                session=session,
                user=resolved_user,
                event_type=event_type,
                page_name=page_name,
                object_type=object_type,
                object_id=object_id,
                metadata=metadata or {},
            )
            return True

        except Exception as exc:
            logger.error(
                "[ProductAnalytics] EventService._record_sync falhou para '%s': %s",
                event_type,
                exc,
                exc_info=True,
            )
            return False

    @staticmethod
    def _record_async(
        event_type: str,
        session_id: Optional[int],
        user_id: Optional[int],
        page_name: str,
        object_type: str,
        object_id: Optional[int],
        metadata: dict,
    ) -> bool:
        """
        Enfileira o evento via Celery para processamento assíncrono.
        Fallback síncrono se o broker não estiver disponível.
        """
        try:
            from ..tasks import record_event_task
            record_event_task.delay(
                event_type=event_type,
                session_id=session_id,
                user_id=user_id,
                page_name=page_name,
                object_type=object_type,
                object_id=object_id,
                metadata=metadata,
            )
            return True
        except Exception as exc:
            logger.warning(
                "[ProductAnalytics] Celery indisponível, fallback síncrono: %s",
                exc,
            )
            # Fallback: tenta registrar de forma síncrona
            from django.contrib.auth import get_user_model

            session = None
            if session_id:
                try:
                    session = AnalyticsSession.objects.get(pk=session_id)
                except AnalyticsSession.DoesNotExist:
                    pass

            user = None
            if user_id:
                try:
                    user = get_user_model().objects.get(pk=user_id)
                except Exception:
                    pass

            return EventService._record_sync(
                event_type=event_type,
                session=session,
                user=user,
                page_name=page_name,
                object_type=object_type,
                object_id=object_id,
                metadata=metadata,
            )

    @staticmethod
    def _is_valid_event_type(event_type: str) -> bool:
        """Verifica se o event_type está na allowlist."""
        return bool(event_type) and event_type in ALLOWED_EVENT_TYPES

    @staticmethod
    def _filter_metadata(metadata: dict) -> dict:
        """
        Retorna apenas as chaves da allowlist, com valores truncados.
        Garante LGPD: nenhum dado sensível armazenado acidentalmente.
        """
        if not isinstance(metadata, dict):
            return {}

        filtered = {}
        for key, value in metadata.items():
            if key not in ALLOWED_METADATA_KEYS:
                continue
            # Trunca strings longas para evitar abuso de armazenamento
            if isinstance(value, str):
                filtered[key] = value[:500]
            elif isinstance(value, (int, float, bool)):
                filtered[key] = value
            # Ignora outros tipos complexos (listas, dicts aninhados)
        return filtered
