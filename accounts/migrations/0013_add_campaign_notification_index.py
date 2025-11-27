# Generated manually for performance optimization
# This migration adds an index to CampaignNotification to optimize unread count queries

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_userprofile_avatar_campaignnotification'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='campaignnotification',
            index=models.Index(fields=['user', 'is_read'], name='accounts_ca_user_id_is_read_idx'),
        ),
    ]
