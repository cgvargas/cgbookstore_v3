"""
Serviço de FAQ para o Chatbot Literário.
Carrega e busca respostas do FAQ da plataforma.

Este serviço permite que o chatbot responda dúvidas básicas sobre
o uso da CG.BookStore de forma simples e clara.
"""
import logging
import re
from typing import Optional, List, Dict, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


# ==========================================
# DADOS DO FAQ
# ==========================================
FAQ_DATA = {
    "categories": [
        {
            "id": "conta",
            "name": "Conta e Perfil",
            "questions": [
                {
                    "id": "conta_1",
                    "question": "Como criar uma conta na CG.BookStore?",
                    "keywords": ["criar conta", "cadastro", "registrar", "nova conta", "como entrar", "se cadastrar"],
                    "answer": "Criar uma conta é simples: clique em 'Entrar' no menu, selecione 'Criar conta', preencha seus dados (nome, email e senha) ou use login social com Google/Facebook. Confirme seu email se solicitado e pronto!"
                },
                {
                    "id": "conta_2",
                    "question": "Esqueci minha senha. Como recuperar?",
                    "keywords": ["senha", "esqueci", "recuperar", "redefinir", "não consigo entrar", "trocar senha"],
                    "answer": "Para recuperar sua senha: clique em 'Entrar' → 'Esqueceu a senha?', digite seu email cadastrado, verifique sua caixa de entrada (ou spam), clique no link de recuperação e crie uma nova senha."
                },
                {
                    "id": "conta_3",
                    "question": "Como atualizar meu perfil?",
                    "keywords": ["atualizar perfil", "editar perfil", "mudar foto", "mudar nome", "alterar dados", "configurações"],
                    "answer": "Você pode editar seu perfil clicando no seu avatar no canto superior direito, selecionando 'Meu Perfil'. Lá você pode editar foto, nome, biografia e gêneros favoritos."
                },
                {
                    "id": "conta_4",
                    "question": "Como excluir minha conta?",
                    "keywords": ["excluir conta", "deletar conta", "apagar conta", "remover conta", "encerrar conta"],
                    "answer": "Para excluir sua conta: acesse 'Minha Biblioteca' no menu, clique em 'Editar Perfil', role até a seção 'Exclusão de Conta' e clique em 'Excluir Conta'. ⚠️ ATENÇÃO: Este processo é IRREVERSÍVEL! Todos os seus dados, incluindo biblioteca, listas, avaliações e histórico de conversas serão permanentemente removidos."
                },
                {
                    "id": "conta_5",
                    "question": "Posso usar login social (Google/Facebook)?",
                    "keywords": ["login google", "login facebook", "login social", "entrar com google", "entrar com facebook"],
                    "answer": "Sim! Clique em 'Continuar com Google' ou 'Continuar com Facebook' na página de login. Seus dados são seguros e não compartilhamos informações com terceiros."
                },
                {
                    "id": "conta_6",
                    "question": "Meus dados estão seguros?",
                    "keywords": ["segurança", "dados seguros", "privacidade", "lgpd", "proteção"],
                    "answer": "Sim! Suas senhas são criptografadas, usamos conexão HTTPS segura, não vendemos seus dados e estamos em conformidade com a LGPD."
                }
            ]
        },
        {
            "id": "livros",
            "name": "Livros e Catálogo",
            "questions": [
                {
                    "id": "livros_1",
                    "question": "Quantos livros estão disponíveis?",
                    "keywords": ["quantos livros", "catálogo", "acervo", "quantidade de livros"],
                    "answer": "Temos milhares de títulos, incluindo ficção, não-ficção, best-sellers, obras de autores emergentes, clássicos da literatura e lançamentos mensais."
                },
                {
                    "id": "livros_2",
                    "question": "Como buscar um livro específico?",
                    "keywords": ["buscar livro", "pesquisar", "procurar livro", "encontrar livro", "lupa", "pesquisa"],
                    "answer": "Use o ícone de lupa no menu para busca rápida, aplique filtros por categoria/autor/idioma, ou pergunte diretamente para mim! 🔍"
                },
                {
                    "id": "livros_3",
                    "question": "Posso ler os livros online?",
                    "keywords": ["ler online", "leitura digital", "ebook", "ler livro", "download livro"],
                    "answer": "Sim! Pelo app você pode ler ebooks gratuitos. No menu superior (navbar), acesse Livros → Biblioteca Digital. Nessa página, é possível buscar pelo título ou autor e escolher a fonte entre Project Gutenberg e Open Library, ambas com obras gratuitas e legais para leitura."
                },
                {
                    "id": "livros_4",
                    "question": "Como funcionam as avaliações e resenhas?",
                    "keywords": ["avaliação", "resenha", "estrelas", "comentar", "avaliar livro", "nota"],
                    "answer": "Você pode avaliar livros de 1 a 5 estrelas, escrever resenhas, ver opiniões de outros leitores e curtir resenhas úteis. Suas avaliações melhoram nossas recomendações!"
                },
                {
                    "id": "livros_5",
                    "question": "Recebo sugestões personalizadas?",
                    "keywords": ["sugestões", "recomendações", "livros parecidos", "indicações", "para você", "recomendação"],
                    "answer": "Sim! Usamos IA para recomendar livros baseado nos seus gêneros favoritos, suas avaliações e tendências. Acesse 'Recomendações para Você' na home ou pergunte para mim!"
                }
            ]
        },
        {
            "id": "premium",
            "name": "Premium e Pagamentos",
            "questions": [
                {
                    "id": "premium_1",
                    "question": "O que é o plano Premium?",
                    "keywords": ["premium", "plano premium", "assinatura", "vantagens", "benefícios", "vip"],
                    "answer": "O Premium oferece: conteúdo exclusivo, navegação sem anúncios, prioridade em recomendações, download de listas, debates premium e acesso antecipado a novos recursos."
                },
                {
                    "id": "premium_2",
                    "question": "Quanto custa o Premium?",
                    "keywords": ["preço", "valor", "custo", "quanto custa", "mensalidade", "preço premium"],
                    "answer": "Planos: Mensal R$ 19,90, Trimestral R$ 49,90 (economize 16%), Anual R$ 149,90 (economize 37%). O plano anual é o mais vantajoso!"
                },
                {
                    "id": "premium_3",
                    "question": "Quais formas de pagamento são aceitas?",
                    "keywords": ["pagamento", "cartão", "pix", "boleto", "mercadopago", "pagar"],
                    "answer": "Aceitamos via MercadoPago: cartão de crédito (à vista ou parcelado), Pix (instantâneo), boleto e saldo MercadoPago. 100% seguro!"
                },
                {
                    "id": "premium_4",
                    "question": "Como cancelar minha assinatura?",
                    "keywords": ["cancelar", "cancelamento", "desistir", "parar assinatura", "cancelar premium", "cancelar assinatura"],
                    "answer": "Para cancelar sua assinatura Premium: acesse 'Minha Biblioteca' no menu, clique em 'Editar Perfil', vá até a seção 'Assinatura Premium' e clique em 'Gerenciar Assinatura'. Lá você encontrará a opção de cancelar. Você mantém todos os benefícios Premium até o fim do período já pago."
                },
                {
                    "id": "premium_5",
                    "question": "Tenho direito a reembolso?",
                    "keywords": ["reembolso", "devolução", "dinheiro de volta", "garantia", "estorno"],
                    "answer": "Sim! 7 dias de garantia com reembolso total. Email: contato@cgbookstore.com. Devolução em até 10 dias úteis."
                },
                {
                    "id": "premium_6",
                    "question": "Há cupons de desconto disponíveis?",
                    "keywords": ["cupom", "desconto", "promoção", "oferta", "código promocional"],
                    "answer": "Fique atento às campanhas sazonais (Black Friday, Natal), ofertas por email e redes sociais. Inscreva-se na newsletter!"
                }
            ]
        },
        {
            "id": "biblioteca",
            "name": "Minha Biblioteca",
            "questions": [
                {
                    "id": "biblioteca_1",
                    "question": "Como adicionar livros à minha biblioteca?",
                    "keywords": ["adicionar livro", "salvar livro", "biblioteca", "minha lista", "guardar livro"],
                    "answer": "Clique no botão '+' na página do livro. Escolha: Lendo (em andamento), Lidos (finalizados), Favoritos ou Quero Ler (lista de desejos)."
                },
                {
                    "id": "biblioteca_2",
                    "question": "Posso criar listas personalizadas?",
                    "keywords": ["lista personalizada", "criar lista", "nova lista", "minhas listas", "organizar livros"],
                    "answer": "Sim! Acesse 'Minha Biblioteca' → 'Criar Nova Lista'. Crie listas como 'Livros para o Verão', 'Leituras Acadêmicas' ou qualquer tema!"
                },
                {
                    "id": "biblioteca_3",
                    "question": "Posso compartilhar minhas listas?",
                    "keywords": ["compartilhar", "enviar lista", "link da lista", "lista pública"],
                    "answer": "Sim! Gere link público da lista, compartilhe nas redes sociais ou envie para amigos leitores."
                },
                {
                    "id": "biblioteca_4",
                    "question": "Posso acompanhar meu progresso de leitura?",
                    "keywords": ["progresso", "estatísticas", "meta", "quantos livros li", "minha leitura"],
                    "answer": "Sim! Acesse 'Meu Perfil' → 'Estatísticas'. Veja: total de livros lidos, metas anuais, conquistas e badges."
                }
            ]
        },
        {
            "id": "tecnico",
            "name": "Suporte Técnico",
            "questions": [
                {
                    "id": "tecnico_1",
                    "question": "O site não está carregando. O que fazer?",
                    "keywords": ["não carrega", "erro", "problema", "lento", "travou", "bug"],
                    "answer": "Tente: F5 para atualizar, verificar internet, limpar cache do navegador, desativar AdBlock ou usar outro navegador. Persiste? Entre em contato!"
                },
                {
                    "id": "tecnico_2",
                    "question": "O site funciona em celular?",
                    "keywords": ["celular", "mobile", "smartphone", "tablet", "responsivo"],
                    "answer": "Sim! O site é 100% responsivo e funciona em smartphones, tablets, desktop e Smart TVs."
                },
                {
                    "id": "tecnico_3",
                    "question": "Há um aplicativo móvel?",
                    "keywords": ["app", "aplicativo", "download app", "play store", "app store"],
                    "answer": "Ainda não temos app nativo, mas você pode adicionar o site à tela inicial do celular (PWA). Um app dedicado está em nosso roadmap!"
                },
                {
                    "id": "tecnico_4",
                    "question": "Como entrar em contato com o suporte?",
                    "keywords": ["contato", "suporte", "ajuda", "atendimento", "falar com alguém", "email"],
                    "answer": "Email: contato@cgbookstore.com, chat de suporte no site, ou redes sociais (@cgbookstore). Respondemos em até 24h úteis!"
                }
            ]
        },
        {
            "id": "debates",
            "name": "Debates Literários",
            "questions": [
                {
                    "id": "debates_1",
                    "question": "O que são os Debates Literários?",
                    "keywords": ["debates literários", "o que são debates", "como funciona debates", "comunidade de leitores", "discussão de livros"],
                    "answer": "O módulo Debates Literários é um espaço comunitário onde leitores criam e participam de discussões sobre qualquer livro do catálogo. Permite criar tópicos, enviar posts/respostas aninhadas, votar positiva ou negativamente nos posts e ver contadores de posts e visualizações. Pode ser acessado via menu /debates/ ou na seção de debates da página de cada livro."
                },
                {
                    "id": "debates_2",
                    "question": "Como criar um tópico de debate?",
                    "keywords": ["criar debate", "criar tópico", "iniciar discussão", "novo debate", "criar debates"],
                    "answer": "Para criar um tópico de debate: 1. Acesse a página do livro desejado (/catalogo/<slug>/). 2. Clique em 'Novo Debate' na seção de debates. 3. Preencha o Título (max 200 caracteres) e a Descrição (obrigatório). 4. Submeta. Usuários Free podem criar 1 tópico por livro; usuários Premium podem criar tópicos ilimitados. Há um limite de 10 tópicos criados por hora (em produção)."
                },
                {
                    "id": "debates_3",
                    "question": "Como participar de um debate (responder)?",
                    "keywords": ["participar de debate", "responder debate", "comentar debate", "resposta aninhada", "responder comentário", "postar debate"],
                    "answer": "Qualquer usuário logado pode responder nos tópicos. Para responder ao tópico, use o formulário no final da página. Para responder a um comentário específico (resposta aninhada), clique em 'Responder' abaixo do post desejado para abrir o formulário inline. As respostas são ilimitadas para Free e Premium. Há limite de 60 posts por hora (em produção)."
                },
                {
                    "id": "debates_4",
                    "question": "Como funciona o sistema de votos?",
                    "keywords": ["votos", "votar", "upvote", "downvote", "positivo", "negativo", "score", "pontuação"],
                    "answer": "Cada post pode receber votos positivos (👍 upvote) ou negativos (👎 downvote) de usuários logados. O score do post é a diferença entre votos positivos e negativos. É permitido apenas 1 voto por post. Você pode alterar ou remover seu voto clicando novamente no botão, mas não pode votar no seu próprio post. Há um limite de 100 votos por hora (em produção)."
                },
                {
                    "id": "debates_5",
                    "question": "Como editar ou deletar meu post/tópico?",
                    "keywords": ["editar post", "deletar post", "editar tópico", "deletar tópico", "excluir post", "remover post", "alterar post"],
                    "answer": "Você pode editar/deletar suas próprias publicações. Para posts: clique em 'Editar' para alterar ou 'Deletar' para remover (soft-delete). Para tópicos: na página do seu tópico clique em 'Editar Tópico' ou 'Deletar Tópico' (deleta o tópico e todos os posts vinculados). Moderadores/staff também podem deletar tópicos/posts de outros usuários."
                },
                {
                    "id": "debates_6",
                    "question": "Quais são as limitações por plano (Free vs Premium)?",
                    "keywords": ["limitações plano", "free vs premium debates", "limite debates", "criar tópico free", "tópicos ilimitados"],
                    "answer": "Leitura, respostas, votos e edições são ilimitados para ambos os planos. A diferença é na criação de tópicos: usuários Free podem criar apenas 1 tópico por livro, enquanto usuários Premium podem criar tópicos ilimitados. Para ter acesso ilimitado, assine o plano Premium via MercadoPago na página /finance/planos/."
                },
                {
                    "id": "debates_7",
                    "question": "Como administrar debates pelo painel Admin?",
                    "keywords": ["administrar debates", "painel admin debates", "moderação debates", "django admin debates", "gerenciar tópicos"],
                    "answer": "Administradores/staff podem gerenciar tudo em /admin/debates/. No painel, é possível: 1. Fixar/Bloquear tópicos (DebateTopic). 2. Deletar/restaurar posts (DebatePost - soft delete com is_deleted). 3. Ver/filtrar votos (DebateVote). Útil para moderação de conteúdos ofensivos ou encerramento de discussões."
                }
            ]
        }
    ]
}


class FAQService:
    """
    Serviço para buscar respostas no FAQ da plataforma.
    
    Permite que o chatbot responda dúvidas sobre:
    - Conta e perfil
    - Livros e catálogo
    - Premium e pagamentos
    - Minha biblioteca
    - Suporte técnico
    - Debates literários
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._faq_data = FAQ_DATA
        self._all_questions = self._flatten_questions()
        self._initialized = True
        logger.info("FAQService inicializado com sucesso")
    
    def _flatten_questions(self) -> List[Dict]:
        """Achata todas as perguntas em uma lista única."""
        questions = []
        for category in self._faq_data.get("categories", []):
            for q in category.get("questions", []):
                q["category_name"] = category["name"]
                questions.append(q)
        return questions
    
    def detect_faq_intent(self, message: str) -> Tuple[bool, str]:
        """
        Detecta se a mensagem é uma pergunta sobre o uso da plataforma.
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Tuple (is_faq_question, category_hint)
        """
        message_lower = message.lower()
        
        # Padrões que indicam dúvida sobre a plataforma
        platform_patterns = [
            r"como\s+(faço|posso|funciona|usar|criar|excluir|cancelar|atualizar)",
            r"onde\s+(fica|está|encontro|acho)",
            r"o\s+que\s+é\s+(o\s+)?(premium|chatbot|biblioteca|debate)",
            r"(quanto\s+custa|preço|valor)",
            r"(posso|consigo|dá\s+para)\s+(ler|baixar|cancelar|criar|compartilhar|votar|editar|deletar)",
            r"(minha\s+conta|meu\s+perfil|minha\s+senha|minha\s+biblioteca)",
            r"(como\s+)?entr(ar|o)\s+(em\s+contato|no\s+site)",
            r"(suporte|ajuda|problema|erro|não\s+funciona)",
            r"(cadastr|registr|login|senha|assinatura|pagamento)",
            r"(debate(s)?|tópico(s)?|voto(s)?|votar|discuss(ão|ões)|post(s)?)",
        ]
        
        for pattern in platform_patterns:
            if re.search(pattern, message_lower):
                return True, self._detect_category(message_lower)
        
        return False, ""
    
    def _detect_category(self, message: str) -> str:
        """Detecta a categoria provável da pergunta."""
        category_keywords = {
            "conta": ["conta", "perfil", "senha", "login", "cadastro", "excluir"],
            "livros": ["livro", "buscar", "pesquisar", "catálogo", "ler", "avaliação"],
            "premium": ["premium", "assinatura", "preço", "pagamento", "cancelar", "reembolso"],
            "biblioteca": ["biblioteca", "lista", "favoritos", "lendo", "lidos"],
            "tecnico": ["erro", "problema", "app", "celular", "contato", "suporte"],
            "debates": ["debate", "tópico", "voto", "votar", "discussão", "post", "comentário", "responder"],
        }
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    return category
        
        return ""
    
    def search_faq(self, query: str, top_n: int = 3) -> List[Dict]:
        """
        Busca perguntas relevantes no FAQ.
        
        Args:
            query: Pergunta do usuário
            top_n: Número máximo de resultados
            
        Returns:
            Lista de perguntas/respostas relevantes
        """
        query_lower = query.lower()
        results = []
        
        for question in self._all_questions:
            score = self._calculate_relevance(query_lower, question)
            if score > 0.3:  # Threshold mínimo
                results.append({
                    "question": question["question"],
                    "answer": question["answer"],
                    "category": question["category_name"],
                    "score": score
                })
        
        # Ordenar por relevância
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_n]
    
    def _calculate_relevance(self, query: str, question: Dict) -> float:
        """
        Calcula a relevância de uma pergunta para a query.
        
        Usa combinação de:
        - Match de keywords
        - Similaridade de texto
        """
        score = 0.0
        
        # Peso para keywords (mais importante)
        keywords = question.get("keywords", [])
        for keyword in keywords:
            if keyword in query:
                score += 0.4
        
        # Similaridade com a pergunta
        q_text = question.get("question", "").lower()
        similarity = SequenceMatcher(None, query, q_text).ratio()
        score += similarity * 0.3
        
        # Palavras em comum
        query_words = set(query.split())
        q_words = set(q_text.split())
        common = len(query_words & q_words)
        if common > 2:
            score += 0.2
        
        return min(score, 1.0)  # Cap em 1.0
    
    def get_faq_context(self, query: str) -> Optional[str]:
        """
        Retorna contexto do FAQ formatado para o chatbot.
        
        Args:
            query: Pergunta do usuário
            
        Returns:
            String com contexto do FAQ ou None se não encontrar
        """
        is_faq, _ = self.detect_faq_intent(query)
        
        if not is_faq:
            return None
        
        results = self.search_faq(query, top_n=2)
        
        if not results:
            return None
        
        # Formatar contexto
        context_parts = ["[INFORMAÇÕES DO FAQ DA PLATAFORMA]"]
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"\nPergunta FAQ #{i}: {result['question']}")
            context_parts.append(f"Resposta: {result['answer']}")
        
        context_parts.append("\n[FIM DO FAQ - Use essas informações para responder de forma natural e amigável]")
        
        return "\n".join(context_parts)


# Singleton instance
_faq_service = None


def get_faq_service() -> FAQService:
    """Retorna instância singleton do serviço de FAQ."""
    global _faq_service
    if _faq_service is None:
        _faq_service = FAQService()
    return _faq_service
