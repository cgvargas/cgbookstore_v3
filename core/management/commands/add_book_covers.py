"""
Management command para adicionar capas placeholder aos livros.

Uso:
    python manage.py add_book_covers
    python manage.py add_book_covers --force
    python manage.py add_book_covers --verbose
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Book
import requests


class Command(BaseCommand):
    """
    Comando para adicionar capas placeholder aos livros que não têm capa.

    Usa o serviço Lorem Picsum para gerar imagens placeholder realistas.
    """

    help = 'Adiciona capas placeholder aos livros que não possuem capa'

    def add_arguments(self, parser):
        """Define argumentos aceitos pelo comando."""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Substitui capas existentes por novas',
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe mensagens detalhadas durante a execução',
        )

    def handle(self, *args, **options):
        """Método principal do comando."""
        force = options['force']
        verbose = options['verbose']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🎨 ADD BOOK COVERS - CGBookStore v3'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Adicionar capas
        self._add_covers(force, verbose)

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ PROCESSO CONCLUÍDO!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # Resumo final
        self._print_summary()

    def _add_covers(self, force, verbose):
        """Adiciona capas placeholder aos livros."""
        self.stdout.write(self.style.WARNING('\n📚 PROCESSANDO LIVROS...'))

        # Filtrar livros
        if force:
            books = Book.objects.all()
            self.stdout.write(f'   🔄 Modo FORCE: Processando todos os {books.count()} livros')
        else:
            books = Book.objects.filter(cover_image='')
            self.stdout.write(f'   📖 Encontrados {books.count()} livros sem capa')

        if books.count() == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ Nenhum livro precisa de capa!\n'))
            return

        self.stdout.write(self.style.WARNING('\n🎨 ADICIONANDO CAPAS PLACEHOLDER...\n'))

        covers_added = 0
        covers_failed = 0
        covers_skipped = 0

        for book in books:
            # Se já tem capa e não é modo force, pular
            if book.cover_image and not force:
                covers_skipped += 1
                if verbose:
                    self.stdout.write(f'   ⏭️  Já tem capa: {book.title}')
                continue

            try:
                # Usar Lorem Picsum com seed baseado no ID do livro
                # Dimensões: 400x600 (proporção padrão de capa de livro)
                seed = book.id
                url = f'https://picsum.photos/seed/{seed}/400/600'

                if verbose:
                    self.stdout.write(f'   🔄 Baixando capa para: {book.title}')

                # Baixar imagem com timeout
                response = requests.get(url, timeout=15)

                if response.status_code == 200:
                    # Criar arquivo de imagem
                    image_content = ContentFile(response.content)
                    filename = f'{book.slug}.jpg'

                    # Deletar capa antiga se existir (modo force)
                    if book.cover_image and force:
                        try:
                            book.cover_image.delete(save=False)
                        except Exception:
                            pass  # Ignorar erro ao deletar

                    # Salvar nova capa
                    book.cover_image.save(filename, image_content, save=True)

                    covers_added += 1
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(f'   ✅ Capa adicionada: {book.title}')
                        )
                    else:
                        # Mostrar progresso mesmo sem verbose
                        self.stdout.write('.', ending='')
                        self.stdout.flush()
                else:
                    covers_failed += 1
                    if verbose:
                        self.stdout.write(
                            self.style.WARNING(
                                f'   ⚠️  Falha HTTP {response.status_code}: {book.title}'
                            )
                        )

            except requests.exceptions.Timeout:
                covers_failed += 1
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Timeout ao baixar: {book.title}')
                    )
            except requests.exceptions.RequestException as e:
                covers_failed += 1
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Erro de rede em {book.title}: {str(e)}')
                    )
            except Exception as e:
                covers_failed += 1
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Erro em {book.title}: {str(e)}')
                    )

        # Quebrar linha se não usou verbose (estava usando dots)
        if not verbose and covers_added > 0:
            self.stdout.write('')

        # Mensagem final
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ {covers_added} capas adicionadas'))

        if covers_failed > 0:
            self.stdout.write(self.style.WARNING(f'⚠️  {covers_failed} falhas'))

        if covers_skipped > 0:
            self.stdout.write(self.style.INFO(f'⏭️  {covers_skipped} pulados (já tinham capa)'))

        self.stdout.write('')

    def _print_summary(self):
        """Exibe resumo final."""
        total_books = Book.objects.count()
        books_with_cover = Book.objects.exclude(cover_image='').count()
        books_without_cover = total_books - books_with_cover

        coverage_percentage = (books_with_cover / total_books * 100) if total_books > 0 else 0

        self.stdout.write('\n📊 RESUMO FINAL:')
        self.stdout.write(f'   📚 Total de Livros: {total_books}')
        self.stdout.write(f'   🎨 Com Capa: {books_with_cover}')
        self.stdout.write(f'   📖 Sem Capa: {books_without_cover}')
        self.stdout.write(f'   📈 Cobertura: {coverage_percentage:.1f}%')
        self.stdout.write('')