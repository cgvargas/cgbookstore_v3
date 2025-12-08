"""
Comando Django para popular os planos iniciais de Autores e Editoras
Uso: python manage.py populate_plans
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from new_authors.models import AuthorPlan, PublisherPlan


class Command(BaseCommand):
    help = 'Popula os planos iniciais de Autores e Editoras'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando população de planos...'))

        # ========== PLANOS DE AUTORES ==========

        # Plano Gratuito
        free_plan, created = AuthorPlan.objects.get_or_create(
            plan_type='free',
            defaults={
                'name': 'Gratuito (Vitrine)',
                'description': '''
                    **Ideal para começar sua jornada como autor emergente!**

                    [OK] Crie seu perfil de autor
                    [OK] Publique até 3 livros
                    [OK] Upload de até 10 capítulos por livro
                    [OK] Estatísticas básicas de visualizações
                    [OK] Apareça na listagem pública

                    [!] Limitações:
                    - Não pode receber mensagens diretas de editoras
                    - Visualiza apenas que editoras demonstraram interesse
                    - Sem acesso a relatórios avançados
                    - Comissão de 10% em negociações fechadas
                ''',
                'price_monthly': Decimal('0.00'),
                'price_yearly': Decimal('0.00'),
                'max_books': 3,
                'max_chapters_per_book': 10,
                'can_receive_publisher_messages': False,
                'is_featured': False,
                'has_verified_badge': False,
                'has_advanced_stats': False,
                'commission_rate': Decimal('10.00'),
                'is_active': True,
                'display_order': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Plano GRATUITO de Autor criado'))
        else:
            self.stdout.write(self.style.WARNING('[!] Plano GRATUITO de Autor ja existe'))

        # Plano Premium
        premium_plan, created = AuthorPlan.objects.get_or_create(
            plan_type='premium',
            defaults={
                'name': 'Autor Premium',
                'description': '''
                    **Destaque-se e aumente suas chances de ser descoberto!**

                    [OK] **Livros ilimitados**
                    [OK] **Capítulos ilimitados**
                    [OK] Mensagens diretas de editoras
                    [OK] Perfil destacado com selo verificado ⭐
                    [OK] Estatísticas avançadas (origem, demografia)
                    [OK] Relatórios mensais de engajamento
                    [OK] Prioridade na busca
                    [OK] Webinars exclusivos sobre publicação
                    [OK] Badge "Autor Premium" no perfil
                    [OK] Comissão de 10% em negociações

                    [$] **R$ 19,90/mês ou R$ 199,00/ano** (economize 17%)
                ''',
                'price_monthly': Decimal('19.90'),
                'price_yearly': Decimal('199.00'),
                'max_books': None,  # Ilimitado
                'max_chapters_per_book': None,  # Ilimitado
                'can_receive_publisher_messages': True,
                'is_featured': True,
                'has_verified_badge': True,
                'has_advanced_stats': True,
                'commission_rate': Decimal('10.00'),
                'is_active': True,
                'display_order': 2
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Plano PREMIUM de Autor criado'))
        else:
            self.stdout.write(self.style.WARNING('[!] Plano PREMIUM de Autor já existe'))

        # Plano Pro
        pro_plan, created = AuthorPlan.objects.get_or_create(
            plan_type='pro',
            defaults={
                'name': 'Autor Pro',
                'description': '''
                    **Nível profissional para autores sérios!**

                    [OK] **Todos os benefícios do Premium +**
                    [OK] **Assessoria literária** (1 consultoria/mês via chat)
                    [OK] **Destaque na home** (rotatividade mensal)
                    [OK] **Selo de qualidade verificado** pela plataforma
                    [OK] **Relatório de mercado** (tendências e demandas)
                    [OK] **Networking exclusivo** em grupo fechado
                    [OK] **0% de comissão** em negociações pela plataforma!

                    [$] **R$ 49,90/mês ou R$ 499,00/ano** (economize 17%)
                ''',
                'price_monthly': Decimal('49.90'),
                'price_yearly': Decimal('499.00'),
                'max_books': None,  # Ilimitado
                'max_chapters_per_book': None,  # Ilimitado
                'can_receive_publisher_messages': True,
                'is_featured': True,
                'has_verified_badge': True,
                'has_advanced_stats': True,
                'commission_rate': Decimal('0.00'),  # SEM COMISSÃO!
                'is_active': True,
                'display_order': 3
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Plano PRO de Autor criado'))
        else:
            self.stdout.write(self.style.WARNING('[!] Plano PRO de Autor já existe'))

        # ========== PLANOS DE EDITORAS ==========

        # Plano Básico
        basic_pub, created = PublisherPlan.objects.get_or_create(
            plan_type='basic',
            defaults={
                'name': 'Editora Básico',
                'description': '''
                    **Comece a descobrir novos talentos literários!**

                    [OK] Acesso ao catálogo completo de autores
                    [OK] Filtros avançados (gênero, engajamento, palavras)
                    [OK] **Visualizar até 10 manuscritos/mês**
                    [OK] **Download de até 5 capítulos/mês** (PDF/DOCX)
                    [OK] Demonstrar interesse em livros
                    [OK] Estatísticas básicas de cada livro
                    [OK] Histórico de downloads

                    [$] **R$ 99,90/mês ou R$ 999,00/ano** (economize 17%)
                ''',
                'price_monthly': Decimal('99.90'),
                'price_yearly': Decimal('999.00'),
                'max_manuscript_views': 10,
                'max_chapter_downloads': 5,
                'can_download_full_book': False,
                'max_users': 1,
                'has_api_access': False,
                'has_priority_support': False,
                'early_access_hours': 0,
                'is_active': True,
                'display_order': 1
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Plano BÁSICO de Editora criado'))
        else:
            self.stdout.write(self.style.WARNING('[!] Plano BÁSICO de Editora já existe'))

        # Plano Premium
        premium_pub, created = PublisherPlan.objects.get_or_create(
            plan_type='premium',
            defaults={
                'name': 'Editora Premium',
                'description': '''
                    **Acesso completo para editoras profissionais!**

                    [OK] **Todos os benefícios do Básico +**
                    [OK] **Manuscritos ilimitados**
                    [OK] **Downloads ilimitados** (PDF/DOCX com watermark)
                    [OK] **Baixar livro completo** (todos os capítulos)
                    [OK] Relatórios detalhados de engajamento
                    [OK] Sistema de favoritos/watchlist ilimitado
                    [OK] Alertas personalizados (novos autores, gêneros)
                    [OK] Perfil destacado com logo
                    [OK] Badge "Editora Verificada Premium"
                    [OK] Mensagens diretas ilimitadas

                    [$] **R$ 249,90/mês ou R$ 2.499,00/ano** (economize 17%)
                ''',
                'price_monthly': Decimal('249.90'),
                'price_yearly': Decimal('2499.00'),
                'max_manuscript_views': None,  # Ilimitado
                'max_chapter_downloads': None,  # Ilimitado
                'can_download_full_book': True,
                'max_users': 1,
                'has_api_access': False,
                'has_priority_support': False,
                'early_access_hours': 0,
                'is_active': True,
                'display_order': 2
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Plano PREMIUM de Editora criado'))
        else:
            self.stdout.write(self.style.WARNING('[!] Plano PREMIUM de Editora já existe'))

        # Plano Enterprise
        enterprise_pub, created = PublisherPlan.objects.get_or_create(
            plan_type='enterprise',
            defaults={
                'name': 'Editora Enterprise',
                'description': '''
                    **Solução corporativa para grandes editoras!**

                    [OK] **Todos os benefícios do Premium +**
                    [OK] **API de acesso** para integração com sistemas
                    [OK] **Gerente de conta dedicado**
                    [OK] **Múltiplos usuários** (até 5 editores)
                    [OK] **Relatórios customizados** sob demanda
                    [OK] **Destaque máximo** na plataforma
                    [OK] **Análise de mercado mensal** sobre tendências
                    [OK] **Acesso antecipado** a novos autores (48h antes)
                    [OK] **Suporte prioritário** (WhatsApp/Chat)

                    [$] **R$ 499,90/mês ou R$ 4.999,00/ano** (economize 17%)
                ''',
                'price_monthly': Decimal('499.90'),
                'price_yearly': Decimal('4999.00'),
                'max_manuscript_views': None,  # Ilimitado
                'max_chapter_downloads': None,  # Ilimitado
                'can_download_full_book': True,
                'max_users': 5,
                'has_api_access': True,
                'has_priority_support': True,
                'early_access_hours': 48,
                'is_active': True,
                'display_order': 3
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Plano ENTERPRISE de Editora criado'))
        else:
            self.stdout.write(self.style.WARNING('[!] Plano ENTERPRISE de Editora já existe'))

        self.stdout.write(self.style.SUCCESS('\n[*] População de planos concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'\n[INFO] Total de Planos de Autores: {AuthorPlan.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'[INFO] Total de Planos de Editoras: {PublisherPlan.objects.count()}'))
