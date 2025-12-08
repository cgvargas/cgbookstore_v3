"""
Script de teste para criar uma Crônica Semanal de exemplo no estilo jornal.
Execute: python manage.py shell < scripts/testing/test_weekly_chronicle.py
"""

from core.models import WeeklyChronicle
from django.utils import timezone
from datetime import timedelta

# Limpar crônicas anteriores (opcional)
WeeklyChronicle.objects.all().delete()

# Calcular datas da semana
today = timezone.now()
week_start = today - timedelta(days=today.weekday())  # Segunda-feira
week_end = week_start + timedelta(days=6)  # Domingo

# Criar crônica de exemplo no estilo jornal
chronicle = WeeklyChronicle.objects.create(
    # Informações da Edição
    volume_number=1,
    issue_number=1,
    week_start_date=week_start.date(),
    week_end_date=week_end.date(),
    published_date=timezone.now(),
    is_published=True,

    # Artigo Principal
    title="Os Livros Que Transformaram Minha Semana",
    subtitle="Uma jornada pessoal através das páginas que mudaram tudo",
    author_name="Carolina Vargas",

    introduction="""
Em uma semana repleta de descobertas literárias, três obras se destacaram
e transformaram completamente minha perspectiva sobre a literatura brasileira
contemporânea. Esta crônica é um relato pessoal dessas experiências que
mudaram minha forma de ler e escrever.
    """,

    main_content="""
Tudo começou na segunda-feira, quando abri pela primeira vez "Grande Sertão: Veredas"
de Guimarães Rosa. Confesso que havia adiado esta leitura por anos, intimidada
pela complexidade da linguagem. Mas ao mergulhar nas primeiras páginas, descobri
um universo de beleza incomparável.

A narrativa de Riobaldo me transportou para o sertão brasileiro, com suas veredas,
jagunços e reflexões filosóficas profundas. Cada parágrafo era uma descoberta,
cada neologismo uma janela para novas possibilidades da língua portuguesa.

Na quarta-feira, alternei a leitura com "Quarto de Despejo" de Carolina Maria de Jesus.
O contraste não poderia ser maior: da literatura erudita para o relato cru e
verdadeiro da vida na favela do Canindé nos anos 1950.
    """,

    conclusion="""
Ao final desta semana literária, percebo que os livros não apenas contam histórias
- eles nos transformam. Cada página lida é uma semente plantada em nossa consciência,
pronta para florescer em novos pensamentos e perspectivas.
    """,

    # Citação Principal
    quote="Um livro, uma caneta, uma criança e um professor podem mudar o mundo.",
    quote_author="Malala Yousafzai",

    # Destaques da Semana
    highlights_accomplishment="Finalizei a leitura de três clássicos da literatura brasileira",
    highlights_social="Participei do clube do livro mensal com amigos leitores",
    highlights_health="Mantive 30 minutos de leitura diária antes de dormir",
    highlights_learning="Descobri novas técnicas de análise literária",
    highlights_personal="Iniciei meu próprio diário de leituras",

    # Seção Casa & Família
    section_home_title="Transformando a Sala em Biblioteca Pessoal",
    section_home_content="""
Este fim de semana dediquei tempo para reorganizar minha coleção de livros.
Com a ajuda da família, instalamos novas prateleiras de madeira no canto da sala,
criando um espaço acolhedor para a leitura.

O processo foi mais do que apenas organização - foi uma redescoberta de histórias
esquecidas nas lombadas empoeiradas. Cada livro carrega memórias de quando foi lido,
presente dado ou encontrado por acaso em um sebo.

Minha filha de 8 anos escolheu seus livros favoritos para ocupar a prateleira
mais baixa, criando sua própria "seção infantil". Foi emocionante vê-la assumir
o papel de bibliotecária da casa.
    """,

    # Seção Saúde
    section_health_title="Os Benefícios da Leitura para o Bem-Estar Mental",
    section_health_content="""
Estudos recentes comprovam o que muitos leitores já sabem intuitivamente:
ler regularmente traz benefícios significativos para a saúde mental. Durante
esta semana, experimentei conscientemente os efeitos terapêuticos da leitura.

Estabeleci uma rotina de 30 minutos de leitura antes de dormir, substituindo
o hábito de rolar o feed das redes sociais. Os resultados foram notáveis:
durmo mais rápido, acordo mais descansada e tenho sonhos mais vívidos.

A leitura funciona como uma forma de meditação ativa, onde nossa mente se
concentra em uma única narrativa, bloqueando as preocupações do dia. É um
exercício de mindfulness disfarçado de entretenimento.
    """,

    # Seção Entretenimento
    section_entertainment_title="Café Literário no Centro Cultural",
    section_entertainment_content="""
Sábado à tarde participei do café literário mensal no Centro Cultural.
O tema era "Mulheres na Literatura Brasileira" e a discussão foi enriquecedora.
Conheci outros leitores apaixonados e trocamos recomendações de livros.

A experiência de discutir literatura presencialmente, olho no olho, tem um
sabor especial que as discussões online não conseguem replicar. As pausas
para o café, as expressões faciais ao mencionar um trecho favorito, tudo
contribui para a riqueza da experiência.
    """,

    # Citação Secundária
    quote_secondary="A leitura de um bom livro é um diálogo incessante: o livro fala e a alma responde.",
    quote_secondary_author="André Maurois",

    # Metadados
    meta_description="Relato pessoal de uma semana transformadora através da literatura brasileira, com reflexões sobre leitura e bem-estar.",
)

print("✅ Crônica criada com sucesso!")
print(f"📰 {chronicle.title}")
print(f"📅 Semana de {chronicle.week_start_date.strftime('%d/%m')} a {chronicle.week_end_date.strftime('%d/%m/%Y')}")
print(f"📖 Volume {chronicle.volume_number}, Edição {chronicle.issue_number}")
print(f"✍️  Autor: {chronicle.author_name}")
print(f"\n🔗 Acesse em: /cronica-semanal/")
print("\n📝 Para adicionar imagens, acesse:")
print("   Admin URL: /admin/core/weeklychronicle/")
