"""
SessionService — Gerencia o ciclo de vida de AnalyticsSession.

Responsabilidade:
- Criar sessões novas quando o visitante chega
- Atualizar last_activity_at e exit_page a cada evento
- Encerrar sessões por timeout ou evento explícito de session_ended
- Detectar quando uma sessão existente expirou e criar uma nova

Design:
- Sem efeitos colaterais fora de AnalyticsSession
- Todas as operações de escrita são atômicas (update_fields explícito)
- Tolerante a falhas: nunca propaga exceção para o middleware
- Sem armazenamento de IP ou User-Agent bruto
"""
import logging
from typing import Optional
from django.utils import timezone

from ..models import AnalyticsSession
from ..utils import get_analytics_settings

logger = logging.getLogger(__name__)


class SessionService:
    """
    Serviço para gerenciar sessões analíticas.

    Uso típico (pelo middleware):
        session = SessionService.get_or_create(request, page_name, device_info)
        # → retorna AnalyticsSession ou None (em caso de erro)
    """

    @staticmethod
    def get_or_create(
        session_key: str,
        user=None,
        page_name: str = "",
        device_type: str = "unknown",
        browser_family: str = "",
        operating_system: str = "",
        referer_domain: str = "",
        source: str = "",
        medium: str = "",
        campaign: str = "",
    ) -> Optional[AnalyticsSession]:
        """
        Retorna a sessão ativa existente ou cria uma nova.

        Uma sessão é considerada ativa se:
        - Existe com o session_key fornecido
        - ended_at é None
        - last_activity_at está dentro do timeout configurado

        Se a sessão expirou, cria uma nova (sem deletar a antiga).

        Retorna None silenciosamente em caso de erro de banco.
        """
        try:
            cfg = get_analytics_settings()
            timeout_minutes = cfg.get("SESSION_TIMEOUT_MINUTES", 30)
            now = timezone.now()

            # Busca sessão existente não encerrada para este session_key
            existing = (
                AnalyticsSession.objects
                .filter(session_key=session_key, ended_at__isnull=True)
                .order_by("-started_at")
                .first()
            )

            if existing:
                # Verifica se ainda está dentro do timeout
                elapsed_minutes = (now - existing.last_activity_at).total_seconds() / 60
                if elapsed_minutes < timeout_minutes:
                    # Sessão ativa: atualiza last_activity_at e exit_page
                    update_fields = ["last_activity_at", "updated_at"]

                    existing.last_activity_at = now

                    # Atualiza exit_page se a página mudou
                    if page_name and existing.exit_page != page_name:
                        existing.exit_page = page_name
                        update_fields.append("exit_page")

                    # Associa usuário se acabou de autenticar
                    if user and not existing.user:
                        existing.user = user
                        existing.is_authenticated = True
                        update_fields.extend(["user", "is_authenticated"])

                    existing.save(update_fields=update_fields)
                    return existing
                else:
                    # Sessão expirada: encerra e cria nova
                    SessionService._close_session(existing, now)

            # Cria nova sessão
            session = AnalyticsSession.objects.create(
                session_key=session_key,
                user=user,
                is_authenticated=bool(user),
                started_at=now,
                last_activity_at=now,
                entry_page=page_name,
                exit_page=page_name,
                device_type=device_type,
                browser_family=browser_family,
                operating_system=operating_system,
                referer_domain=referer_domain,
                source=source,
                medium=medium,
                campaign=campaign,
            )
            return session

        except Exception as exc:
            logger.error(
                "[ProductAnalytics] SessionService.get_or_create falhou: %s",
                exc,
                exc_info=True,
            )
            return None

    @staticmethod
    def close_session(session_key: str) -> bool:
        """
        Encerra explicitamente a sessão mais recente de um session_key.

        Chamado quando recebe evento session_ended ou logout.
        Retorna True se encerrou, False se não havia sessão ativa.
        """
        try:
            now = timezone.now()
            session = (
                AnalyticsSession.objects
                .filter(session_key=session_key, ended_at__isnull=True)
                .order_by("-started_at")
                .first()
            )
            if session:
                SessionService._close_session(session, now)
                return True
            return False
        except Exception as exc:
            logger.error(
                "[ProductAnalytics] SessionService.close_session falhou: %s",
                exc,
                exc_info=True,
            )
            return False

    @staticmethod
    def _close_session(session: AnalyticsSession, at=None) -> None:
        """
        Marca ended_at na sessão (uso interno).
        """
        session.ended_at = at or timezone.now()
        session.save(update_fields=["ended_at", "updated_at"])

    @staticmethod
    def get_active_session(session_key: str) -> Optional[AnalyticsSession]:
        """
        Retorna a sessão ativa atual para um session_key, sem criar nem atualizar.
        Útil para EventService vincular eventos à sessão.
        """
        try:
            cfg = get_analytics_settings()
            timeout_minutes = cfg.get("SESSION_TIMEOUT_MINUTES", 30)
            cutoff = timezone.now() - timezone.timedelta(minutes=timeout_minutes)

            return (
                AnalyticsSession.objects
                .filter(
                    session_key=session_key,
                    ended_at__isnull=True,
                    last_activity_at__gte=cutoff,
                )
                .order_by("-started_at")
                .first()
            )
        except Exception as exc:
            logger.error(
                "[ProductAnalytics] SessionService.get_active_session falhou: %s",
                exc,
                exc_info=True,
            )
            return None
