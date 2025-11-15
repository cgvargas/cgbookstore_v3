"""
Comando de gerenciamento para criar buckets no Supabase Storage
CG.BookStore v3
"""

from django.core.management.base import BaseCommand
from core.utils.supabase_storage import supabase_storage_admin


class Command(BaseCommand):
    help = 'Cria os buckets necessários no Supabase Storage'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Criando buckets no Supabase Storage...'))
        
        try:
            supabase_storage_admin.create_buckets()
            self.stdout.write(self.style.SUCCESS('✓ Buckets criados com sucesso!'))
            self.stdout.write('')
            self.stdout.write('Buckets disponíveis:')
            self.stdout.write(f'  - {supabase_storage_admin.BOOK_COVERS_BUCKET}')
            self.stdout.write(f'  - {supabase_storage_admin.USER_AVATARS_BUCKET}')
            self.stdout.write(f'  - {supabase_storage_admin.AUTHOR_PHOTOS_BUCKET}')
            self.stdout.write(f'  - {supabase_storage_admin.VIDEO_THUMBNAILS_BUCKET}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao criar buckets: {str(e)}'))
            self.stdout.write(self.style.WARNING('\nCertifique-se de que:'))
            self.stdout.write('  1. SUPABASE_SERVICE_KEY está configurado no .env')
            self.stdout.write('  2. A service key tem permissões de administrador')
