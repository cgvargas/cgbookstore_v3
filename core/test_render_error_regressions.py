"""Regressões para erros observados nos logs de produção do Render."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from core.services.ai_review_service import AIReviewService
from core.views.library_view import LibraryView


class RateLimitError(Exception):
    status_code = 429


class LibraryPersonalizationRegressionTest(SimpleTestCase):
    def test_recommended_article_uses_featured_image(self):
        article = SimpleNamespace(
            id=10,
            title='Notícia literária',
            subtitle='Destaque',
            featured_image=SimpleNamespace(url='https://cdn.example/news.webp'),
            published_at=datetime(2026, 7, 16),
        )

        serialized = LibraryView._serialize_recommended_article(article)

        self.assertEqual(serialized['image']['url'], 'https://cdn.example/news.webp')
        self.assertEqual(serialized['published_at'], '16/07/2026')

    def test_recommended_article_without_image_returns_none(self):
        article = SimpleNamespace(
            id=11,
            title='Notícia sem imagem',
            subtitle='',
            featured_image=None,
            published_at=datetime(2026, 7, 16),
        )

        serialized = LibraryView._serialize_recommended_article(article)

        self.assertIsNone(serialized['image'])


@override_settings(
    AI_PROVIDER='groq',
    AI_FALLBACK_PROVIDERS=['gemini'],
    AI_RATE_LIMIT_COOLDOWN_SECONDS=1200,
    GROQ_API_KEY='groq-test-key',
    GEMINI_API_KEY='gemini-test-key',
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
)
class AIReviewRateLimitRegressionTest(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.book = SimpleNamespace(
            id=29,
            title='Arquitetura Limpa',
            subtitle='',
            author=SimpleNamespace(name='Robert C. Martin'),
            category=SimpleNamespace(name='Tecnologia'),
            description='Descrição do livro.',
            page_count=400,
        )

    @patch('core.services.ai_review_service.AIProviderFactory.get_provider')
    def test_rate_limited_primary_uses_configured_fallback(self, get_provider):
        groq = MagicMock()
        groq.generate_json.side_effect = RateLimitError('429 rate limit exceeded')
        gemini = MagicMock()
        gemini.generate_json.return_value = {
            'resumo': 'Resumo por fallback.',
            'perfil_leitor': 'Leitores de tecnologia.',
            'faixa_etaria': '14+',
            'complexidade': 'Média',
            'tempo_leitura': '8 horas',
            'temas_principais': ['Arquitetura'],
            'nota_geral': 9,
        }
        get_provider.side_effect = lambda name: {'groq': groq, 'gemini': gemini}[name]

        result = AIReviewService.generate_review(self.book)

        self.assertEqual(result['resumo'], 'Resumo por fallback.')
        self.assertTrue(cache.get('ai_provider_rate_limited:groq'))
        self.assertEqual(get_provider.call_args_list, [call('groq'), call('gemini')])

    @patch('core.services.ai_review_service.AIProviderFactory.get_provider')
    def test_circuit_breaker_skips_limited_provider_on_next_analysis(self, get_provider):
        cache.set('ai_provider_rate_limited:groq', True, 1200)
        gemini = MagicMock()
        gemini.generate_json.return_value = {'contexto_historico': 'Fallback ativo.'}
        get_provider.return_value = gemini

        result = AIReviewService.generate_expanded_analysis(self.book)

        self.assertEqual(result['contexto_historico'], 'Fallback ativo.')
        get_provider.assert_called_once_with('gemini')
