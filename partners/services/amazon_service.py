"""
Serviço centralizado para validação, extração de ASIN e normalização de URLs da Amazon Brasil.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from django.conf import settings


class AmazonURLNormalizer:
    """
    Normalizador e validador centralizado de URLs de produtos da Amazon Brasil.
    
    Padroniza URLs para o formato:
    https://www.amazon.com.br/dp/{ASIN}?tag={AMAZON_ASSOCIATE_TAG}
    """

    ALLOWED_DOMAINS = frozenset({'amazon.com.br', 'www.amazon.com.br'})

    @classmethod
    def get_associate_tag(cls) -> str:
        """Retorna a tag de associado configurada nas opções globais do Django."""
        return getattr(settings, 'AMAZON_ASSOCIATE_TAG', 'cgbookstore-20')

    @classmethod
    def is_amazon_url(cls, url: str) -> bool:
        """
        Verifica se a URL pertence a um domínio oficial da Amazon Brasil.
        """
        if not url:
            return False
        try:
            parsed = urlsplit(url.strip())
            hostname = (parsed.hostname or '').lower().rstrip('.')
            return hostname in cls.ALLOWED_DOMAINS
        except ValueError:
            return False

    @classmethod
    def extract_asin(cls, url: str) -> str:
        """
        Extrai o ASIN (10 caracteres alfanuméricos) de uma URL de produto da Amazon Brasil.

        Levanta ValueError se:
        - A URL for vazia ou nula;
        - O domínio não for um domínio oficial da Amazon Brasil;
        - O ASIN não puder ser identificado no padrão de rotas da Amazon.
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL não informada ou inválida.")

        raw_url = url.strip()
        if not raw_url:
            raise ValueError("URL vazia.")

        try:
            parsed = urlsplit(raw_url)
        except ValueError:
            raise ValueError("URL malformada.")

        hostname = (parsed.hostname or '').lower().rstrip('.')
        if hostname not in cls.ALLOWED_DOMAINS:
            raise ValueError(f"Domínio '{hostname}' não é um domínio oficial da Amazon Brasil.")

        path = parsed.path or ''

        # Padrão 1: /dp/ASIN, /gp/product/ASIN, /gp/aw/d/ASIN
        match = re.search(r'/(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})(?:[/?#]|$)', path, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        # Padrão 2: Segmento de caminho contendo ASIN (10 chars iniciando com dígito ou 'B')
        match = re.search(r'/([B0-9][A-Z0-9]{9})(?:[/?#]|$)', path, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        raise ValueError("ASIN válido não foi localizado na URL da Amazon fornecida.")

    @classmethod
    def normalize(cls, url: str, associate_tag: str | None = None) -> str:
        """
        Normaliza uma URL da Amazon Brasil para o formato padrão:
        https://www.amazon.com.br/dp/{ASIN}?tag={tag}

        É idempotente: executar múltiplas vezes produzirá exatamente o mesmo resultado.
        Levanta ValueError se a URL for inválida ou não contiver um ASIN.
        """
        tag = associate_tag or cls.get_associate_tag()
        asin = cls.extract_asin(url)
        return f"https://www.amazon.com.br/dp/{asin}?tag={tag}"
