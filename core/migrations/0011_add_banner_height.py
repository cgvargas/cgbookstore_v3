# Generated manually for banner height customization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_banner_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='height',
            field=models.PositiveIntegerField(
                default=700,
                help_text='Altura do banner em pixels (padrão: 700px, estilo Crunchyroll: 700-900px)',
                verbose_name='Altura do Banner (px)'
            ),
        ),
    ]
