# Generated manually - Safe migration that checks if column exists before adding
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import migrations, models


def add_container_opacity_if_not_exists(apps, schema_editor):
    """Add container_opacity column only if it doesn't exist."""
    # Use raw SQL to check if column exists
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='core_section'
            AND column_name='container_opacity';
        """)
        exists = cursor.fetchone()

        if not exists:
            # Column doesn't exist, add it
            cursor.execute("""
                ALTER TABLE core_section
                ADD COLUMN container_opacity DOUBLE PRECISION DEFAULT 1.0 NOT NULL;
            """)
            cursor.execute("""
                ALTER TABLE core_section
                ADD CONSTRAINT core_section_container_opacity_check
                CHECK (container_opacity >= 0.0 AND container_opacity <= 1.0);
            """)
        # If column exists, do nothing (no error)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_banner_model'),
    ]

    operations = [
        migrations.RunPython(
            add_container_opacity_if_not_exists,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
