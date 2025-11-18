# Generated migration to fix deployment issue
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_banner_model'),
    ]

    operations = [
        # Remove container_opacity if it exists
        # This is a safe operation that won't fail if column doesn't exist
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'core_section'
                    AND column_name = 'container_opacity'
                ) THEN
                    ALTER TABLE core_section DROP COLUMN container_opacity;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
