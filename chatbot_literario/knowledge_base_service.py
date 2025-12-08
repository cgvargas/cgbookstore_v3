"""
Knowledge Base Service - Serviço de Busca e Gerenciamento da Base de Conhecimento.

Este módulo implementa busca inteligente na base de conhecimento aprendida
através de correções de admins.
"""

import logging
from typing import Optional, Dict, List
from django.db.models import Q
from .models import ChatbotKnowledge

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """
    Serviço para consultar e gerenciar a base de conhecimento
    aprendida através de correções.

    Funcionalidades:
    - Busca exata por pergunta
    - Busca fuzzy por palavras-chave
    - Adição de novas correções
    - Extração automática de palavras-chave
    """

    def search_knowledge(
        self,
        question: str,
        knowledge_type: Optional[str] = None,
        min_confidence: float = 0.7
    ) -> Optional[Dict]:
        """
        Busca conhecimento prévio para uma pergunta.

        Estratégia de busca:
        1. Tenta match exato (case-insensitive)
        2. Se falhar, tenta match por palavras-chave (fuzzy)
        3. Ordena por confiança e popularidade

        Args:
            question: Pergunta do usuário
            knowledge_type: Tipo de conhecimento (opcional)
            min_confidence: Confiança mínima (0-1)

        Returns:
            Dicionário com conhecimento encontrado ou None
        """
        try:
            # Normalizar pergunta
            question_normalized = question.lower().strip()

            # Filtro base
            base_filter = Q(is_active=True) & Q(confidence_score__gte=min_confidence)

            if knowledge_type:
                base_filter &= Q(knowledge_type=knowledge_type)

            # === ESTRATÉGIA 1: Busca Exata ===
            exact_match = ChatbotKnowledge.objects.filter(
                base_filter,
                original_question__iexact=question
            ).first()

            if exact_match:
                logger.info(f"✅ Knowledge Base: Match EXATO encontrado para '{question[:50]}'")
                exact_match.increment_usage()
                return self._serialize_knowledge(exact_match)

            # === ESTRATÉGIA 2: Busca Fuzzy por Palavras-chave ===
            keywords = self._extract_keywords(question_normalized)

            if keywords:
                # Buscar por overlap de keywords
                fuzzy_matches = ChatbotKnowledge.objects.filter(
                    base_filter,
                    keywords__overlap=keywords
                ).order_by('-confidence_score', '-times_used')[:3]

                # Se encontrou matches, pegar o melhor
                if fuzzy_matches:
                    best_match = fuzzy_matches[0]

                    # Calcular similaridade
                    similarity = self._calculate_similarity(keywords, best_match.keywords)

                    # Só usar se similaridade for > 50%
                    if similarity > 0.5:
                        logger.info(
                            f"✅ Knowledge Base: Match FUZZY encontrado para '{question[:50]}' "
                            f"(similaridade: {similarity:.2%})"
                        )
                        best_match.increment_usage()
                        return self._serialize_knowledge(best_match)

            # === ESTRATÉGIA 3: Busca por Substring ===
            # Tenta encontrar perguntas que contenham parte da pergunta atual
            if len(question_normalized) > 20:
                substring_match = ChatbotKnowledge.objects.filter(
                    base_filter,
                    original_question__icontains=question_normalized[:20]
                ).order_by('-confidence_score').first()

                if substring_match:
                    logger.info(f"✅ Knowledge Base: Match por SUBSTRING para '{question[:50]}'")
                    substring_match.increment_usage()
                    return self._serialize_knowledge(substring_match)

            logger.info(f"ℹ️ Knowledge Base: Nenhum conhecimento prévio para '{question[:50]}'")
            return None

        except Exception as e:
            logger.error(f"Erro ao buscar knowledge base: {e}", exc_info=True)
            return None

    def add_correction(
        self,
        original_question: str,
        incorrect_response: str,
        correct_response: str,
        knowledge_type: str,
        created_by,
        **kwargs
    ) -> ChatbotKnowledge:
        """
        Adiciona uma correção à base de conhecimento.

        Args:
            original_question: Pergunta original do usuário
            incorrect_response: Resposta incorreta (para referência)
            correct_response: Resposta correta
            knowledge_type: Tipo de conhecimento
            created_by: Usuário que criou
            **kwargs: Campos adicionais (related_book, related_author, etc)

        Returns:
            Instância de ChatbotKnowledge criada
        """
        keywords = self._extract_keywords(original_question.lower())

        knowledge = ChatbotKnowledge.objects.create(
            knowledge_type=knowledge_type,
            original_question=original_question,
            incorrect_response=incorrect_response,
            correct_response=correct_response,
            keywords=keywords,
            created_by=created_by,
            **kwargs
        )

        logger.info(f"✅ Nova correção adicionada à Knowledge Base: ID={knowledge.id}")
        return knowledge

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extrai palavras-chave de um texto.

        Remove stop words e palavras muito curtas.
        Retorna até 10 palavras-chave mais relevantes.

        Args:
            text: Texto para extrair keywords

        Returns:
            Lista de palavras-chave
        """
        # Stop words em português (palavras comuns a ignorar)
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
            'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas',
            'para', 'por', 'com', 'sem', 'sob', 'sobre',
            'e', 'ou', 'mas', 'porém', 'contudo',
            'que', 'quem', 'qual', 'quais', 'onde', 'quando', 'como', 'por que', 'porque',
            'é', 'foi', 'ser', 'estar', 'ter', 'haver',
            'meu', 'minha', 'seu', 'sua', 'nosso', 'nossa',
            'este', 'esta', 'esse', 'essa', 'aquele', 'aquela',
            'ele', 'ela', 'eles', 'elas', 'eu', 'tu', 'você',
            'me', 'te', 'se', 'lhe', 'nos', 'vos',
            'mais', 'menos', 'muito', 'pouco', 'todo', 'toda',
        }

        # Limpar e dividir
        text = text.lower()
        words = text.split()

        # Filtrar stop words, pontuação e palavras muito curtas
        keywords = []
        for word in words:
            # Remover pontuação
            word = word.strip('?,!.;:\"\'()[]{}')

            # Adicionar se não for stop word e tiver tamanho adequado
            if word and len(word) > 3 and word not in stop_words:
                keywords.append(word)

        # Limitar a 10 palavras-chave mais relevantes (primeiras palavras tendem a ser mais importantes)
        return keywords[:10]

    def _calculate_similarity(self, keywords1: List[str], keywords2: List[str]) -> float:
        """
        Calcula similaridade entre dois conjuntos de palavras-chave.

        Usa Jaccard similarity: |A ∩ B| / |A ∪ B|

        Args:
            keywords1: Primeiro conjunto de keywords
            keywords2: Segundo conjunto de keywords

        Returns:
            Similaridade (0.0 a 1.0)
        """
        if not keywords1 or not keywords2:
            return 0.0

        set1 = set(keywords1)
        set2 = set(keywords2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        if union == 0:
            return 0.0

        return intersection / union

    def _serialize_knowledge(self, knowledge: ChatbotKnowledge) -> Dict:
        """
        Serializa objeto de conhecimento para dicionário.

        Args:
            knowledge: Instância de ChatbotKnowledge

        Returns:
            Dicionário com dados estruturados
        """
        return {
            'id': knowledge.id,
            'type': knowledge.knowledge_type,
            'question': knowledge.original_question,
            'response': knowledge.correct_response,
            'confidence': knowledge.confidence_score,
            'times_used': knowledge.times_used,
            'related_book_id': knowledge.related_book_id,
            'related_author_id': knowledge.related_author_id,
            'keywords': knowledge.keywords,
        }

    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas sobre a base de conhecimento.

        Returns:
            Dict com estatísticas
        """
        total = ChatbotKnowledge.objects.count()
        active = ChatbotKnowledge.objects.filter(is_active=True).count()
        by_type = {}

        for ktype, _ in ChatbotKnowledge.KNOWLEDGE_TYPES:
            count = ChatbotKnowledge.objects.filter(knowledge_type=ktype).count()
            by_type[ktype] = count

        most_used = ChatbotKnowledge.objects.filter(
            is_active=True
        ).order_by('-times_used')[:5]

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_type': by_type,
            'most_used': [
                {
                    'id': k.id,
                    'question': k.original_question[:50],
                    'times_used': k.times_used,
                }
                for k in most_used
            ]
        }


# ==============================================================================
# SINGLETON PATTERN
# ==============================================================================

_knowledge_service_instance = None


def get_knowledge_service() -> KnowledgeBaseService:
    """
    Retorna instância singleton do serviço de Knowledge Base.

    Returns:
        Instância de KnowledgeBaseService
    """
    global _knowledge_service_instance
    if _knowledge_service_instance is None:
        _knowledge_service_instance = KnowledgeBaseService()
        logger.info("✅ Knowledge Base Service inicializado")
    return _knowledge_service_instance
