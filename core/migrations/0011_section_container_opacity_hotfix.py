# HOTFIX: Emergency migration to add container_opacity field
# This migration adds the field safely, checking if it already exists

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_banner_model'),
    ]

    operations = [
        # Safe SQL that adds the column only if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name = 'core_section'
                        AND column_name = 'container_opacity'
                    ) THEN
                        ALTER TABLE core_section
                        ADD COLUMN container_opacity DOUBLE PRECISION DEFAULT 1.0 NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql="""
                ALTER TABLE core_section DROP COLUMN IF EXISTS container_opacity;
            """,
        ),
    ]
