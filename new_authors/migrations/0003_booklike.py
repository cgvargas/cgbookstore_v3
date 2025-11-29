# Generated manually to fix BookLike table missing issue

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('new_authors', '0002_chapter_author_notes_alter_authorbook_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BookLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Curtido em')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='new_authors.authorbook')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_books', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Curtida de Livro',
                'verbose_name_plural': 'Curtidas de Livros',
                'db_table': 'new_authors_book_like',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['book'], name='idx_like_book'), models.Index(fields=['user'], name='idx_like_user')],
                'unique_together': {('book', 'user')},
            },
        ),
    ]
