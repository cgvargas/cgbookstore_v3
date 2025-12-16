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

app_name = 'admin_tools'

urlpatterns = [
    path('setup/', setup_initial_data_view, name='setup_initial_data'),
    path('health/', health_check_view, name='health_check'),
    path('stats/json/', quick_stats_json, name='quick_stats_json'),
    path('redis-test/', redis_test_view, name='redis_test'),  # Público - diagnóstico
]
