"""
URLs para ferramentas administrativas (sem necessidade de Shell).
"""

from django.urls import path
from core.views.admin_tools import (
    setup_initial_data_view,
    health_check_view,
    quick_stats_json,
    redis_test_view,
)
from core.views.section_autocomplete import section_item_autocomplete
from core.views.reports_dashboard import (
    reports_dashboard,
    export_books_csv,
    export_authors_csv,
    export_videos_csv,
    export_books_markdown,
    export_authors_markdown,
    export_videos_markdown,
    export_finance_markdown,
)

app_name = 'admin_tools'

urlpatterns = [
    path('setup/', setup_initial_data_view, name='setup_initial_data'),
    path('health/', health_check_view, name='health_check'),
    path('stats/json/', quick_stats_json, name='quick_stats_json'),
    path('redis-test/', redis_test_view, name='redis_test'),
    path('section-autocomplete/', section_item_autocomplete, name='section_autocomplete'),
    
    # Dashboard de Relatórios
    path('reports/', reports_dashboard, name='reports_dashboard'),
    
    # Exportação CSV
    path('reports/export/books/csv/', export_books_csv, name='export_books_csv'),
    path('reports/export/authors/csv/', export_authors_csv, name='export_authors_csv'),
    path('reports/export/videos/csv/', export_videos_csv, name='export_videos_csv'),
    
    # Exportação Markdown
    path('reports/export/books/md/', export_books_markdown, name='export_books_markdown'),
    path('reports/export/authors/md/', export_authors_markdown, name='export_authors_markdown'),
    path('reports/export/videos/md/', export_videos_markdown, name='export_videos_markdown'),
    path('reports/export/finance/md/', export_finance_markdown, name='export_finance_markdown'),
]

