"""Validação centralizada de destinos de parceiros comerciais."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import parse_qs, urlsplit, urlunsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


@dataclass(frozen=True)
class URLValidationIssue:
    """Problema encontrado durante a validação de uma URL comercial."""

    code: str
    message: str


@dataclass(frozen=True)
class URLValidationResult:
    """Resultado imutável da validação de uma URL comercial."""

    original_url: str
    normalized_url: str
    hostname: str
    issues: tuple[URLValidationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues

    def has_issue(self, code: str) -> bool:
        return any(issue.code == code for issue in self.issues)


class URLValidationService:
    """
    Política única para URLs de parceiros.

    O serviço não realiza requests externos e não segue redirecionamentos. Uma
    URL encurtada é rejeitada porque seu destino final não pode ser garantido.
    """

    DEFAULT_TRACKING_QUERY_PARAM = 'tag'
    QUERY_PARAM_PATTERN = re.compile(r'^[A-Za-z0-9_.~-]+$')
    HOST_LABEL_PATTERN = re.compile(r'^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$')

    @staticmethod
    def _normalize_hostname(hostname: str) -> str:
        if not hostname:
            return ''
        hostname = hostname.strip().rstrip('.').lower()
        try:
            return hostname.encode('idna').decode('ascii')
        except UnicodeError:
            return ''

    @classmethod
    def _is_structurally_valid_hostname(cls, hostname: str) -> bool:
        if not hostname or len(hostname) > 253:
            return False
        return all(cls.HOST_LABEL_PATTERN.fullmatch(label) for label in hostname.split('.'))

    @classmethod
    def _configured_partner_data(cls, partner) -> dict:
        config = getattr(settings, 'PARTNER_COMMERCIAL_CONFIG', {}) or {}
        partner_config = config.get(partner.slug, {}) if partner and partner.slug else {}
        return partner_config if isinstance(partner_config, dict) else {}

    @classmethod
    def get_allowed_domains(cls, partner) -> frozenset[str]:
        """Retorna a allowlist efetiva de um parceiro, normalizada e sem curingas."""
        if not partner:
            return frozenset()

        configured = cls._configured_partner_data(partner).get('allowed_domains', [])
        if isinstance(configured, str):
            configured = [configured]

        domains = {
            cls._normalize_hostname(domain)
            for domain in configured
            if isinstance(domain, str) and domain.strip()
        }

        # url_base é o fallback administrativo existente, sem introduzir campo novo.
        # Apenas o host exato é aceito: aliases precisam ser declarados explicitamente.
        if partner.url_base:
            try:
                base_host = cls._normalize_hostname(urlsplit(partner.url_base).hostname or '')
            except ValueError:
                base_host = ''
            if base_host:
                domains.add(base_host)

        return frozenset(
            domain
            for domain in domains
            if domain and cls._is_structurally_valid_hostname(domain)
        )

    @classmethod
    def get_tracking_query_param(cls, partner) -> str:
        """Obtém o nome configurado do parâmetro, sem conhecer parceiros específicos."""
        value = cls._configured_partner_data(partner).get(
            'tracking_query_param',
            cls.DEFAULT_TRACKING_QUERY_PARAM,
        )
        value = str(value or '').strip()
        return value if cls.QUERY_PARAM_PATTERN.fullmatch(value) else cls.DEFAULT_TRACKING_QUERY_PARAM

    @classmethod
    def get_shortener_domains(cls) -> frozenset[str]:
        domains: Iterable[str] = getattr(settings, 'PARTNER_SHORTENER_DOMAINS', set()) or set()
        return frozenset(
            cls._normalize_hostname(domain)
            for domain in domains
            if isinstance(domain, str) and domain.strip()
        )

    @classmethod
    def validate(cls, url: str, partner=None) -> URLValidationResult:
        """Valida uma URL e, quando informado, sua pertença ao parceiro."""
        raw_url = str(url or '')
        original_url = raw_url.strip()
        issues: list[URLValidationIssue] = []
        hostname = ''
        normalized_url = original_url

        if not original_url:
            issues.append(URLValidationIssue('missing_url', 'A URL não foi informada.'))
            return URLValidationResult(original_url, normalized_url, hostname, tuple(issues))

        if any(ord(char) < 32 or ord(char) == 127 for char in raw_url):
            issues.append(URLValidationIssue('control_characters', 'A URL contém caracteres de controle.'))

        if re.search(r'%(?:0[0-9a-f]|1[0-9a-f]|7f)', original_url, flags=re.IGNORECASE):
            issues.append(URLValidationIssue('encoded_control_characters', 'A URL contém caracteres de controle codificados.'))

        if '\\' in original_url:
            issues.append(URLValidationIssue('ambiguous_url', 'A URL contém barras invertidas não permitidas.'))

        try:
            parsed = urlsplit(original_url)
        except ValueError:
            issues.append(URLValidationIssue('malformed_url', 'A URL é malformada.'))
            return URLValidationResult(original_url, normalized_url, hostname, tuple(issues))

        if parsed.scheme.lower() != 'https':
            issues.append(URLValidationIssue('https_required', 'A URL deve utilizar HTTPS.'))

        if not parsed.netloc or not parsed.hostname:
            issues.append(URLValidationIssue('malformed_url', 'A URL não possui um host válido.'))

        if parsed.username is not None or parsed.password is not None:
            issues.append(URLValidationIssue('embedded_credentials', 'Credenciais embutidas não são permitidas.'))

        try:
            port = parsed.port
        except ValueError:
            port = None
            issues.append(URLValidationIssue('invalid_port', 'A porta informada é inválida.'))
        else:
            if port not in (None, 443):
                issues.append(URLValidationIssue('port_not_allowed', 'Somente a porta HTTPS padrão é permitida.'))

        hostname = cls._normalize_hostname(parsed.hostname or '')
        if parsed.hostname and not hostname:
            issues.append(URLValidationIssue('malformed_hostname', 'O hostname não pôde ser normalizado.'))
        elif hostname and not cls._is_structurally_valid_hostname(hostname):
            issues.append(URLValidationIssue('malformed_hostname', 'O hostname possui formato inválido.'))

        if hostname:
            try:
                ipaddress.ip_address(hostname.strip('[]'))
            except ValueError:
                pass
            else:
                issues.append(URLValidationIssue('ip_host_not_allowed', 'Endereços IP não são permitidos.'))

            if hostname in cls.get_shortener_domains():
                issues.append(URLValidationIssue('shortened_url', 'Links encurtados não são permitidos.'))

            if partner:
                allowed_domains = cls.get_allowed_domains(partner)
                if not allowed_domains or hostname not in allowed_domains:
                    issues.append(
                        URLValidationIssue(
                            'domain_not_allowed',
                            'O domínio da URL não pertence à allowlist do parceiro.',
                        )
                    )

        try:
            URLValidator(schemes=['https'])(original_url)
        except ValidationError:
            issues.append(URLValidationIssue('malformed_url', 'A URL não passou na validação estrutural.'))

        if parsed.netloc and hostname:
            normalized_netloc = hostname
            if port == 443:
                normalized_netloc = f'{hostname}:443'
            normalized_url = urlunsplit((
                parsed.scheme.lower(),
                normalized_netloc,
                parsed.path or '',
                parsed.query,
                parsed.fragment,
            ))

        # Remove códigos duplicados para produzir relatório estável.
        unique_issues = []
        seen_codes = set()
        for issue in issues:
            if issue.code not in seen_codes:
                seen_codes.add(issue.code)
                unique_issues.append(issue)

        return URLValidationResult(
            original_url=original_url,
            normalized_url=normalized_url,
            hostname=hostname,
            issues=tuple(unique_issues),
        )

    @classmethod
    def validate_or_raise(cls, url: str, partner=None) -> str:
        """Retorna a URL normalizada ou levanta ValidationError com todos os problemas."""
        result = cls.validate(url, partner=partner)
        if not result.is_valid:
            raise ValidationError({
                'url': [ValidationError(issue.message, code=issue.code) for issue in result.issues]
            })
        return result.normalized_url

    @classmethod
    def get_tracking_values(cls, url: str, partner) -> list[str]:
        """Extrai os valores de tracking presentes na URL sem modificá-la."""
        try:
            parsed = urlsplit(str(url or '').strip())
        except ValueError:
            return []
        param_name = cls.get_tracking_query_param(partner)
        return parse_qs(parsed.query, keep_blank_values=True).get(param_name, [])
