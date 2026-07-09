from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from django.db import models
from django.utils.text import slugify
from partners.models import AffiliatePartner


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

        # Normalizar slug para verificar o parceiro
        partner_slug = partner.slug or slugify(partner.nome)

        # Regras específicas para Amazon
        if 'amazon' in partner_slug:
            return AffiliateService._apply_query_param(url_original, 'tag', tracking_id)

        # Regras genéricas para outros parceiros (podem ser estendidas futuramente)
        # Por padrão, se houver um tracking_id, adicionamos como query param 'tag' ou mantemos a URL original
        return AffiliateService._apply_query_param(url_original, 'tag', tracking_id)

    @staticmethod
    def _apply_query_param(url: str, param_name: str, param_value: str) -> str:
        """
        Adiciona ou substitui um parâmetro de consulta (query param) em uma URL de forma segura.
        """
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Atualiza ou insere o parâmetro
            query_params[param_name] = [param_value]
            
            # Reconstrói a query string e a URL
            new_query = urlencode(query_params, doseq=True)
            return urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
        except Exception:
            # Fallback seguro caso ocorra erro no parse da URL
            return url

    @classmethod
    def get_partner_for_book(cls, book) -> AffiliatePartner:
        """
        Busca o parceiro comercial ativo que corresponde ao purchase_partner_name do livro.
        Faz a busca por nome exato (case-insensitive) ou slug correspondente.
        """
        partner_name = book.purchase_partner_name
        if not partner_name:
            return None

        partner_slug = slugify(partner_name)
        
        return AffiliatePartner.objects.filter(ativo=True).filter(
            models.Q(nome__iexact=partner_name) | models.Q(slug=partner_slug)
        ).first()

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
