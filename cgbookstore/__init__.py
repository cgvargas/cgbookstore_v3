# Garante que o Celery � carregado quando Django inicia
from .celery import app as celery_app

__all__ = ('celery_app',)
