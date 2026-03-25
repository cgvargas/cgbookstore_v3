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

        NOTA: Não filtra por knowledge_type porque os tipos de intent
        da detecção (franchise_info, adaptation_info, etc.) não correspondem
        aos KNOWLEDGE_TYPES do modelo (author_query, book_info, etc.).
        A relevância é validada pela similaridade de texto.

        Args:
            question: Pergunta do usuário
            knowledge_type: Tipo de conhecimento (ignorado - busca ampla)
            min_confidence: Confiança mínima (0-1)

        Returns:
            Dicionário com conhecimento encontrado ou None
        """
        try:
            # Normalizar pergunta
            question_normalized = question.lower().strip()

            # Filtro base - NÃO filtra por knowledge_type para garantir
            # que correções admin sejam encontradas independente do intent
            base_filter = Q(is_active=True) & Q(confidence_score__gte=min_confidence)

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
                ).order_by('-confidence_score', '-times_used')[:5]  # Aumenta pool para análise

                # Se encontrou matches, testar similaridades
                best_match = None
                best_similarity = 0.0

                for match in fuzzy_matches:
                    similarity = self._calculate_similarity(keywords, match.keywords)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = match

                # Reduzido threshold de 0.5 (50%) para 0.25 (25%) para capturar variações do usuário (ex: uso de pronomes diferentes)
                if best_match and best_similarity >= 0.25:
                    logger.info(
                        f"✅ Knowledge Base: Match FUZZY encontrado para '{question[:50]}' "
                        f"(similaridade: {best_similarity:.2%})"
                    )
                    best_match.increment_usage()
                    return self._serialize_knowledge(best_match)

            # === ESTRATÉGIA 3: Busca por Substring (Melhorada) ===
            # Em vez de tentar os primeiros 20 chars contidos na pergunta do KB
            # (que falha se a estrutura da frase mudar), tentar ver se a pergunta do KB 
            # está CONTIDA na pergunta atual, ou usar um overlap menor
            
            # Limpar pergunta removendo palavras curtas para a busca
            clean_q = " ".join([w for w in question_normalized.split() if w not in ['e', 'o', 'a', 'um', 'uma', 'de', 'do', 'da'] and len(w) > 3])
            
            if len(clean_q) > 10:
                # Procurar perguntas no banco que compartilham pelo menos uma substring com a atual
                # Truncando em palavras para tentar achar uma frase em comum
                first_few_words = " ".join(clean_q.split()[:3])
                if first_few_words:
                    substring_match = ChatbotKnowledge.objects.filter(
                        base_filter,
                        original_question__icontains=first_few_words
                    ).order_by('-confidence_score').first()

                    if substring_match:
                        logger.info(f"✅ Knowledge Base: Match por SUBSTRING (frase: '{first_few_words}') para '{question[:50]}'")
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
        Extrai palavras-chave de um texto com normalização básica.

        Remove stop words e palavras muito curtas.
        Aplica stemming básico em português (plural→singular, sufixos verbais).
        Retorna até 10 palavras-chave mais relevantes.

        Args:
            text: Texto para extrair keywords

        Returns:
            Lista de palavras-chave normalizadas
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
            'cite', 'diga', 'fale', 'deste', 'desta', 'desse', 'dessa',
            'alguma', 'algum', 'alguns', 'algumas', 'outra', 'outro', 'outras', 'outros',
            'também', 'ainda', 'já', 'então', 'assim',
        }

        # Limpar e dividir
        text = text.lower()
        words = text.split()

        # Filtrar stop words, pontuação e palavras muito curtas
        keywords = []
        for word in words:
            # Remover pontuação
            word = word.strip('?,!.;:"\'()[]{}')

            # Adicionar se não for stop word e tiver tamanho adequado
            if word and len(word) > 2 and word not in stop_words:
                # Normalização básica de português (stemming simples)
                normalized = self._normalize_word(word)
                if normalized not in keywords:  # Evitar duplicatas
                    keywords.append(normalized)

        # Limitar a 10 palavras-chave mais relevantes
        return keywords[:10]

    def _normalize_word(self, word: str) -> str:
        """
        Normalização básica de palavra em português (stemming simples).
        
        Remove sufixos comuns de plural, gênero e conjugação verbal
        para que 'obras'→'obra', 'autores'→'autor', 'escreveu'→'escrev'.
        """
        # Plurais irregulares (-ões → -ão, -ães → -ão)
        if word.endswith('ões') and len(word) > 4:
            return word[:-3] + 'ão'
        if word.endswith('ães') and len(word) > 4:
            return word[:-3] + 'ão'
        
        # Plural -es (ex: autores → autor)
        if word.endswith('ores') and len(word) > 5:
            return word[:-2]
        if word.endswith('res') and len(word) > 4:
            return word[:-1]
        
        # Plural simples -s (ex: obras → obra, livros → livro)
        if word.endswith('s') and not word.endswith('ss') and len(word) > 3:
            return word[:-1]
        
        # Sufixos verbais comuns
        for suffix in ['aram', 'eram', 'iram', 'endo', 'ando', 'indo']:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        # Passado simples (-ou, -eu, -iu)
        for suffix in ['ou', 'eu', 'iu']:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        return word

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
