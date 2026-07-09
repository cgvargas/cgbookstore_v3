import logging
from django.db.models import Q
from django.contrib.auth.models import User
from recommendations.models import AIReaderProfile
from accounts.models import SystemNotification

logger = logging.getLogger(__name__)


class AINotificationService:
    """
    Serviço para disparar notificações inteligentes para usuários com base em seus perfis
    de interesse literário gerados por IA.
    """

    @classmethod
    def get_users_interested_in(cls, category_name=None, author_name=None, threshold=0.6) -> list:
        """
        Retorna a lista de usuários com alta afinidade (afinidade >= threshold)
        pela categoria ou pelo autor especificados.
        """
        interested_users = []
        profiles = AIReaderProfile.objects.all().select_related('user')
        
        for p in profiles:
            has_interest = False
            
            # Verificar categoria
            if category_name and p.categories_interest:
                score = p.categories_interest.get(category_name, 0.0)
                if score >= threshold:
                    has_interest = True
                    
            # Verificar autor
            if author_name and p.authors_interest:
                score = p.authors_interest.get(author_name, 0.0)
                if score >= threshold:
                    has_interest = True
                    
            if has_interest and p.user.is_active:
                interested_users.append(p.user)
                
        return interested_users

    @classmethod
    def notify_book_launch(cls, book):
        """
        Notifica dinamicamente os leitores interessados no lançamento de um livro.
        """
        try:
            category_name = book.category.name if book.category else None
            author_name = book.author.name if book.author else None
            
            users = cls.get_users_interested_in(category_name, author_name, threshold=0.6)
            
            if users:
                logger.info(f"[AI NOTIFICATION] Notificando {len(users)} usuários sobre lançamento do livro: {book.title}")
                SystemNotification.create_book_launch(book=book, users=users)
                return len(users)
            return 0
        except Exception as e:
            logger.error(f"Erro ao disparar notificação de lançamento de livro por IA: {e}")
            return 0

    @classmethod
    def notify_literary_event(cls, event):
        """
        Notifica dinamicamente os leitores sobre eventos literários de seu interesse.
        """
        try:
            # Pegamos a categoria do evento
            category_name = event.category if hasattr(event, 'category') else None
            
            users = cls.get_users_interested_in(category_name=category_name, threshold=0.6)
            
            if users:
                logger.info(f"[AI NOTIFICATION] Notificando {len(users)} usuários sobre evento: {event.title}")
                SystemNotification.create_literary_event(
                    event_name=event.title,
                    event_date=event.start_date,
                    event_url=f"/events/{event.id}/",
                    users=users
                )
                return len(users)
            return 0
        except Exception as e:
            logger.error(f"Erro ao disparar notificação de evento por IA: {e}")
            return 0
