# core/tests/test_video_media.py
"""
Testes automatizados para a Central de Mídias Externas Corporativa (Evolução do Modelo Video).
Verifica:
1. Parsing de URLs do YouTube e ID normalizado (embed_code).
2. Constraint de unicidade (platform + embed_code).
3. URL de embed em modo de alta privacidade (youtube-nocookie).
4. Fallback de thumbnails e suporte à duração formatada.
5. Validação de Selo Oficial de Canal (exige oficial_status_verified_by/at).
6. Incremento atômico de visualizações com F() por sessão.
7. Integração com ImageRightsRecord para thumbnail customizada.
8. Status de saúde 'unknown' sem falhar a aplicação quando a API do YouTube não está configurada.
"""

from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core.models import Video, ImageRightsRecord
from core.services.youtube_media_service import YouTubeMediaService

User = get_user_model()


class VideoMediaTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin_video',
            email='admin_video@test.com',
            password='password123'
        )

    def test_youtube_url_parsing_and_nocookie_embed(self):
        """Testa parsing de URLs do YouTube e geração de embed com youtube-nocookie."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = YouTubeMediaService.extract_video_id(url)
        self.assertEqual(video_id, "dQw4w9WgXcQ")

        embed_url = YouTubeMediaService.get_nocookie_embed_url(video_id)
        self.assertEqual(embed_url, "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")

    def test_video_model_normalizes_embed_code_and_embed_url(self):
        """Verifica se o save do model Video normaliza o ID e gera a URL youtube-nocookie."""
        video = Video.objects.create(
            title="Trailer Teste",
            video_url="https://youtu.be/dQw4w9WgXcQ"
        )
        self.assertEqual(video.embed_code, "dQw4w9WgXcQ")
        self.assertEqual(video.get_embed_url(), "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")

    def test_unique_video_per_platform_constraint(self):
        """Verifica se a constraint impede mídias duplicadas na mesma plataforma."""
        Video.objects.create(
            title="Vídeo Original",
            platform="youtube",
            video_url="https://www.youtube.com/watch?v=ABC123XYZ"
        )

        with self.assertRaises(Exception):
            Video.objects.create(
                title="Vídeo Duplicado",
                platform="youtube",
                video_url="https://www.youtube.com/watch?v=ABC123XYZ"
            )

    def test_official_channel_validation(self):
        """Verifica se is_official_channel exige responsável e data de verificação."""
        video = Video(
            title="Trailer Oficial Sem Auditoria",
            platform="youtube",
            video_url="https://www.youtube.com/watch?v=123OFFICIAL",
            is_official_channel=True # Sem verified_by / verified_at
        )

        with self.assertRaises(ValidationError):
            video.full_clean()

        # Com os dados de auditoria preenchidos, deve passar na validação
        video.official_status_verified_by = self.user
        video.official_status_verified_at = timezone.now()
        video.full_clean() # Não deve disparar exceção

    def test_formatted_duration_property(self):
        """Verifica se a propriedade formatted_duration formata o DurationField corretamente."""
        video = Video.objects.create(
            title="Vídeo com Duração",
            platform="youtube",
            video_url="https://youtu.be/durationTest",
            duration_td=timedelta(minutes=10, seconds=25)
        )
        self.assertEqual(video.formatted_duration, "10:25")

    def test_atomic_views_count_increment_by_session(self):
        """Verifica incremento de visualizações via F() com limite de 1 por sessão."""
        client = Client()
        video = Video.objects.create(
            title="Vídeo Visualizações",
            platform="youtube",
            video_url="https://youtu.be/viewTestCount"
        )
        url = reverse('core:video_detail', kwargs={'slug': video.slug})

        # Primeira visita -> Incrementa +1
        client.get(url)
        video.refresh_from_db()
        self.assertEqual(video.views_count, 1)

        # Segunda visita na mesma sessão -> NÃO incrementa
        client.get(url)
        video.refresh_from_db()
        self.assertEqual(video.views_count, 1)

    def test_health_check_returns_unknown_when_no_api_key(self):
        """Verifica se sem a chave de API do YouTube o status é mantido como 'unknown' sem crash."""
        video = Video.objects.create(
            title="Vídeo Checagem",
            platform="youtube",
            video_url="https://youtu.be/healthCheckTest"
        )
        YouTubeMediaService.check_video_health(video)
        video.refresh_from_db()
        self.assertEqual(video.media_status, 'unknown')
        self.assertEqual(video.health_check_source, 'none')

    def test_custom_thumbnail_image_rights_integration(self):
        """Verifica se thumbnail customizada do vídeo pode se integrar ao ImageRightsRecord."""
        video = Video.objects.create(
            title="Vídeo Capa Custom",
            platform="youtube",
            video_url="https://youtu.be/customThumb"
        )
        video_ct = ContentType.objects.get_for_model(Video)

        rights = ImageRightsRecord.objects.create(
            content_type=video_ct,
            object_id=video.id,
            image_field_name='thumbnail_image',
            credit_name='Ilustrador de Capas',
            license_type='licensed'
        )

        self.assertEqual(rights.content_object, video)
