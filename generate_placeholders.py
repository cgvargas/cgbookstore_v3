import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Configurações de Design
# ---------------------------------------------------------------------------
FONT_PATH = r"C:\Windows\Fonts\arial.ttf"

# Gradients de cores premium
GRADIENTS = [
    # (start_color, end_color)
    ((15, 12, 27), (48, 43, 99)),      # Dark Obsidian
    ((255, 81, 47), (221, 36, 118)),   # Sunset Orange
    ((127, 0, 255), (225, 0, 255)),    # Neon Violet
    ((0, 198, 255), (0, 114, 255)),    # Ocean Blue
    ((138, 35, 135), (233, 64, 87)),   # Deep Purple/Rose
    ((34, 193, 195), (253, 187, 45)),  # Vintage Teal/Gold
    ((19, 78, 94), (113, 178, 128))    # Forest Teal
]

def draw_gradient_background(image, colors):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    c1, c2 = colors
    for y in range(height):
        # Interpolação de cor
        r = int(c1[0] + (c2[0] - c1[0]) * (y / height))
        g = int(c1[1] + (c2[1] - c1[1]) * (y / height))
        b = int(c1[2] + (c2[2] - c1[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def create_placeholder(filename, title, subtitle, category="CG.BOOKSTORE", size=(1280, 720), gradient_idx=0):
    image = Image.new("RGB", size)
    draw_gradient_background(image, GRADIENTS[gradient_idx % len(GRADIENTS)])
    
    draw = ImageDraw.Draw(image)
    width, height = size
    
    # Adicionar borda interna sutil para dar efeito de card
    draw.rectangle([15, 15, width - 15, height - 15], outline=(255, 255, 255, 30), width=2)
    
    # Carregar fontes
    try:
        font_title = ImageFont.truetype(FONT_PATH, int(height * 0.07))
        font_subtitle = ImageFont.truetype(FONT_PATH, int(height * 0.045))
        font_category = ImageFont.truetype(FONT_PATH, int(height * 0.035))
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_category = ImageFont.load_default()
        
    # Desenhar categoria no topo
    draw.text((width / 2, height * 0.2), category.upper(), fill=(255, 255, 255, 180), font=font_category, anchor="mm")
    
    # Desenhar linha divisória sutil
    draw.line([(width * 0.4, height * 0.28), (width * 0.6, height * 0.28)], fill=(255, 255, 255, 80), width=1)
    
    # Quebrar texto do título se for muito longo
    words = title.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        # Check size of line
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font_title)
        line_w = bbox[2] - bbox[0]
        if line_w > width * 0.8:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
        
    # Desenhar linhas de título
    y_start = height * 0.45 - (len(lines) - 1) * (height * 0.04)
    for i, line in enumerate(lines):
        draw.text((width / 2, y_start + i * (height * 0.095)), line.upper(), fill=(255, 255, 255), font=font_title, anchor="mm")
        
    # Desenhar subtítulo
    draw.text((width / 2, height * 0.75), subtitle, fill=(255, 255, 255, 200), font=font_subtitle, anchor="mm")
    
    # Salvar
    os.makedirs("generated_placeholders", exist_ok=True)
    out_path = os.path.join("generated_placeholders", filename)
    
    # Se a extensão for .webp ou .png ou .jpeg, Pillow trata automaticamente
    # Se for outra coisa, forçar JPEG ou PNG
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        image.save(out_path, "JPEG", quality=90)
    elif ext == '.webp':
        image.save(out_path, "WEBP", quality=90)
    else:
        image.save(out_path, "PNG")
        
    print(f"Gerado: {out_path}")

# ---------------------------------------------------------------------------
# Executar a Geração
# ---------------------------------------------------------------------------
placeholders = [
    # Horizontal Images (1280x720)
    ("ChatGPT_Image_8_de_mai_de_2026_11_10_36.png", "VERITY", "O Thriller Psicologico de Colleen Hoover", "NOTICIA", (1280, 720), 0),
    ("ChatGPT_Image_25_de_mai_de_2026_17_47_23.png", "LORD OF THE MYSTERIES", "O Despertar do Louco", "NOTICIA", (1280, 720), 1),
    ("ChatGPT_Image_25_de_mai_de_2026_11_06_59.png", "LORD OF THE MYSTERIES", "Adaptacao e Misterios", "NOTICIA", (1280, 720), 2),
    ("ChatGPT_Image_19_de_dez_de_2025_10_06_58.png", "FUVEST 2026", "Autores Indigenas no Vestibular", "NOTICIA", (1280, 720), 3),
    ("Chainsaw-Man__The-Movie-Reze-Arc-capa.png", "CHAINSAW MAN", "The Movie: Reze Arc", "NOTICIA", (1280, 720), 4),
    ("filters_quality95formatwebp.webp", "DUEL MASTERS LOST", "Bokyaku no Taiyo", "NOTICIA", (1280, 720), 5),
    ("filters_quality95formatwebp.jpg", "MOFUSAND", "Adaptacao em Anime", "NOTICIA", (1280, 720), 6),
    ("filters_quality_95_format_webp_1.jpg", "CG.BOOKSTORE", "Novidades Literarias", "NOTICIA", (1280, 720), 0),
    ("gjIIkr9-8qc.jpg", "YONA OF THE DAWN", "Manga & Anime", "NOTICIA", (1280, 720), 1),
    ("gjIIkr9-8qc_qIDKroz.jpg", "YONA OF THE DAWN", "Manga & Anime", "NOTICIA", (1280, 720), 1),
    ("xUDobyOVM7Q.jpg", "AKATSUKI NO YONA", "Trailer Especial", "NOTICIA", (1280, 720), 2),
    ("6LjNvjOyk6M.jpg", "CONSELHOS DE NOBEL", "Svetlana Alexievich", "NOTICIA", (1280, 720), 3),
    ("6LjNvjOyk6M_zY0gW90.jpg", "SVETLANA ALEXIEVICH", "Literatura no Exilio", "NOTICIA", (1280, 720), 3),
    ("0rzaGbx3V5s_UGxfw3M.jpg", "PREMIOS LITERARIOS", "Os Grandes Vencedores", "NOTICIA", (1280, 720), 4),
    ("duna_1.jpg", "DUNA", "O Universo Epico de Frank Herbert", "NOTICIA", (1280, 720), 5),
    ("bbcsvetlana-alexievich-escreve-seu-proximo-livro-no-exilio-em-berlim-alemanha-uq0ll4l6_oKeBtmN.jpg", "SVETLANA ALEXIEVICH", "Escrevendo em Berlim", "NOTICIA", (1280, 720), 3),
    ("Captura_de_tela_26-12-2025_183741_buchigire-anime_com.jpeg", "BUCHIGIRE REIJOU", "Materia Especial", "NOTICIA", (1280, 720), 6),
    ("81abJdVrdSL_AC_UF1000_1000_QL80.jpg", "LEITURAS DO ANO", "Novidades Literarias", "NOTICIA", (1280, 720), 0),
    ("71XqmYTtS1L_AC_UF1000_1000_QL80.jpg", "MUNDO DOS LIVROS", "Indicacoes e Criticas", "NOTICIA", (1280, 720), 1),
    
    # Vertical Images (720x1280)
    ("Captura_de_tela_6-12-2025_95938_www.tiktok.com.jpeg", "LIVROS IMPERDIVEIS", "TikTok Review", "REVIEW", (720, 1280), 2),
    ("Captura_de_tela_15-11-2025_84012_www_KUaQIVw.instagram.com.jpeg", "DRACULA BOOK BOX", "Instagram Reel", "REVIEW", (720, 1280), 4),
    ("Captura_de_tela_21-5-2026_161249_www_instagram_com.jpeg", "E SE EU TIVESSE DESISTIDO?", "Instagram Reel", "REVIEW", (720, 1280), 5),
    ("dbit_01_TPgqK8R.jpeg", "APRESENTACAO", "CG.BookStore", "REVIEW", (720, 1280), 6),
    
    # Wide Banner (1920x600)
    ("O_Bruxo.png", "A SAGA THE WITCHER", "O Universo de Geralt de Rivia", "UNIVERSO LITERARIO", (1920, 600), 1)
]

for filename, title, subtitle, cat, size, grad in placeholders:
    create_placeholder(filename, title, subtitle, cat, size, grad)
