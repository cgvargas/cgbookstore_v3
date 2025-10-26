from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class DebateTopic(models.Model):
    """Tópico de debate sobre um livro"""

    book = models.ForeignKey('core.Book', on_delete=models.CASCADE, related_name='debate_topics')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_topics')
    title = models.CharField('Título', max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField('Descrição')

    # Meta
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    # Status
    is_pinned = models.BooleanField('Fixado', default=False)
    is_locked = models.BooleanField('Bloqueado', default=False)

    # Contadores
    views_count = models.IntegerField('Visualizações', default=0)
    posts_count = models.IntegerField('Posts', default=0)

    class Meta:
        verbose_name = 'Tópico de Debate'
        verbose_name_plural = 'Tópicos de Debate'
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['book', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('debates:topic_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Incrementa contador de visualizações"""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def update_posts_count(self):
        """Atualiza contador de posts"""
        self.posts_count = self.posts.filter(is_deleted=False).count()
        self.save(update_fields=['posts_count'])


class DebatePost(models.Model):
    """Post em um tópico de debate"""

    topic = models.ForeignKey(DebateTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debate_posts')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    content = models.TextField('Conteúdo')

    # Meta
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    edited_at = models.DateTimeField('Editado em', null=True, blank=True)
    is_deleted = models.BooleanField('Deletado', default=False)

    # Votos
    votes_score = models.IntegerField('Pontuação', default=0)

    class Meta:
        verbose_name = 'Post de Debate'
        verbose_name_plural = 'Posts de Debate'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['topic', 'created_at']),
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return f"Post de {self.author.username} em {self.topic.title}"

    def update_votes_score(self):
        """Atualiza pontuação baseada em votos"""
        upvotes = self.votes.filter(vote_type='up').count()
        downvotes = self.votes.filter(vote_type='down').count()
        self.votes_score = upvotes - downvotes
        self.save(update_fields=['votes_score'])

    def get_user_vote(self, user):
        """Retorna o voto do usuário neste post"""
        if not user.is_authenticated:
            return None
        try:
            return self.votes.get(user=user).vote_type
        except DebateVote.DoesNotExist:
            return None


class DebateVote(models.Model):
    """Voto em um post de debate"""

    VOTE_CHOICES = [
        ('up', 'Positivo'),
        ('down', 'Negativo'),
    ]

    post = models.ForeignKey(DebatePost, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debate_votes')
    vote_type = models.CharField('Tipo de Voto', max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Voto em Debate'
        verbose_name_plural = 'Votos em Debates'
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'vote_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_vote_type_display()}"