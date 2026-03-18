from django.core.management.base import BaseCommand
from core.models import Book
from django.utils.html import strip_tags
from django.db import transaction

class Command(BaseCommand):
    help = 'Remove tags HTML das descrições dos livros existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula a limpeza sem salvar no banco de dados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO SIMULAÇÃO (DRY RUN) - Nenhuma alteração será salva.'))

        books = Book.objects.all()
        total = books.count()
        count = 0
        changed = 0

        self.stdout.write(f'Analisando {total} livros...')

        with transaction.atomic():
            for book in books:
                if not book.description:
                    continue
                
                old_description = book.description
                new_description = strip_tags(old_description)
                
                # Strip tags can leave multiple spaces or newlines, 
                # but the main goal is removing HTML.
                
                if old_description != new_description:
                    changed += 1
                    if not dry_run:
                        book.description = new_description
                        book.save()
                    
                    if changed <= 10: # Mostrar apenas os primeiros 10 para exemplo
                        self.stdout.write(f'  [CLEANED] "{book.title}"')
                
                count += 1
                if count % 50 == 0:
                    self.stdout.write(f'Processados {count}/{total}...')

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Simulação concluída. {changed} livros seriam limpos.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Sucesso! {changed} livros foram atualizados.'))
