# Generated migration to add container_opacity field to Section model

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_banner_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='container_opacity',
            field=models.FloatField(
                default=1.0,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(1.0)
                ],
                verbose_name='Opacidade do Container',
                help_text='Transparência do container (0.0 = totalmente transparente, 1.0 = totalmente opaco)'
            ),
        ),
    ]
