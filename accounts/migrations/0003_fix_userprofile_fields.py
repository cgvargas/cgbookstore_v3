# Generated manually to fix favorite_genre conversion

import core.storage_backends
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_remove_bookreview_accounts_bo_book_id_921817_idx_and_more'),
        ('core', '0009_add_purchase_partner_fields'),
    ]

    operations = [
        # ========== ETAPA 1: Remover campos antigos ==========
        migrations.RemoveField(
            model_name='userprofile',
            name='library_is_public',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='points',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='reading_goal',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='show_reading_progress',
        ),

        # ========== ETAPA 2: Remover favorite_genre antigo (texto) ==========
        migrations.RemoveField(
            model_name='userprofile',
            name='favorite_genre',
        ),

        # ========== ETAPA 3: Adicionar novos campos ==========
        migrations.AddField(
            model_name='userprofile',
            name='allow_followers',
            field=models.BooleanField(default=True, verbose_name='Permitir Seguidores'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='badges',
            field=models.JSONField(blank=True, default=list, help_text='Lista de IDs de badges conquistados',
                                   verbose_name='Badges Conquistados'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='banner',
            field=models.ImageField(blank=True, help_text='Banner personalizado (máx. 5MB, 1200x300px)', null=True,
                                    storage=core.storage_backends.SupabaseMediaStorage(), upload_to='users/banners/',
                                    verbose_name='Banner'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='books_read_count',
            field=models.IntegerField(default=0, help_text='Total de livros concluídos',
                                      validators=[django.core.validators.MinValueValidator(0)],
                                      verbose_name='Livros Lidos'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_premium',
            field=models.BooleanField(default=False, verbose_name='Usuário Premium'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_profile_public',
            field=models.BooleanField(default=True, help_text='Permitir que outros usuários vejam seu perfil',
                                      verbose_name='Perfil Público'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='last_activity_date',
            field=models.DateField(blank=True, null=True, verbose_name='Última Atividade'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='level',
            field=models.IntegerField(default=1, help_text='Nível atual (1-30)',
                                      validators=[django.core.validators.MinValueValidator(1),
                                                  django.core.validators.MaxValueValidator(30)], verbose_name='Nível'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='premium_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Premium Expira Em'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='reading_goal_year',
            field=models.IntegerField(default=12, help_text='Quantos livros deseja ler este ano?',
                                      validators=[django.core.validators.MinValueValidator(1),
                                                  django.core.validators.MaxValueValidator(365)],
                                      verbose_name='Meta Anual de Leitura'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='streak_days',
            field=models.IntegerField(default=0, help_text='Dias consecutivos com atividade',
                                      validators=[django.core.validators.MinValueValidator(0)],
                                      verbose_name='Dias de Streak'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='theme_preference',
            field=models.CharField(
                choices=[('fantasy', '✨ Fantasia (Roxo/Dourado)'), ('classic', '📚 Clássicos (Marrom/Bege)'),
                         ('romance', '💕 Romance (Rosa/Vermelho)'),
                         ('scifi', '🚀 Ficção Científica (Azul Neon/Prateado) - PREMIUM'),
                         ('horror', '👻 Terror (Vermelho Escuro/Preto) - PREMIUM'),
                         ('mystery', '🔍 Mistério (Verde Escuro/Cinza) - PREMIUM'),
                         ('biography', '🎓 Biografia (Azul Royal/Dourado) - PREMIUM'),
                         ('poetry', '🌸 Poesia (Lilás/Rosa Claro) - PREMIUM'),
                         ('adventure', '⛰️ Aventura (Laranja/Marrom) - PREMIUM'),
                         ('thriller', '⚡ Thriller (Vermelho/Preto) - PREMIUM'),
                         ('historical', '🏛️ Histórico (Dourado/Marrom) - PREMIUM'),
                         ('selfhelp', '🌟 Autoajuda (Amarelo/Laranja) - PREMIUM'),
                         ('philosophy', '🧠 Filosofia (Azul Escuro/Cinza) - PREMIUM'),
                         ('dystopian', '🌆 Distopia (Cinza/Vermelho) - PREMIUM'),
                         ('contemporary', '🎨 Contemporâneo (Multicolor) - PREMIUM')], default='fantasy',
                help_text='Tema de personalização da biblioteca', max_length=20, verbose_name='Tema Visual'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_pages_read',
            field=models.IntegerField(default=0, help_text='Total de páginas lidas',
                                      validators=[django.core.validators.MinValueValidator(0)],
                                      verbose_name='Páginas Lidas'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_xp',
            field=models.IntegerField(default=0, help_text='Pontos de experiência acumulados',
                                      validators=[django.core.validators.MinValueValidator(0)],
                                      verbose_name='XP Total'),
        ),

        # ========== ETAPA 4: Recriar favorite_genre como ForeignKey ==========
        migrations.AddField(
            model_name='userprofile',
            name='favorite_genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='favorite_of_users', to='core.category',
                                    verbose_name='Gênero Favorito'),
        ),

        # ========== ETAPA 5: Alterar campos existentes ==========
        migrations.AlterModelOptions(
            name='userprofile',
            options={'ordering': ['-total_xp'], 'verbose_name': 'Perfil de Usuário',
                     'verbose_name_plural': 'Perfis de Usuários'},
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Foto de perfil (máx. 2MB, 500x500px)', null=True,
                                    storage=core.storage_backends.SupabaseMediaStorage(), upload_to='users/avatars/',
                                    verbose_name='Avatar'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(blank=True, help_text='Descreva seu perfil de leitor em até 150 caracteres',
                                   max_length=150, verbose_name='Bio Literária'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Criado Em'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Atualizado Em'),
        ),
    ]