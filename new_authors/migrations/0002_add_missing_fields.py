# Generated manually on 2025-11-28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('new_authors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authorbook',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Descrição detalhada do livro e enredo', verbose_name='Descrição Completa'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='author_notes',
            field=models.TextField(blank=True, help_text='Notas ou comentários do autor sobre o capítulo', verbose_name='Notas do Autor'),
        ),
    ]
