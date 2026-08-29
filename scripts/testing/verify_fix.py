import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\ProjectDjango\cgbookstore_v3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings') # Adjust setting module if needed
django.setup()

from core.utils.google_books_api import extract_book_info
from django.utils.html import strip_tags

# Example provided by the user
html_description = """
<p><b>Obra é o oitavo volume de A<i> Roda do Tempo</i>, aclamada série de fantasia que ganhou as telas em uma superprodução do Amazon Prime Video</b></p><p>No oitavo volume da série que consagrou Robert Jordan como o maior nome da fantasia desde J.R.R. Tolkien, Elayne e Nynaeve fortalecem alianças difíceis com outras canalizadoras em nome da cooperação que pode restaurar o equilíbrio climático no mundo, libertando-o da influência arrasadora do Tenebroso. Enquanto isso, Egwene precisa encontrar uma maneira de triunfar sobre suas rivais entre as Aes Sedai rebeldes se quiser fazer frente a Elaida, que ainda mantém seu controle sobre a Torre Branca. Mas nem todas as alianças são duradouras, e Perrin, acompanhado por Faile, parte em uma jornada perigosa para deter aqueles que agora cometem atrocidades em nome de Rand.</p><p>Quando os invasores Seanchan partem em direção a Illian, o temido exército de Asha’man formado por Rand é a última esperança de impedir a dominação de seu povo. No entanto, a mácula de <i>saidin</i> ameaça a integridade de suas forças, lembrando o Dragão Renascido de que, nas guerras e disputas entre os homens, a maior vitória é sempre da Sombra.</p><p>Publicação inédita no Brasil, <i>O Caminho das Adagas</i> chega às livrarias na esteira do sucesso da série do Amazon Prime Video, estrelada por Rosamund Pike. Em mais uma obra incomparável que conquistou milhões de fãs, Robert Jordan presenteia os leitores com personagens notáveis, tramas intrincadas e uma impecável construção de mundo.</p>
"""

mock_item = {
    'id': 'test_id',
    'volumeInfo': {
        'title': 'Test Book',
        'description': html_description
    }
}

info = extract_book_info(mock_item)
description = info['description']

print("--- DESCRICAO ORIGINAL (HTML) ---")
print(html_description[:100] + "...")
print("\n--- DESCRICAO POS-PROCESSAMENTO ---")
print(description[:100] + "...")

if '<p>' not in description and '<b>' not in description:
    print("\nSUCCESS: HTML tags were stripped correctly!")
else:
    print("\nFAILURE: HTML tags are still present.")
