"""
Model: UserProfile
Perfil estendido do usuário com informações adicionais e gamificação.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Perfil estendido do usuário.

    Campos:
    - user: Relacionamento 1:1 com User
    - avatar: Foto de perfil
    - bio: Biografia/descrição
    - reading_goal: Meta anual de livros
    - points: Pontos de gamificação
    - level: Nível do usuário (calculado por pontos)
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuário'
    )

    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar'
    )

    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Biografia'
    )

    reading_goal = models.PositiveIntegerField(
        default=12,
        verbose_name='Meta Anual de Leitura',
        help_text='Quantos livros você pretende ler este ano?'
    )

    points = models.PositiveIntegerField(
        default=0,
        verbose_name='Pontos',
        help_text='Pontos acumulados através de atividades'
    )

    # Preferências
    favorite_genre = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Gênero Favorito'
    )

    # Configurações de privacidade
    library_is_public = models.BooleanField(
        default=False,
        verbose_name='Biblioteca Pública',
        help_text='Permitir que outros usuários vejam sua biblioteca'
    )

    show_reading_progress = models.BooleanField(
        default=True,
        verbose_name='Mostrar Progresso de Leitura',
        help_text='Exibir progresso de leitura na biblioteca'
    )

    # Datas
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'
        ordering = ['-created_at']

    def __str__(self):
        return f'Perfil de {self.user.username}'

    @property
    def level(self):
        """Calcula o nível baseado nos pontos."""
        if self.points < 100:
            return 1
        elif self.points < 500:
            return 2
        elif self.points < 1000:
            return 3
        elif self.points < 2000:
            return 4
        else:
            return 5

    @property
    def level_name(self):
        """Retorna o nome do nível."""
        levels = {
            1: 'Leitor Iniciante',
            2: 'Leitor Entusiasta',
            3: 'Leitor Dedicado',
            4: 'Leitor Expert',
            5: 'Mestre Leitor'
        }
        return levels.get(self.level, 'Leitor')

    def add_points(self, amount):
        """Adiciona pontos ao perfil."""
        self.points += amount
        self.save()

    def books_read_this_year(self):
        """Retorna quantidade de livros lidos este ano."""
        from datetime import datetime
        current_year = datetime.now().year
        return self.user.bookshelves.filter(
            shelf_type='read',
            date_added__year=current_year
        ).count()

    def reading_goal_percentage(self):
        """Retorna percentual da meta alcançada."""
        books_read = self.books_read_this_year()
        if self.reading_goal > 0:
            return round((books_read / self.reading_goal) * 100, 1)
        return 0


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo."""
    if hasattr(instance, 'profile'):
        instance.profile.save()