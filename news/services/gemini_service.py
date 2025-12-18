"""
AI Service for News Agent
Serviço unificado para filtragem e criação de artigos usando Groq ou Gemini.
Prioriza Groq (gratuito e rápido) com fallback para Gemini.
"""

from groq import Groq
import google.generativeai as genai
from typing import List, Dict, Optional
import json
import re
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiNewsService:
    """
    Serviço para processar notícias com IA (Groq ou Gemini).
    
    Prioriza Groq (llama-3.3-70b) por ser gratuito e rápido.
    Falls back para Gemini se Groq não disponível.
    
    Exemplo de uso:
        service = GeminiNewsService()
        
        # Filtrar notícias
        filtered = service.filter_and_rank_news(raw_news, limit=10)
        
        # Criar artigo
        article = service.create_article(news_data)
    """
    
    def __init__(self):
        self.groq_client = None
        self.gemini_model = None
        self.provider = None
        
        # Tentar Groq primeiro (prioridade)
        groq_key = getattr(settings, 'GROQ_API_KEY', '')
        if groq_key:
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.provider = 'groq'
                self.model_name = 'llama-3.3-70b-versatile'
                logger.info(f"✅ AI Service inicializado com Groq ({self.model_name})")
            except Exception as e:
                logger.warning(f"Groq indisponível: {e}")
        
        # Fallback para Gemini
        if not self.groq_client:
            gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.provider = 'gemini'
                self.model_name = 'gemini-2.5-flash'
                logger.info(f"✅ AI Service inicializado com Gemini ({self.model_name})")
        
        if not self.provider:
            logger.warning("⚠️ Nenhuma API de IA configurada. Serviço funcionará em modo fallback.")
    
    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        return self.provider is not None
    
    def _call_ai(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """
        Chamada unificada para a IA (Groq ou Gemini).
        
        Returns:
            Resposta em texto da IA
        """
        if self.provider == 'groq':
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        
        elif self.provider == 'gemini':
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text
        
        else:
            raise Exception("Nenhuma API de IA disponível")
    
    def filter_and_rank_news(
        self, 
        news_items: List[Dict], 
        limit: int = 10
    ) -> List[Dict]:
        """
        Filtra e ranqueia notícias por relevância literária.
        """
        if not self.is_available():
            logger.warning("IA não disponível, retornando notícias sem filtro")
            return self._fallback_filter(news_items, limit)
        
        if not news_items:
            return []
        
        try:
            start_time = time.time()
            
            items_to_analyze = news_items[:50]
            prompt = self._build_filter_prompt(items_to_analyze, limit)
            
            response_text = self._call_ai(prompt, temperature=0.3, max_tokens=4096)
            result = self._parse_json_response(response_text)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ {self.provider.upper()} filtrou {len(result)} notícias de {len(items_to_analyze)} em {elapsed:.1f}s")
            
            # Enriquecer com dados originais
            enriched_result = []
            for item in result:
                original_idx = item.get('id', 0)
                if 0 <= original_idx < len(items_to_analyze):
                    original = items_to_analyze[original_idx].copy()
                    original.update({
                        'summary': item.get('summary', ''),
                        'relevance_score': item.get('relevance_score', 5),
                        'suggested_category': item.get('suggested_category', 'Geral'),
                        'suggested_tags': item.get('suggested_tags', []),
                    })
                    enriched_result.append(original)
            
            return enriched_result
            
        except Exception as e:
            logger.error(f"Erro ao filtrar com {self.provider}: {str(e)}")
            return self._fallback_filter(news_items, limit)
    
    def create_article(self, news_data: Dict) -> Dict:
        """
        Cria artigo completo a partir de dados da notícia.
        """
        if not self.is_available():
            raise Exception("Nenhuma API de IA disponível. Configure GROQ_API_KEY ou GEMINI_API_KEY.")
        
        try:
            start_time = time.time()
            
            prompt = self._build_article_prompt(news_data)
            response_text = self._call_ai(prompt, temperature=0.7, max_tokens=8192)
            
            article = self._parse_json_response(response_text)
            
            # Adicionar metadados
            article['processing_time'] = time.time() - start_time
            article['ai_model'] = self.model_name
            
            logger.info(f"✅ Artigo criado: '{article.get('title', '')[:50]}...' em {article['processing_time']:.1f}s")
            
            return article
            
        except Exception as e:
            logger.error(f"Erro ao criar artigo com {self.provider}: {str(e)}")
            raise
    
    def _build_filter_prompt(self, news_items: List[Dict], limit: int) -> str:
        """Constrói prompt para filtrar notícias."""
        
        news_text = "\n\n".join([
            f"ID: {i}\n"
            f"Título: {item['title']}\n"
            f"Descrição: {item['description'][:300]}...\n"
            f"Fonte: {item['source_name']}"
            for i, item in enumerate(news_items)
        ])
        
        prompt = f"""Você é um curador especializado em literatura para o blog CGBookStore.

ANALISE as seguintes {len(news_items)} notícias sobre literatura:

{news_text}

---

TAREFA:
1. Selecione as {limit} notícias MAIS RELEVANTES para leitores apaixonados por literatura
2. Para cada notícia, crie um resumo em português brasileiro (100-150 palavras)

PRIORIZE: Lançamentos de livros, entrevistas com autores, prêmios literários, eventos literários, adaptações.
EVITE: Política, celebridades não-autores, notícias superficiais.

CATEGORIAS: "Lançamentos", "Autores", "Mercado Editorial", "Prêmios", "Eventos", "Adaptações", "Geral"

RETORNE APENAS JSON válido:
[
  {{
    "id": 0,
    "relevance_score": 9.5,
    "summary": "Resumo em português...",
    "suggested_category": "Lançamentos",
    "suggested_tags": ["tag1", "tag2", "tag3"]
  }}
]
"""
        return prompt
    
    def _build_article_prompt(self, news_data: Dict) -> str:
        """Constrói prompt para criar artigo, com enriquecimento para adaptações."""
        
        # Detectar se é notícia de adaptação
        title = news_data.get('title', '').lower()
        summary = news_data.get('summary', news_data.get('description', '')).lower()
        text = f"{title} {summary}"
        
        is_adaptation = any(word in text for word in [
            'adaptação', 'adaptation', 'filme', 'movie', 'série', 'series',
            'netflix', 'hbo', 'disney', 'amazon prime', 'anime', 'manga',
            'game', 'jogo', 'baseado', 'based on', 'livro para'
        ])
        
        category = news_data.get('suggested_category', 'Geral')
        if category == 'Adaptações':
            is_adaptation = True
        
        # Instruções para adaptações
        adaptation_instructions = ""
        if is_adaptation:
            adaptation_instructions = """
CONTEÚDO ESPECIAL PARA ADAPTAÇÕES:
Como esta é sobre uma ADAPTAÇÃO, inclua obrigatoriamente:

📚 SOBRE O LIVRO: autor, ano, descrição breve
🎬 SOBRE A ADAPTAÇÃO: elenco, diretor, estúdio, plataforma, data
🎵 TRILHA SONORA: compositor (se conhecido)
💡 CURIOSIDADES: bastidores, diferenças do livro
📊 COMPARAÇÃO: o que esperar

Use seções com <h2> para organizar.
"""
        
        prompt = f"""Você é um escritor especializado em literatura para o blog CGBookStore.

INFORMAÇÕES DA NOTÍCIA:
Título: {news_data.get('title', '')}
Resumo: {news_data.get('summary', news_data.get('description', ''))}
Fonte: {news_data.get('source_name', '')}
Link: {news_data.get('link', '')}

---

CRIE um artigo ORIGINAL em português brasileiro sobre esta notícia.

ESTRUTURA:
1. Título cativante (máximo 70 caracteres)
2. Introdução (2-3 parágrafos)
3. Desenvolvimento (4-6 parágrafos)
4. Conclusão (1-2 parágrafos)

ESTILO: Profissional mas acessível, 800-1200 palavras.
FORMATAÇÃO: Use HTML semântico (<p>, <h2>, <h3>, <strong>, <em>, <blockquote>)
IMPORTANTE: NÃO copie texto da fonte. Adicione contexto e análise.
{adaptation_instructions}
RETORNE APENAS JSON válido:
{{
  "title": "Título do artigo (máx 70 chars)",
  "content": "Conteúdo completo em HTML...",
  "excerpt": "Resumo de 200-300 caracteres",
  "meta_description": "Meta description (150-160 chars)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
"""
        return prompt
    
    def _parse_json_response(self, response_text: str) -> any:
        """Parse da resposta JSON com tratamento robusto."""
        
        # Remover markdown code blocks
        text = re.sub(r'```json\s*', '', response_text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        # Tentar encontrar JSON válido
        if text.startswith('['):
            match = re.search(r'\[[\s\S]*\]', text)
        else:
            match = re.search(r'\{[\s\S]*\}', text)
        
        if match:
            text = match.group(0)
        
        # Tentar parse direto
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Tentar corrigir problemas comuns
        try:
            # Remover caracteres de controle
            text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
            # Escapar newlines dentro de strings
            text = re.sub(r'(?<!\\)\n', '\\n', text)
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Última tentativa: extrair campos manualmente
        try:
            if '"title"' in text and '"content"' in text:
                title_match = re.search(r'"title"\s*:\s*"([^"]*)"', text)
                content_match = re.search(r'"content"\s*:\s*"([\s\S]*?)"(?=\s*[,}])', text)
                excerpt_match = re.search(r'"excerpt"\s*:\s*"([^"]*)"', text)
                meta_match = re.search(r'"meta_description"\s*:\s*"([^"]*)"', text)
                tags_match = re.search(r'"tags"\s*:\s*\[(.*?)\]', text)
                
                article = {
                    'title': title_match.group(1) if title_match else 'Artigo',
                    'content': content_match.group(1) if content_match else '<p>Conteúdo não disponível</p>',
                    'excerpt': excerpt_match.group(1) if excerpt_match else '',
                    'meta_description': meta_match.group(1) if meta_match else '',
                    'tags': []
                }
                
                if tags_match:
                    tags_str = tags_match.group(1)
                    article['tags'] = re.findall(r'"([^"]*)"', tags_str)
                
                logger.info("JSON parseado com método de fallback")
                return article
        except Exception as e:
            logger.warning(f"Fallback parser falhou: {e}")
        
        logger.error(f"Erro ao parsear JSON")
        logger.debug(f"Resposta: {response_text[:1000]}...")
        raise json.JSONDecodeError("Não foi possível parsear a resposta", text, 0)
    
    def _fallback_filter(self, news_items: List[Dict], limit: int) -> List[Dict]:
        """Fallback: retorna as mais recentes."""
        sorted_items = sorted(
            news_items, 
            key=lambda x: (x.get('source_priority', 0), x.get('published_date', '')),
            reverse=True
        )
        return sorted_items[:limit]
