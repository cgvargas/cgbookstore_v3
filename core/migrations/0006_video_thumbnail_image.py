# Generated manually for adding thumbnail_image field to Video model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_author_instagram_author_photo_author_twitter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='thumbnail_image',
            field=models.ImageField(
                blank=True,
                help_text='Envie uma imagem local para usar como thumbnail (recomendado para Instagram). Sobrescreve a URL automática.',
                null=True,
                upload_to='video_thumbnails/',
                verbose_name='Upload de Thumbnail'
            ),
        ),
    ]
