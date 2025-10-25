"""
Comando Django para popular o banco de dados com Achievements e Badges iniciais.

Uso:
    python manage.py populate_achievements
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import Achievement, Badge


class Command(BaseCommand):
    help = 'Popula o banco com Achievements e Badges iniciais do sistema de gamificação'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os achievements e badges existentes antes de popular',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎮 Iniciando população de dados de gamificação...\n'))

        # Limpar dados existentes se solicitado
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Removendo dados existentes...'))
            Achievement.objects.all().delete()
            Badge.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Dados removidos\n'))

        # Popular Achievements
        achievements_created = self.populate_achievements()

        # Popular Badges
        badges_created = self.populate_badges()

        # Resumo final
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ POPULAÇÃO CONCLUÍDA COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'📊 Conquistas criadas: {achievements_created}')
        self.stdout.write(f'🏅 Badges criados: {badges_created}')
        self.stdout.write(self.style.SUCCESS('=' * 60 + '\n'))

    @transaction.atomic
    def populate_achievements(self):
        """Cria as 20 conquistas iniciais."""
        self.stdout.write(self.style.WARNING('\n📖 Criando Conquistas (Achievements)...\n'))

        achievements_data = [
            # CATEGORIA: LEITURA (5 conquistas)
            {
                'name': 'Primeiro Livro',
                'description': 'Termine seu primeiro livro',
                'icon': '📖',
                'xp_reward': 50,
                'category': 'reading',
                'difficulty_level': 1,
                'display_order': 1,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 1,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Leitor Iniciante',
                'description': 'Leia 5 livros',
                'icon': '📚',
                'xp_reward': 100,
                'category': 'reading',
                'difficulty_level': 1,
                'display_order': 2,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 5,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Leitor Assíduo',
                'description': 'Leia 10 livros',
                'icon': '🎓',
                'xp_reward': 200,
                'category': 'reading',
                'difficulty_level': 2,
                'display_order': 3,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 10,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Mestre dos Livros',
                'description': 'Leia 50 livros',
                'icon': '🏆',
                'xp_reward': 1000,
                'category': 'reading',
                'difficulty_level': 4,
                'display_order': 4,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 50,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Velocista',
                'description': 'Leia 300 páginas em um período curto',
                'icon': '⚡',
                'xp_reward': 150,
                'category': 'reading',
                'difficulty_level': 3,
                'display_order': 5,
                'requirements_json': {
                    'type': 'pages_read',
                    'value': 300,
                    'condition': 'greater_or_equal'
                }
            },

            # CATEGORIA: PROGRESSO (5 conquistas)
            {
                'name': 'Pontual',
                'description': 'Complete sua primeira leitura dentro do prazo',
                'icon': '🎯',
                'xp_reward': 200,
                'category': 'progress',
                'difficulty_level': 2,
                'display_order': 6,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 1,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Disciplinado',
                'description': 'Complete 5 leituras com progresso regular',
                'icon': '📅',
                'xp_reward': 500,
                'category': 'progress',
                'difficulty_level': 3,
                'display_order': 7,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 5,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Maratonista',
                'description': 'Leia um grande volume de páginas',
                'icon': '📊',
                'xp_reward': 250,
                'category': 'progress',
                'difficulty_level': 3,
                'display_order': 8,
                'requirements_json': {
                    'type': 'pages_read',
                    'value': 1000,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Sequência de 7',
                'description': 'Mantenha um streak de 7 dias de leitura',
                'icon': '🔥',
                'xp_reward': 300,
                'category': 'progress',
                'difficulty_level': 2,
                'display_order': 9,
                'requirements_json': {
                    'type': 'streak_days',
                    'value': 7,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Sequência de 30',
                'description': 'Mantenha um streak de 30 dias de leitura',
                'icon': '💯',
                'xp_reward': 800,
                'category': 'progress',
                'difficulty_level': 4,
                'display_order': 10,
                'requirements_json': {
                    'type': 'streak_days',
                    'value': 30,
                    'condition': 'greater_or_equal'
                }
            },

            # CATEGORIA: SOCIAL (3 conquistas)
            {
                'name': 'Crítico',
                'description': 'Escreva 5 reviews de livros',
                'icon': '✍️',
                'xp_reward': 100,
                'category': 'social',
                'difficulty_level': 1,
                'display_order': 11,
                'requirements_json': {
                    'type': 'reviews_written',
                    'value': 5,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Avaliador',
                'description': 'Escreva 20 reviews de livros',
                'icon': '⭐',
                'xp_reward': 300,
                'category': 'social',
                'difficulty_level': 2,
                'display_order': 12,
                'requirements_json': {
                    'type': 'reviews_written',
                    'value': 20,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Influenciador',
                'description': 'Escreva 50 reviews e ajude outros leitores',
                'icon': '💬',
                'xp_reward': 400,
                'category': 'social',
                'difficulty_level': 3,
                'display_order': 13,
                'requirements_json': {
                    'type': 'reviews_written',
                    'value': 50,
                    'condition': 'greater_or_equal'
                }
            },

            # CATEGORIA: DIVERSIDADE (4 conquistas)
            {
                'name': 'Explorador',
                'description': 'Leia livros de 5 categorias diferentes',
                'icon': '🌈',
                'xp_reward': 250,
                'category': 'diversity',
                'difficulty_level': 2,
                'display_order': 14,
                'requirements_json': {
                    'type': 'categories_read',
                    'value': 5,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Globetrotter',
                'description': 'Explore 10 categorias diferentes',
                'icon': '🌍',
                'xp_reward': 350,
                'category': 'diversity',
                'difficulty_level': 3,
                'display_order': 15,
                'requirements_json': {
                    'type': 'categories_read',
                    'value': 10,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Clássicos',
                'description': 'Leia livros de literatura clássica',
                'icon': '📜',
                'xp_reward': 400,
                'category': 'diversity',
                'difficulty_level': 3,
                'display_order': 16,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 3,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Eclético',
                'description': 'Demonstre versatilidade em suas leituras',
                'icon': '🎭',
                'xp_reward': 500,
                'category': 'diversity',
                'difficulty_level': 4,
                'display_order': 17,
                'requirements_json': {
                    'type': 'categories_read',
                    'value': 15,
                    'condition': 'greater_or_equal'
                }
            },

            # CATEGORIA: ESPECIAL (3 conquistas)
            {
                'name': 'Aniversariante',
                'description': 'Leia no seu aniversário',
                'icon': '🎂',
                'xp_reward': 100,
                'category': 'special',
                'difficulty_level': 1,
                'display_order': 18,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 1,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Coruja',
                'description': 'Continue lendo durante a madrugada',
                'icon': '🌙',
                'xp_reward': 50,
                'category': 'special',
                'difficulty_level': 1,
                'display_order': 19,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 1,
                    'condition': 'greater_or_equal'
                }
            },
            {
                'name': 'Madrugador',
                'description': 'Comece o dia lendo',
                'icon': '☀️',
                'xp_reward': 50,
                'category': 'special',
                'difficulty_level': 1,
                'display_order': 20,
                'requirements_json': {
                    'type': 'books_read',
                    'value': 1,
                    'condition': 'greater_or_equal'
                }
            },
        ]

        created_count = 0
        for data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                name=data['name'],
                defaults=data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {achievement}'))
            else:
                self.stdout.write(f'  ⤷ {achievement.name} (já existe)')

        return created_count

    @transaction.atomic
    def populate_badges(self):
        """Cria os 15 badges iniciais."""
        self.stdout.write(self.style.WARNING('\n🏅 Criando Badges...\n'))

        badges_data = [
            # BRONZE (2 badges)
            {
                'name': 'Iniciante',
                'description': 'Complete seu cadastro',
                'icon': '🥉',
                'rarity': 'bronze',
                'category': 'reading',
                'display_order': 1,
                'requirements_json': {'achievements_count': 1}
            },
            {
                'name': 'Primeira Leitura',
                'description': 'Adicione seu primeiro livro à biblioteca',
                'icon': '📗',
                'rarity': 'bronze',
                'category': 'reading',
                'display_order': 2,
                'requirements_json': {'books_read_genre': 'any', 'count': 1}
            },

            # PRATA (3 badges)
            {
                'name': 'Leitor Regular',
                'description': 'Complete 10 livros',
                'icon': '🥈',
                'rarity': 'silver',
                'category': 'reading',
                'display_order': 3,
                'requirements_json': {'achievements_count': 3}
            },
            {
                'name': 'Crítico Ativo',
                'description': 'Escreva 10 reviews',
                'icon': '⭐',
                'rarity': 'silver',
                'category': 'social',
                'display_order': 4,
                'requirements_json': {'achievements_count': 2}
            },
            {
                'name': 'Pontual',
                'description': 'Complete 5 leituras dentro do prazo',
                'icon': '🎯',
                'rarity': 'silver',
                'category': 'achievement',
                'display_order': 5,
                'requirements_json': {'achievements_count': 5}
            },

            # OURO (4 badges)
            {
                'name': 'Leitor Assíduo',
                'description': 'Complete 50 livros',
                'icon': '🥇',
                'rarity': 'gold',
                'category': 'reading',
                'display_order': 6,
                'requirements_json': {'achievements_count': 10}
            },
            {
                'name': 'Colecionador',
                'description': 'Tenha 100 livros na biblioteca',
                'icon': '💎',
                'rarity': 'gold',
                'category': 'reading',
                'display_order': 7,
                'requirements_json': {'achievements_count': 15}
            },
            {
                'name': 'Sequência Épica',
                'description': 'Mantenha 30 dias de leitura consecutivos',
                'icon': '🔥',
                'rarity': 'gold',
                'category': 'time',
                'display_order': 8,
                'requirements_json': {'streak_days': 30}
            },
            {
                'name': 'Explorador Cultural',
                'description': 'Leia livros de 10 categorias diferentes',
                'icon': '🌍',
                'rarity': 'gold',
                'category': 'reading',
                'display_order': 9,
                'requirements_json': {'achievements_count': 12}
            },

            # PLATINA (3 badges)
            {
                'name': 'Mestre da Leitura',
                'description': 'Complete 100 livros e escreva 50 reviews',
                'icon': '💍',
                'rarity': 'platinum',
                'category': 'achievement',
                'display_order': 10,
                'requirements_json': {'achievements_count': 18}
            },
            {
                'name': 'Top 10 do Mês',
                'description': 'Fique entre os 10 melhores leitores do mês',
                'icon': '👑',
                'rarity': 'platinum',
                'category': 'achievement',
                'display_order': 11,
                'requirements_json': {'ranking_position': 10}
            },
            {
                'name': 'Sequência Lendária',
                'description': 'Mantenha 100 dias de leitura consecutivos',
                'icon': '🔥',
                'rarity': 'platinum',
                'category': 'time',
                'display_order': 12,
                'requirements_json': {'streak_days': 100}
            },

            # DIAMANTE (2 badges)
            {
                'name': 'Lenda Viva',
                'description': 'Complete 500 livros e esteja no top 3 anual',
                'icon': '💎',
                'rarity': 'diamond',
                'category': 'achievement',
                'display_order': 13,
                'requirements_json': {'achievements_count': 20}
            },
            {
                'name': 'Influenciador Literário',
                'description': 'Escreva reviews que inspirem milhares',
                'icon': '🌟',
                'rarity': 'diamond',
                'category': 'social',
                'display_order': 14,
                'requirements_json': {'achievements_count': 20}
            },

            # ESPECIAL (1 badge)
            {
                'name': 'Fundador',
                'description': 'Membro desde o início da plataforma',
                'icon': '🎖️',
                'rarity': 'special',
                'category': 'special_event',
                'display_order': 15,
                'is_limited_edition': True,
                'requirements_json': {}
            },
        ]

        created_count = 0
        for data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=data['name'],
                defaults=data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {badge}'))
            else:
                self.stdout.write(f'  ⤷ {badge.name} (já existe)')

        return created_count