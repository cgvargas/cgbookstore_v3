import time
import urllib.request
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from core.models.banner import Banner

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Aquece o cache do Cloudflare CDN para vídeos e imagens dos banners ativos da home'

    def handle(self, *args, **options):
        now = timezone.now()
        banners = list(Banner.objects.filter(active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('order'))

        if not banners:
            self.stdout.write(self.style.WARNING("Nenhum banner ativo encontrado para aquecer."))
            return

        self.stdout.write(self.style.NOTICE(f"\n🚀 Iniciando aquecimento de cache para {len(banners)} banner(s) ativo(s)..."))

        headers = {
            'User-Agent': 'CGBookStore-CacheWarmup/1.0 (+https://www.cgbookstore.com.br)',
            'Accept': '*/*',
        }

        total_assets = 0
        total_hits = 0

        for banner in banners:
            self.stdout.write(f"\nBanner #{banner.id}: \"{banner.title}\"")

            # 1. Imagem do Banner / Poster
            if banner.image:
                try:
                    img_url = banner.image.url
                    self._warmup_url(img_url, "Imagem", headers)
                    total_assets += 1
                except Exception as e:
                    self.stderr.write(f"  ❌ Erro ao obter URL da imagem: {e}")

            # 2. Vídeo do Banner
            if getattr(banner, 'video_file', None) and banner.video_file:
                try:
                    video_url = banner.video_file.url
                    # Para vídeos, solicitamos os primeiros 2MB com Range request para aquecer o início do stream
                    video_headers = dict(headers)
                    video_headers['Range'] = 'bytes=0-2097152'
                    self._warmup_url(video_url, "Vídeo (primeiros 2MB stream)", video_headers)
                    total_assets += 1
                except Exception as e:
                    self.stderr.write(f"  ❌ Erro ao obter URL do vídeo: {e}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ Aquecimento concluído! {total_assets} recurso(s) processado(s) no Cloudflare."))

    def _warmup_url(self, url, label, headers):
        if not url.startswith('http://') and not url.startswith('https://'):
            self.stdout.write(f"  ⚠️ Ignorando URL local ou relativa: {url}")
            return

        start_time = time.time()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                elapsed = (time.time() - start_time) * 1000
                cf_cache = response.headers.get('CF-Cache-Status', 'N/A')
                content_length = response.headers.get('Content-Length', 'desconhecido')
                status_code = response.status

                cache_badge = f"[CF: {cf_cache}]" if cf_cache != 'N/A' else "[Direto R2]"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✔️ {label} | Status: {status_code} | Tempo: {elapsed:.0f}ms | {cache_badge} | Tam: {content_length} bytes"
                    )
                )
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            self.stderr.write(f"  ❌ Falha ao aquecer {label} ({url}): {e} ({elapsed:.0f}ms)")
