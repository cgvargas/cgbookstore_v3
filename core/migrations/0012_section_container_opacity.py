# Generated migration to add container_opacity field back

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_remove_container_opacity'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='container_opacity',
            field=models.FloatField(
                default=1.0,
                help_text='Opacidade do fundo da seção (0.0 a 1.0). 1.0 = opaco, 0.0 = transparente',
                verbose_name='Opacidade do Fundo'
            ),
        ),
    ]
