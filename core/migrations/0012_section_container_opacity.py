# Generated manually for adding container_opacity field to Section model

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_video_thumbnail_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='container_opacity',
            field=models.FloatField(
                default=1.0,
                help_text='Transparência do container (0.0 = totalmente transparente, 1.0 = totalmente opaco)',
                validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
                verbose_name='Opacidade do Container'
            ),
        ),
    ]
