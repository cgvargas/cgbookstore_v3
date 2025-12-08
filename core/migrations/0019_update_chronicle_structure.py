# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_add_weekly_chronicle'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklychronicle',
            name='week_start_date',
            field=models.DateField(
                blank=True,
                help_text='Data de início da semana',
                null=True,
                verbose_name='Início da Semana'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='week_end_date',
            field=models.DateField(
                blank=True,
                help_text='Data de fim da semana',
                null=True,
                verbose_name='Fim da Semana'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='volume_number',
            field=models.IntegerField(
                default=1,
                help_text='Número do volume',
                verbose_name='Volume'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='issue_number',
            field=models.IntegerField(
                default=1,
                help_text='Número da edição',
                verbose_name='Edição'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='section_health_title',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Título do artigo sobre saúde',
                max_length=200,
                verbose_name='Título - Saúde'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='section_health_content',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Conteúdo do artigo sobre saúde',
                verbose_name='Conteúdo - Saúde'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='section_entertainment_title',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Título do artigo sobre entretenimento',
                max_length=200,
                verbose_name='Título - Entretenimento'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='section_entertainment_content',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Conteúdo do artigo sobre entretenimento',
                verbose_name='Conteúdo - Entretenimento'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='section_home_title',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Título do artigo sobre casa/família',
                max_length=200,
                verbose_name='Título - Casa & Família'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='section_home_content',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Conteúdo do artigo sobre casa/família',
                verbose_name='Conteúdo - Casa & Família'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='highlights_accomplishment',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Realização da semana',
                max_length=300,
                verbose_name='Realização'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='highlights_social',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Destaque social da semana',
                max_length=300,
                verbose_name='Social'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='highlights_health',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Destaque de saúde da semana',
                max_length=300,
                verbose_name='Saúde'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='highlights_learning',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Destaque de aprendizado da semana',
                max_length=300,
                verbose_name='Aprendizado'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='highlights_personal',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Destaque pessoal da semana',
                max_length=300,
                verbose_name='Pessoal'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='quote_secondary',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Segunda citação em destaque (opcional)',
                verbose_name='Citação Secundária'
            ),
        ),
        migrations.AddField(
            model_name='weeklychronicle',
            name='quote_secondary_author',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Autor da segunda citação (opcional)',
                max_length=100,
                verbose_name='Autor da Citação Secundária'
            ),
        ),
    ]
