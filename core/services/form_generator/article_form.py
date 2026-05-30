"""
Gerador de formulário de contribuição para Artigos/Notícias.

Mapeado sobre o model Article do app `news`.
Campos: title, subtitle, content_type, excerpt, content,
        category, tags, featured_image, video_url, source_url,
        source_name, event_date, event_location, event_link,
        priority, is_featured, meta_description.
"""

from .base_generator import BaseFormGenerator, FieldDefinition


class ArticleFormGenerator(BaseFormGenerator):
    """Gerador de formulário para contribuição de Artigos/Notícias."""

    COLOR_HEADER_BG = "1A3A5C"
    COLOR_ACCENT = "2E86AB"

    def get_form_title(self) -> str:
        return "Formulário de Contribuição — Artigo/Notícia"

    def get_form_description(self) -> str:
        return (
            "Use este formulário para contribuir com um novo artigo, notícia, entrevista, "
            "evento ou outro tipo de conteúdo editorial para a plataforma CG Bookstore. "
            "Após preencher, envie o arquivo para a equipe editorial para revisão e publicação."
        )

    def get_fields(self) -> list:
        return [
            # ── Informações Básicas ────────────────────────────────────────
            FieldDefinition(
                label="Título",
                field_type="text",
                required=True,
                instruction=(
                    "Título principal do artigo. Deve ser claro, objetivo e atraente. "
                    "Máximo de 200 caracteres."
                ),
                example="Stephen King anuncia nova trilogia de horror"
            ),
            FieldDefinition(
                label="Subtítulo / Chamada",
                field_type="text",
                required=False,
                instruction=(
                    "Frase de apoio ao título. Complementa o título com mais contexto. "
                    "Máximo de 300 caracteres."
                ),
                example="O mestre do terror revela planos para três novos livros em 2025"
            ),
            FieldDefinition(
                label="Tipo de Conteúdo",
                field_type="choice",
                required=True,
                instruction=(
                    "Selecione o tipo que melhor descreve este conteúdo. "
                    "Afeta a exibição e categorização na plataforma."
                ),
                options=[
                    "news — Notícia",
                    "interview — Entrevista",
                    "event — Evento",
                    "announcement — Anúncio",
                    "tip — Dica da Semana",
                    "highlight — Destaque",
                    "schedule — Programação",
                    "article — Artigo",
                    "guide — Guia",
                    "review — Resenha",
                ],
                example="news — Notícia"
            ),
            FieldDefinition(
                label="Categoria",
                field_type="text",
                required=True,
                instruction=(
                    "Nome da categoria existente na plataforma. "
                    "Consulte o admin para a lista de categorias ativas."
                ),
                example="Literatura Nacional"
            ),
            # ── Conteúdo ──────────────────────────────────────────────────
            FieldDefinition(
                label="Resumo (Excerpt)",
                field_type="textarea",
                required=True,
                instruction=(
                    "Texto curto exibido nos cards e listas. "
                    "Deve resumir o artigo em até 500 caracteres. "
                    "Evite repetir o título."
                ),
                example=(
                    "Em entrevista exclusiva ao The New York Times, Stephen King confirmou "
                    "que está trabalhando em três novos livros de horror a serem lançados entre 2025 e 2027."
                )
            ),
            FieldDefinition(
                label="Conteúdo Completo",
                field_type="textarea",
                required=True,
                instruction=(
                    "Texto completo do artigo. Pode incluir parágrafos, listas e citações. "
                    "Formatação HTML básica é aceita (<b>, <i>, <p>, <ul>, <li>). "
                    "Mínimo recomendado: 300 palavras para artigos de qualidade."
                ),
                example="<p>Em uma entrevista concedida nesta semana...</p>"
            ),
            # ── Mídia ─────────────────────────────────────────────────────
            FieldDefinition(
                label="URL da Imagem de Destaque",
                field_type="url",
                required=False,
                instruction=(
                    "URL pública de uma imagem para usar como destaque do artigo. "
                    "Resolução recomendada: 1200x630px. "
                    "Se não fornecida, a equipe editorial irá selecionar uma imagem."
                ),
                example="https://exemplo.com/imagem-stephen-king.jpg"
            ),
            FieldDefinition(
                label="Legenda da Imagem",
                field_type="text",
                required=False,
                instruction="Descrição curta da imagem para acessibilidade (alt text). Máximo 200 caracteres.",
                example="Stephen King durante coletiva de imprensa em Nova York"
            ),
            FieldDefinition(
                label="URL do Vídeo (YouTube/Vimeo)",
                field_type="url",
                required=False,
                instruction=(
                    "Link completo de um vídeo do YouTube ou Vimeo relacionado ao artigo. "
                    "Se fornecido, será incorporado na página do artigo."
                ),
                example="https://www.youtube.com/watch?v=EXEMPLO"
            ),
            # ── Evento (apenas para content_type = 'event') ───────────────
            FieldDefinition(
                label="Data do Evento",
                field_type="date",
                required=False,
                instruction=(
                    "Preencha apenas se o tipo de conteúdo for 'Evento'. "
                    "Formato: DD/MM/AAAA HH:MM (ex: 15/06/2025 14:00)"
                ),
                example="15/06/2025 14:00"
            ),
            FieldDefinition(
                label="Local do Evento",
                field_type="text",
                required=False,
                instruction=(
                    "Preencha apenas se o tipo for 'Evento'. "
                    "Endereço ou nome do local. Máximo 200 caracteres."
                ),
                example="Centro de Convenções Anhembi — São Paulo, SP"
            ),
            FieldDefinition(
                label="Link do Evento (Inscrição/Info)",
                field_type="url",
                required=False,
                instruction="URL para inscrição ou mais informações sobre o evento.",
                example="https://sympla.com.br/evento-exemplo"
            ),
            # ── Fonte e Atribuição ────────────────────────────────────────
            FieldDefinition(
                label="URL da Fonte Original",
                field_type="url",
                required=False,
                instruction=(
                    "Link da matéria/notícia original caso este artigo seja baseado "
                    "em outra publicação. Essencial para transparência editorial."
                ),
                example="https://nytimes.com/2025/01/stephen-king-nova-trilogia"
            ),
            FieldDefinition(
                label="Nome da Fonte",
                field_type="text",
                required=False,
                instruction="Nome do veículo de comunicação original. Máximo 100 caracteres.",
                example="The New York Times"
            ),
            # ── Configurações de Publicação ───────────────────────────────
            FieldDefinition(
                label="Prioridade",
                field_type="choice",
                required=True,
                instruction=(
                    "Define o peso editorial do artigo. "
                    "Artigos de alta prioridade aparecem em destaque."
                ),
                options=[
                    "1 — Baixa",
                    "2 — Normal (padrão)",
                    "3 — Alta",
                    "4 — Urgente",
                    "5 — Destaque Principal",
                ],
                example="2 — Normal (padrão)"
            ),
            FieldDefinition(
                label="Destaque na Home?",
                field_type="choice",
                required=True,
                instruction="Marque 'Sim' para que o artigo apareça em destaque na página inicial.",
                options=["Sim", "Não"],
                example="Não"
            ),
            FieldDefinition(
                label="Tags",
                field_type="text",
                required=False,
                instruction=(
                    "Palavras-chave separadas por vírgula para melhor categorização. "
                    "Use tags já existentes na plataforma quando possível."
                ),
                example="stephen-king, horror, lançamento, livros-2025"
            ),
            FieldDefinition(
                label="Meta Descrição (SEO)",
                field_type="text",
                required=False,
                instruction=(
                    "Resumo para mecanismos de busca (Google, Bing). "
                    "Máximo de 160 caracteres. Se não fornecida, o Resumo será utilizado."
                ),
                example="Stephen King confirma nova trilogia de horror para 2025. Saiba os detalhes."
            ),
            FieldDefinition(
                label="Nome do Autor",
                field_type="text",
                required=False,
                instruction=(
                    "Nome do usuário registrado na plataforma que assina o artigo. "
                    "Se deixado em branco, o artigo não terá autor atribuído."
                ),
                example="joao.silva (username na plataforma)"
            ),
        ]

    def get_instructions(self) -> list:
        return [
            (
                "📌 Sobre o Processo Editorial",
                (
                    "Após preencher este formulário e enviá-lo para a equipe, seu conteúdo será revisado "
                    "por um editor antes de ser publicado. O prazo médio de análise é de 2 a 5 dias úteis. "
                    "Você será notificado por e-mail sobre a decisão editorial."
                )
            ),
            (
                "✅ Critérios de Qualidade",
                (
                    "Para garantir a aprovação do seu artigo, certifique-se de que:\n"
                    "• O título é claro, factual e não sensacionalista;\n"
                    "• O conteúdo tem ao menos 300 palavras e está bem estruturado;\n"
                    "• As informações são verificáveis e a fonte original é citada (quando aplicável);\n"
                    "• A imagem de destaque tem alta resolução (mínimo 800x400px);\n"
                    "• O conteúdo não infringe direitos autorais de terceiros."
                )
            ),
            (
                "🚫 Conteúdo Não Aceito",
                (
                    "A plataforma CG Bookstore não publica:\n"
                    "• Conteúdo com fins publicitários disfarçado de editorial;\n"
                    "• Informações falsas ou não verificadas;\n"
                    "• Conteúdo com preconceito, ódio ou discriminação;\n"
                    "• Reprodução integral de matérias de outros veículos sem autorização;\n"
                    "• Spoilers de obras sem aviso claro no título."
                )
            ),
            (
                "📧 Como Enviar",
                (
                    "Após preencher este formulário, salve o arquivo e envie para: "
                    "editorial@cgbookstore.com — com o assunto "
                    "'Contribuição Editorial: [Título do Artigo]'. "
                    "Você também pode entrar em contato via chat da plataforma."
                )
            ),
        ]
