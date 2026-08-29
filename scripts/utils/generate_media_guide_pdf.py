import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # Cabeçalho (Páginas > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#2C3E50"))
            self.drawString(54, 750, "CG.BookStore — Roteiro de Utilização: Central de Mídias & Direitos Autorais")
            self.setStrokeColor(colors.HexColor("#BDC3C7"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Rodapé em todas as páginas
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#7F8C8D"))
        self.drawString(54, 36, "CG.BookStore © 2026 — Documento de Governança Corporativa de Ativos Visuais")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 36, page_str)
        self.setStrokeColor(colors.HexColor("#BDC3C7"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()

def generate_pdf():
    pdf_filename = "Roteiro_de_Utilizacao_Central_de_Midias_CG_BookStore.pdf"
    output_path = os.path.join("c:\\ProjectDjango\\cgbookstore_v3", pdf_filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Cores Corporativas
    COLOR_PRIMARY = colors.HexColor("#1A252F")
    COLOR_SECONDARY = colors.HexColor("#2980B9")
    COLOR_ACCENT = colors.HexColor("#F39C12")
    COLOR_DARK = colors.HexColor("#2C3E50")
    COLOR_TEXT = colors.HexColor("#34495E")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=COLOR_PRIMARY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=COLOR_SECONDARY,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=4
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=COLOR_SECONDARY,
        spaceBefore=8,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=COLOR_TEXT,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=12,
        spaceAfter=2.5
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=COLOR_DARK
    )

    story = []

    # Título & Cabeçalho Principal
    story.append(Paragraph("CG.BOOKSTORE — GUIA OPERACIONAL", subtitle_style))
    story.append(Paragraph("Roteiro de Utilização: Central de Mídias Externas & Governança Visual", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_SECONDARY, spaceBefore=2, spaceAfter=10))

    # Resumo do Documento
    intro_text = (
        "Este guia prático descreve os procedimentos operacionais para utilização da <b>Central de Mídias Externas</b> "
        "e do <b>Sistema Corporativo de Governança de Direitos Autorais de Imagens</b> da CG.BookStore. "
        "Desenvolvido para ser gerenciado com máxima eficiência por uma única pessoa, o sistema assegura total conformidade "
        "jurídica, otimização de SEO e preservação da qualidade visual da plataforma."
    )
    story.append(Paragraph(intro_text, body_style))
    story.append(Spacer(1, 4))

    # SEÇÃO 1: CENTRAL DE MÍDIAS EXTERNAS
    story.append(Paragraph("1. Gestão da Central de Mídias Externas", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7"), spaceBefore=1, spaceAfter=5))
    
    sec1_text = (
        "A Central de Mídias permite cadastrar trailers, entrevistas, bastidores e gameplays organizados e reutilizáveis "
        "em toda a plataforma (Livros, Autores, Universos Literários, Artigos e Quizzes)."
    )
    story.append(Paragraph(sec1_text, body_style))

    story.append(Paragraph("1.1 Passo a Passo para Cadastro de um Novo Vídeo", h2_style))
    story.append(Paragraph("<b>1. Acesse o Painel Administrativo:</b> Vá em <i>Django Admin &gt; Central de Mídias Externas &gt; Vídeos</i> e clique em <b>Adicionar Vídeo</b>.", bullet_style))
    story.append(Paragraph("<b>2. Insira as Informações Básicas:</b> Preencha o <b>Título</b>, escolha o <b>Tipo de Mídia</b> (ex: Trailer Oficial, Entrevista, Gameplay) e redija o texto editorial completo no campo <b>Descrição</b>.", bullet_style))
    story.append(Paragraph("<b>3. Cole a URL do YouTube:</b> No campo <b>URL do Vídeo</b>, insira a URL completa (formatos suportados: <code>youtube.com/watch?v=...</code>, <code>youtu.be/...</code> ou <code>youtube.com/shorts/...</code>). O sistema extrairá automaticamente o ID e gerará a URL de embed em modo de alta privacidade (<code>youtube-nocookie.com</code>).", bullet_style))
    story.append(Paragraph("<b>4. Informe o Canal Criador:</b> Digite o <b>Nome do Canal</b> original no YouTube.", bullet_style))
    story.append(Paragraph("<b>5. Selecione os Relacionamentos:</b> Associe o vídeo aos <b>Livros</b>, <b>Autores</b> e <b>Universos Literários</b> correspondentes.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("1.2 Selo de Canal Oficial Verificado", h2_style))
    story.append(Paragraph(
        "Para evitar divulgar canais de terceiros como se fossem oficiais, o selo <b>Canal Oficial</b> só pode ser ativado "
        "quando o canal realmente pertencer ao estúdio, editora, autor ou desenvolvedora do livro/jogo. "
        "Por segurança, ao marcar a opção <i>Canal Oficial Verificado</i>, o sistema exige registrar o <b>Responsável pela Verificação</b> "
        "e a <b>Data da Verificação</b>.", body_style))

    # Tabela Informativa de Selos
    data_selos = [
        [Paragraph("<b>Status do Canal</b>", body_style), Paragraph("<b>Exibição no Site</b>", body_style), Paragraph("<b>Critério de Atribuição</b>", body_style)],
        [Paragraph("<b>Canal Oficial Verificado</b>", body_style), Paragraph("<font color='#F39C12'><b>[★ Oficial]</b></font>", body_style), Paragraph("Canal próprio do autor, editora, estúdio ou desenvolvedora.", body_style)],
        [Paragraph("<b>Canal de Terceiros</b>", body_style), Paragraph("<font color='#7F8C8D'>[Terceiros]</font>", body_style), Paragraph("Veículos de imprensa, resenhistas, canais de fãs ou agregadores (ex: IGN, Omelete).", body_style)]
    ]
    t_selos = Table(data_selos, colWidths=[130, 90, 284])
    t_selos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAEDED")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BDC3C7")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_selos)

    story.append(Spacer(1, 8))

    # SEÇÃO 2: GOVERNANÇA DE ATIVOS VISUAIS (DIREITOS AUTORAIS)
    story.append(Paragraph("2. Governança de Direitos Autorais & Procedência de Imagens", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7"), spaceBefore=1, spaceAfter=5))

    sec2_text = (
        "Sempre que enviar uma capa customizada de vídeo, banner de universo, capa de livro ou foto de autor, "
        "o formulário apresentará a seção colapsável <b>Direitos Autorais e Procedência da Imagem</b>. "
        "O preenchimento garante proteção jurídica e transparência no site público."
    )
    story.append(Paragraph(sec2_text, body_style))

    story.append(Paragraph("2.1 Como Cadastrar os Direitos da Imagem", h2_style))
    story.append(Paragraph("<b>1. Expanda a Seção no Admin:</b> Clique em <i>Direitos Autorais e Procedência da Imagem</i> abaixo do envio da imagem.", bullet_style))
    story.append(Paragraph("<b>2. Selecione o Regime de Licença:</b> Escolha entre <i>Própria / CG.BookStore</i>, <i>Licenciada / Comprada</i>, <i>Creative Commons</i>, <i>Domínio Público</i>, <i>Cortesia da Editora</i>, etc. <b>Nota:</b> Deixe em branco se a licença ainda não foi auditada.", bullet_style))
    story.append(Paragraph("<b>3. Padrão TASL (Title, Author, Source, License):</b> Para imagens <b>Creative Commons</b>, informe obrigatoriamente o <b>Título da Obra</b>, <b>Autor/Criador</b>, <b>URL da Fonte</b> e <b>URL Oficial da Licença</b>.", bullet_style))
    story.append(Paragraph("<b>4. Anexo Privado de Documento:</b> Para imagens licenciadas ou com autorização por e-mail/contrato, faça o upload no campo <b>Documento Comprobatório</b>. Este arquivo ficará armazenado em diretório estritamente privado, inacessível publicamente.", bullet_style))

    story.append(Spacer(1, 4))

    # Caixa Destaque
    callout_data = [[
        Paragraph(
            "<b>[!] REGRA DE PRIVACIDADE ABSOLUTA:</b><br/>"
            "No site público, apenas o nome do criador/crédito e o link da licença Creative Commons (padrão TASL) são exibidos discretamente. "
            "URLs da fonte original privada, documentos anexados, contratos e notas de uso <b>jamais serão expostos ao público</b>.", callout_style
        )
    ]]
    t_callout = Table(callout_data, colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF9E7")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#F39C12")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_callout)

    story.append(Spacer(1, 8))

    # SEÇÃO 3: PAINEL DE AUDITORIA E SAÚDE
    story.append(Paragraph("3. Dashboard de Auditoria & Verificação de Saúde", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7"), spaceBefore=1, spaceAfter=5))

    sec3_text = (
        "A aplicação conta com um painel de inteligência operacional acessível em <code>/admin/audit/image-copyright/</code> "
        "e ferramentas de verificação automática para prevenir links ou players quebrados."
    )
    story.append(Paragraph(sec3_text, body_style))

    story.append(Paragraph("<b>• Taxa de Atribuição & Fonte (%):</b> Mede o percentual de imagens com autor, fonte e licença devidamente identificados.", bullet_style))
    story.append(Paragraph("<b>• Taxa de Comprovação Jurídica (%):</b> Mede a porcentagem de imagens com contratos, comprovantes ou justificativas legais armazenadas.", bullet_style))
    story.append(Paragraph("<b>• Checagem Automática de Vídeos:</b> No admin de mídias, selecione os vídeos e execute a ação <i>Verificar disponibilidade/saúde das mídias selecionadas</i>. Se um vídeo for removido do YouTube, a página da CG.BookStore continua ativa preservando o SEO e o texto editorial, exibindo uma mensagem sutil ao visitante.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceBefore=2, spaceAfter=6))
    
    footer_doc = Paragraph("<b>CG.BookStore</b> — Excelente leitura, governança sólida e tecnologia de ponta.", ParagraphStyle('FootDoc', parent=body_style, fontName='Helvetica-Bold', alignment=1, textColor=COLOR_PRIMARY))
    story.append(footer_doc)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF recriado com sucesso em: {output_path}")

if __name__ == '__main__':
    generate_pdf()
