import json
import logging
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Book, Category, Author
from accounts.models import BookShelf, BookReview
from recommendations.models import AIReaderProfile, UserBookInteraction
from core.services.ai_provider_service import AIProviderFactory

logger = logging.getLogger(__name__)


class ReaderProfileService:
    """
    Serviço para gerenciar o Perfil Literário de IA (AIReaderProfile) dos usuários.
    Calcula as afinidades por categorias e autores baseando-se nas interações
    (estantes, avaliações e cliques) e gera análises descritivas com IA.
    """

    @staticmethod
    def get_or_create_profile(user) -> AIReaderProfile:
        """Obtém ou cria o perfil literário de IA do usuário."""
        profile, created = AIReaderProfile.objects.get_or_create(user=user)
        return profile

    @classmethod
    def update_profile_weights(cls, user) -> AIReaderProfile:
        """
        Analisa as interações do usuário no banco de dados e calcula pesos de
        afinidade (de 0.0 a 1.0) para categorias e autores.
        """
        profile = cls.get_or_create_profile(user)
        
        category_points = {}
        author_points = {}

        # 1. Analisar itens nas prateleiras (BookShelf)
        shelves = BookShelf.objects.filter(user=user).select_related('book', 'book__category', 'book__author')
        for item in shelves:
            book = item.book
            
            # Definir pontuação pelo tipo de prateleira
            points = 2
            if item.shelf_type == 'favorites':
                points = 10
            elif item.shelf_type == 'read':
                points = 6
            elif item.shelf_type == 'reading':
                points = 5
            elif item.shelf_type == 'to_read':
                points = 3
            elif item.shelf_type == 'abandoned':
                points = -3
                
            # Categoria
            if book.category:
                cat_name = book.category.name
                category_points[cat_name] = category_points.get(cat_name, 0) + points
                
            # Autor
            if book.author:
                aut_name = book.author.name
                author_points[aut_name] = author_points.get(aut_name, 0) + points

        # 2. Analisar avaliações (BookReview)
        reviews = BookReview.objects.filter(user=user).select_related('book', 'book__category', 'book__author')
        for r in reviews:
            book = r.book
            rating = float(r.rating)
            
            # Pontuação por avaliação
            points = 0
            if rating >= 4.0:
                points = 8
            elif rating >= 3.0:
                points = 4
            else:
                points = -4
                
            # Categoria
            if book.category:
                cat_name = book.category.name
                category_points[cat_name] = category_points.get(cat_name, 0) + points
                
            # Autor
            if book.author:
                aut_name = book.author.name
                author_points[aut_name] = author_points.get(aut_name, 0) + points

        # 3. Analisar interações menores (UserBookInteraction)
        interactions = UserBookInteraction.objects.filter(user=user).select_related('book', 'book__category', 'book__author')
        for inter in interactions:
            book = inter.book
            
            # Pontuação por tipo de interação
            points = 1
            if inter.interaction_type in ('read', 'completed'):
                points = 3
            elif inter.interaction_type == 'wishlist':
                points = 2
                
            # Categoria
            if book.category:
                cat_name = book.category.name
                category_points[cat_name] = category_points.get(cat_name, 0) + points
                
            # Autor
            if book.author:
                aut_name = book.author.name
                author_points[aut_name] = author_points.get(aut_name, 0) + points

        # Normalizar pesos de 0.0 a 1.0
        # Categorias
        normalized_categories = {}
        if category_points:
            max_cat_points = max(1, max(category_points.values()))
            # Filtra pontuações menores ou iguais a zero
            for cat, pts in category_points.items():
                if pts > 0:
                    normalized_categories[cat] = round(pts / max_cat_points, 2)
                    
        # Autores
        normalized_authors = {}
        if author_points:
            max_aut_points = max(1, max(author_points.values()))
            for aut, pts in author_points.items():
                if pts > 0:
                    normalized_authors[aut] = round(pts / max_aut_points, 2)

        # Ordenar e limitar top 10 categorias/autores
        sorted_categories = dict(sorted(normalized_categories.items(), key=lambda x: x[1], reverse=True)[:10])
        sorted_authors = dict(sorted(normalized_authors.items(), key=lambda x: x[1], reverse=True)[:10])

        profile.categories_interest = sorted_categories
        profile.authors_interest = sorted_authors
        profile.save()
        return profile

    @classmethod
    def generate_profile_summary_ai(cls, user, force=False) -> AIReaderProfile:
        """
        Chama o provedor de IA ativo para compor a biografia literária
        e o estilo de leitura do usuário, salvando no perfil.
        Caches por 7 dias para evitar chamadas de API repetidas.
        """
        profile = cls.get_or_create_profile(user)
        
        # Se as afinidades estiverem vazias, atualiza os pesos primeiro
        if not profile.categories_interest and not profile.authors_interest:
            profile = cls.update_profile_weights(user)
            
        # Verificar se o cálculo recente ainda é válido (7 dias)
        now = timezone.now()
        age = now - profile.last_calculated if profile.last_calculated else timezone.timedelta(days=99)
        if age.days < 7 and profile.profile_summary and profile.reading_style_ai and not force:
            return profile

        # Obter os dados básicos para o prompt
        categories_list = [f"{k} (afinidade: {v})" for k, v in profile.categories_interest.items()]
        authors_list = [f"{k} (afinidade: {v})" for k, v in profile.authors_interest.items()]
        
        # Livros favoritos e recentemente lidos
        fav_books = list(BookShelf.objects.filter(user=user, shelf_type='favorites').select_related('book')[:5])
        read_books = list(BookShelf.objects.filter(user=user, shelf_type='read').select_related('book')[:5])
        
        fav_books_titles = [b.book.title for b in fav_books if b.book]
        read_books_titles = [b.book.title for b in read_books if b.book]

        username = user.first_name or user.username
        
        prompt = f"""
        Você é o analista literário e conselheiro oficial da rede social de leitores CG.BookStore.
        Sua tarefa é criar um perfil literário divertido, descritivo e cativante para o leitor "{username}" com base em seus dados de consumo.
        
        Dados de Afinidades por Categoria:
        {json.dumps(categories_list, ensure_ascii=False)}
        
        Dados de Afinidades por Autor:
        {json.dumps(authors_list, ensure_ascii=False)}
        
        Livros Favoritos: {fav_books_titles}
        Livros Já Lidos: {read_books_titles}
        
        Com base nestas informações, gere um JSON contendo os seguintes campos em português:
        {{
            "biografia": "Um texto divertido e inspirador (de exatamente 2 a 3 parágrafos curtos) resumindo o estilo e preferências literárias do leitor. Diga que tipo de leitor ele é (ex: Explorador de Mundos, Detetive Clássico, etc.).",
            "estilo_leitura": {{
                "humor": "Humor preferido nas leituras (ex: Sombrio, Aventureiro, Reflexivo, Emotivo, Cômico)",
                "complexidade": "Nível de complexidade ideal (ex: Fácil, Média, Alta)",
                "ritmo": "Ritmo de leitura estimado (ex: Rápido, Moderado, Lento)",
                "temas_frequentes": ["Tema 1", "Tema 2", "Tema 3"]
            }}
        }}
        
        IMPORTANTE: Responda EXCLUSIVAMENTE com o JSON válido. Não adicione markdown, blocos ```json ou introduções.
        """
        
        try:
            provider = AIProviderFactory.get_provider()
            data = provider.generate_json(
                prompt=prompt,
                feature_name="reader_profile",
                user=user
            )
            
            if data:
                profile.profile_summary = data.get('biografia', '')
                profile.reading_style_ai = data.get('estilo_leitura', {})
                profile.save()
                
            return profile
        except Exception as e:
            logger.error(f"Erro ao gerar biografia literária de IA para {user.username}: {e}")
            return profile

    @classmethod
    def adjust_weights_on_feedback(cls, user, category_name=None, author_name=None, score_change=0.1):
        """
        Feedback Loop / Aprendizado Contínuo.
        Ajusta diretamente os pesos do perfil baseado nas reações do usuário
        (ex: clique em recomendação = +0.1, feedback negativo de resposta = -0.15).
        """
        try:
            profile = cls.get_or_create_profile(user)
            modified = False
            
            # Categoria
            if category_name:
                categories = dict(profile.categories_interest or {})
                old_score = categories.get(category_name, 0.0)
                new_score = max(0.0, min(1.0, old_score + score_change))
                categories[category_name] = round(new_score, 2)
                profile.categories_interest = categories
                modified = True
                
            # Autor
            if author_name:
                authors = dict(profile.authors_interest or {})
                old_score = authors.get(author_name, 0.0)
                new_score = max(0.0, min(1.0, old_score + score_change))
                authors[author_name] = round(new_score, 2)
                profile.authors_interest = authors
                modified = True
                
            if modified:
                profile.save()
                logger.info(f"[APRENDIZADO CONTINUO] Perfil de {user.username} atualizado via feedback: cat={category_name}, aut={author_name}, delta={score_change}")
        except Exception as e:
            logger.error(f"Erro ao aplicar feedback contínuo em reader profile: {e}")
