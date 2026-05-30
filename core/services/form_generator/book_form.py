"""
Gerador de formulário de contribuição para Livros.

Mapeado sobre o model Book do app `core`.
Campos: title, subtitle, author, category, description,
        publication_date, isbn, publisher, page_count, language,
        cover_image, formatos disponíveis, pré-venda, parceiro comercial.
"""

from .base_generator import BaseFormGenerator, FieldDefinition


class BookFormGenerator(BaseFormGenerator):
    """Gerador de formulário para contribuição de novos Livros ao catálogo."""

    COLOR_HEADER_BG = "2C3E50"   # Azul-escuro acinzentado (diferente do de artigos)
    COLOR_ACCENT = "8E44AD"       # Roxo — identidade visual de livros

    def get_form_title(self) -> str:
        return "Formulário de Contribuição — Livro"

    def get_form_description(self) -> str:
        return (
            "Use este formulário para solicitar a inclusão de um novo livro no catálogo da CG Bookstore. "
            "Preencha todos os campos obrigatórios com informações precisas e verificáveis. "
            "A equipe editorial revisará as informações antes de publicar o livro na plataforma."
        )

    def get_fields(self) -> list:
        return [
            # ── Identificação Principal ────────────────────────────────────
            FieldDefinition(
                label="Título do Livro",
                field_type="text",
                required=True,
                instruction=(
                    "Título completo e oficial do livro, conforme consta na capa e nos registros editoriais. "
                    "Não abrevie. Máximo de 300 caracteres."
                ),
                example="O Senhor dos Anéis: A Sociedade do Anel"
            ),
            FieldDefinition(
                label="Subtítulo",
                field_type="text",
                required=False,
                instruction=(
                    "Subtítulo do livro, se houver. Inclua apenas se faz parte do título oficial. "
                    "Máximo de 500 caracteres."
                ),
                example="Parte I da trilogia O Senhor dos Anéis"
            ),
            FieldDefinition(
                label="ISBN-13",
                field_type="text",
                required=True,
                instruction=(
                    "Código ISBN-13 (13 dígitos) da edição que deseja cadastrar. "
                    "Encontrado na contracapa ou página de direitos. "
                    "Formato: 978-XXXXXXXXX ou apenas 13 dígitos sem hífens."
                ),
                example="978-8533619081"
            ),
            FieldDefinition(
                label="ISBN-10 (alternativo)",
                field_type="text",
                required=False,
                instruction=(
                    "Código ISBN-10 (10 dígitos) caso o ISBN-13 não esteja disponível. "
                    "Comum em edições anteriores a 2007."
                ),
                example="8533619081"
            ),
            # ── Autoria e Publicação ──────────────────────────────────────
            FieldDefinition(
                label="Autor(es)",
                field_type="text",
                required=True,
                instruction=(
                    "Nome completo do autor principal. Se houver múltiplos autores, "
                    "separe por ponto e vírgula. Use o nome completo sem abreviações."
                ),
                example="J.R.R. Tolkien"
            ),
            FieldDefinition(
                label="Editora",
                field_type="text",
                required=True,
                instruction=(
                    "Nome oficial da editora responsável pela edição que deseja cadastrar. "
                    "Se houver diferentes edições, especifique a que corresponde ao ISBN informado."
                ),
                example="Martins Fontes"
            ),
            FieldDefinition(
                label="Data de Publicação",
                field_type="date",
                required=True,
                instruction=(
                    "Data de publicação original desta edição. "
                    "Formato: DD/MM/AAAA (dia pode ser 01 caso só saiba mês/ano)."
                ),
                example="01/09/2002"
            ),
            FieldDefinition(
                label="Idioma",
                field_type="choice",
                required=True,
                instruction=(
                    "Idioma principal do livro. Use o código ISO 639-1 de 2 letras. "
                    "Se o idioma não estiver listado, informe nas observações."
                ),
                options=[
                    "pt — Português",
                    "en — Inglês",
                    "es — Espanhol",
                    "fr — Francês",
                    "de — Alemão",
                    "it — Italiano",
                    "ja — Japonês",
                    "zh — Chinês",
                    "ar — Árabe",
                    "outro — Outro (especifique nas observações)",
                ],
                example="pt — Português"
            ),
            # ── Categorização ─────────────────────────────────────────────
            FieldDefinition(
                label="Categoria Principal",
                field_type="text",
                required=True,
                instruction=(
                    "Gênero literário ou categoria principal do livro. "
                    "Consulte a lista de categorias cadastradas na plataforma para usar um nome existente."
                ),
                example="Fantasia"
            ),
            # ── Conteúdo ──────────────────────────────────────────────────
            FieldDefinition(
                label="Sinopse / Descrição",
                field_type="textarea",
                required=True,
                instruction=(
                    "Descrição completa do livro. Use a sinopse oficial da editora ou back cover. "
                    "Mínimo de 80 caracteres. Não copie avaliações de leitores, apenas a sinopse editorial."
                ),
                example=(
                    "A história começa no Shire, uma região idílica e rural habitada pelos Hobbits, "
                    "criaturas pacatas que vivem longe dos problemas do mundo exterior..."
                )
            ),
            FieldDefinition(
                label="Número de Páginas",
                field_type="number",
                required=True,
                instruction=(
                    "Número total de páginas desta edição específica. "
                    "Inclua apenas páginas de conteúdo (exclua índice remissivo se estiver no final)."
                ),
                example="712"
            ),
            # ── Mídia ─────────────────────────────────────────────────────
            FieldDefinition(
                label="URL da Imagem de Capa",
                field_type="url",
                required=True,
                instruction=(
                    "URL pública de alta qualidade da capa oficial do livro. "
                    "OBRIGATÓRIO: deve ser a capa real da edição, não uma capa genérica. "
                    "A equipe verificará se a imagem corresponde à edição informada. "
                    "Fontes aceitas: Google Books, Open Library, site da editora, Amazon."
                ),
                example="https://books.google.com/books/content?id=EXEMPLO&printsec=frontcover&img=1&zoom=3"
            ),
            # ── Formatos Disponíveis ──────────────────────────────────────
            FieldDefinition(
                label="Disponível em E-book/Kindle?",
                field_type="choice",
                required=True,
                instruction="Indique se esta edição está disponível em formato digital Kindle/eBook.",
                options=["Sim", "Não", "Não sei"],
                example="Sim"
            ),
            FieldDefinition(
                label="Disponível em Audiolivro?",
                field_type="choice",
                required=True,
                instruction="Indique se existe versão audiolivro desta obra.",
                options=["Sim", "Não", "Não sei"],
                example="Não"
            ),
            FieldDefinition(
                label="Disponível em Livro Físico?",
                field_type="choice",
                required=True,
                instruction="Indique se o livro físico (impresso) ainda está em circulação.",
                options=["Sim", "Não", "Não sei"],
                example="Sim"
            ),
            FieldDefinition(
                label="Disponível em PDF?",
                field_type="choice",
                required=False,
                instruction="Indique se existe versão oficial em PDF (ex: via Google Play Books).",
                options=["Sim", "Não", "Não sei"],
                example="Não"
            ),
            # ── Parceiro Comercial ────────────────────────────────────────
            FieldDefinition(
                label="Link para Compra (opcional)",
                field_type="url",
                required=False,
                instruction=(
                    "URL da página de compra deste livro em uma loja parceira "
                    "(Amazon, Saraiva, Cultura, etc.). "
                    "Certifique-se de que o link aponta especificamente para esta edição."
                ),
                example="https://www.amazon.com.br/Senhor-dos-Aneis-Sociedade/dp/8533619081"
            ),
            FieldDefinition(
                label="Nome do Parceiro Comercial",
                field_type="text",
                required=False,
                instruction="Nome da loja onde o link de compra foi fornecido. Máximo 100 caracteres.",
                example="Amazon Brasil"
            ),
            # ── ID Google Books ───────────────────────────────────────────
            FieldDefinition(
                label="ID Google Books",
                field_type="text",
                required=False,
                instruction=(
                    "ID do volume no Google Books. Encontrado na URL: "
                    "books.google.com/books?id=ESTE_CODIGO_AQUI. "
                    "Facilita a sincronização automática de dados pela plataforma."
                ),
                example="aRt4DwAAQBAJ"
            ),
            # ── Pré-venda ─────────────────────────────────────────────────
            FieldDefinition(
                label="Este livro está em pré-venda?",
                field_type="choice",
                required=True,
                instruction="Indique se o livro ainda não foi lançado e está em pré-venda.",
                options=["Sim", "Não"],
                example="Não"
            ),
            FieldDefinition(
                label="Data Prevista de Lançamento",
                field_type="date",
                required=False,
                instruction="Preencha apenas se o livro estiver em pré-venda. Formato: DD/MM/AAAA.",
                example="30/11/2025"
            ),
            # ── Observações ───────────────────────────────────────────────
            FieldDefinition(
                label="Observações Adicionais",
                field_type="textarea",
                required=False,
                instruction=(
                    "Qualquer informação adicional relevante sobre este livro ou sobre a solicitação "
                    "de cadastro. Mencione se há edições anteriores já cadastradas, "
                    "se é uma edição especial, etc."
                ),
                example="Esta é a edição comemorativa de 50 anos, com prefácio inédito."
            ),
        ]

    def get_instructions(self) -> list:
        return [
            (
                "📌 Política de Qualidade de Cadastro",
                (
                    "A plataforma CG Bookstore segue critérios rigorosos de qualidade para o catálogo. "
                    "Livros cadastrados devem obrigatoriamente possuir:\n"
                    "• Capa original e de alta qualidade (não imagens genéricas);\n"
                    "• ISBN válido e verificável;\n"
                    "• Sinopse com ao menos 80 caracteres;\n"
                    "• Número de páginas correto;\n"
                    "• Autor(es) devidamente identificado(s)."
                )
            ),
            (
                "🔍 Como Verificar a Capa",
                (
                    "Uma capa válida deve:\n"
                    "• Mostrar claramente o título e o nome do autor;\n"
                    "• Corresponder exatamente à edição cujo ISBN foi informado;\n"
                    "• Ter resolução mínima de 200x300 pixels;\n"
                    "• Não ser uma capa genérica (fundo branco com texto em preto sem arte).\n\n"
                    "Para verificar, pesquise o ISBN no Google Books ou Open Library "
                    "e confirme que a imagem corresponde à edição."
                )
            ),
            (
                "❌ Motivos Comuns de Rejeição",
                (
                    "Solicitações são rejeitadas quando:\n"
                    "• A capa fornecida não corresponde à edição;\n"
                    "• O ISBN não é válido ou pertence a outra obra;\n"
                    "• O livro já está cadastrado no catálogo com as mesmas informações;\n"
                    "• A sinopse é muito curta (menos de 80 caracteres) ou genérica;\n"
                    "• As informações de autor ou editora estão incorretas ou incompletas."
                )
            ),
            (
                "📧 Como Enviar",
                (
                    "Após preencher este formulário, salve o arquivo e envie para: "
                    "catalogo@cgbookstore.com — com o assunto "
                    "'Contribuição Catálogo: [Título do Livro] — ISBN [número]'. "
                    "Você também pode entrar em contato via chat da plataforma."
                )
            ),
        ]
