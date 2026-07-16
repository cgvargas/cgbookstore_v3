from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.db import models
from django.utils.text import slugify

from partners.models import AffiliatePartner
from partners.services.url_validation_service import URLValidationResult, URLValidationService


@dataclass(frozen=True)
class AffiliateLinkResolution:
    """Diagnóstico imutável para a futura ativação segura do redirecionamento."""

    partner: AffiliatePartner | None
    original_url: str
    generated_url: str
    validation: URLValidationResult
    partner_matches_book: bool

    @property
    def is_ready(self) -> bool:
        return bool(
            self.partner
            and self.partner.ativo
            and self.partner_matches_book
            and self.validation.is_valid
            and self.generated_url
        )


class AffiliateService:
    """
    Camada de serviço responsável pelo gerenciamento de links de afiliados
    e resolução de parceiros comerciais para livros.
    """

    @staticmethod
    def generate_link(partner: AffiliatePartner, book, url_original: str) -> str:
        """
        Recebe um parceiro comercial, um livro e a URL original de compra,
        e gera a URL final de afiliado com os parâmetros de rastreamento corretos.
        """
        if not url_original:
            return ""

        tracking_id = partner.tracking_id
        if not tracking_id:
            return url_original

        param_name = URLValidationService.get_tracking_query_param(partner)
        return AffiliateService._apply_query_param(url_original, param_name, tracking_id)

    @staticmethod
    def _apply_query_param(url: str, param_name: str, param_value: str) -> str:
        """
        Adiciona ou substitui um parâmetro de consulta (query param) em uma URL de forma segura.
        """
        if not url or not param_name or not param_value:
            return url

        try:
            parsed_url = urlsplit(url)
            query_items = [
                (name, value)
                for name, value in parse_qsl(parsed_url.query, keep_blank_values=True)
                if name != param_name
            ]
            query_items.append((param_name, param_value))
            return urlunsplit((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                urlencode(query_items, doseq=True),
                parsed_url.fragment,
            ))
        except ValueError:
            # Compatibilidade temporária: o bloqueio será ativado somente após saneamento.
            return url

    @classmethod
    def find_partner_by_name(cls, partner_name: str, active_only: bool = True) -> AffiliatePartner:
        """Resolve um parceiro por nome/slug, preservando a compatibilidade textual atual."""
        if not partner_name:
            return None

        partner_slug = slugify(partner_name)
        queryset = AffiliatePartner.objects.all()
        if active_only:
            queryset = queryset.filter(ativo=True)

        return queryset.filter(
            models.Q(nome__iexact=partner_name) | models.Q(slug=partner_slug)
        ).first()

    @classmethod
    def get_partner_for_book(cls, book) -> AffiliatePartner:
        """
        Busca o parceiro comercial ativo que corresponde ao purchase_partner_name do livro.
        Faz a busca por nome exato (case-insensitive) ou slug correspondente.
        """
        return cls.find_partner_by_name(book.purchase_partner_name, active_only=True)

    @staticmethod
    def partner_matches_book(partner: AffiliatePartner, book) -> bool:
        """Compara o parceiro resolvido com o nome legado sem consultar o banco."""
        if not partner or not book:
            return False
        book_partner_name = str(getattr(book, 'purchase_partner_name', '') or '').strip()
        if not book_partner_name:
            return False
        return (
            partner.nome.casefold() == book_partner_name.casefold()
            or partner.slug == slugify(book_partner_name)
        )

    @classmethod
    def resolve_partner_for_book(
        cls,
        book,
        requested_partner: AffiliatePartner | None = None,
        active_only: bool = True,
    ) -> AffiliatePartner | None:
        """Resolve o parceiro e rejeita, em memória, um parceiro de rota inconsistente."""
        if requested_partner is not None:
            if active_only and not requested_partner.ativo:
                return None
            return requested_partner if cls.partner_matches_book(requested_partner, book) else None
        return cls.find_partner_by_name(
            getattr(book, 'purchase_partner_name', ''),
            active_only=active_only,
        )

    @staticmethod
    def validate_partner_url(partner: AffiliatePartner, url: str) -> URLValidationResult:
        """Ponto único de validação, ainda não conectado à view de produção."""
        return URLValidationService.validate(url, partner=partner)

    @classmethod
    def inspect_link_for_book(
        cls,
        book,
        requested_partner: AffiliatePartner | None = None,
    ) -> AffiliateLinkResolution:
        """Prepara e diagnostica um link sem alterar registros nem redirecionar."""
        original_url = str(getattr(book, 'purchase_partner_url', '') or '').strip()
        partner = cls.resolve_partner_for_book(
            book,
            requested_partner=requested_partner,
            active_only=False,
        )
        matches = cls.partner_matches_book(partner, book) if partner else False
        validation = URLValidationService.validate(original_url, partner=partner)
        generated_url = ''
        if partner and partner.ativo and matches and validation.is_valid:
            generated_url = cls.generate_link(partner, book, validation.normalized_url)
        return AffiliateLinkResolution(
            partner=partner,
            original_url=original_url,
            generated_url=generated_url,
            validation=validation,
            partner_matches_book=matches,
        )

    @classmethod
    def get_link_for_book(cls, book) -> str:
        """
        Retorna a URL final de afiliado para o livro.
        Se não houver parceiro ativo correspondente ou URL original, retorna a URL original ou vazio.
        """
        url_original = book.purchase_partner_url
        if not url_original:
            return ""

        partner = cls.get_partner_for_book(book)
        if not partner:
            return url_original

        return cls.generate_link(partner, book, url_original)
