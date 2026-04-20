"""
Migration: Adiciona campos de pré-venda / lançamento ao modelo Book.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_add_author_work'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='is_presale',
            field=models.BooleanField(
                default=False,
                verbose_name='Em Pré-Venda',
                help_text='Marque se este livro está em pré-venda / pré-lançamento'
            ),
        ),
        migrations.AddField(
            model_name='book',
            name='presale_release_date',
            field=models.DateField(
                null=True,
                blank=True,
                verbose_name='Data Prevista de Lançamento',
                help_text='Data prevista para o lançamento oficial do livro'
            ),
        ),
        migrations.AddField(
            model_name='book',
            name='presale_info',
            field=models.CharField(
                max_length=300,
                blank=True,
                verbose_name='Mensagem de Pré-Venda',
                help_text="Texto de destaque exibido na página do livro"
            ),
        ),
    ]
