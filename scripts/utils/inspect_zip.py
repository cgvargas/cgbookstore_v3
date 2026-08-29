import zipfile
import os

zip_path = r"C:\Users\claud\OneDrive\Imagens\_Nao_Imagens\Compactados\CG.BookStore.Online.zip"

if not os.path.exists(zip_path):
    print(f"Zip file '{zip_path}' not found.")
    exit(1)

print(f"Lendo '{zip_path}'...")
with zipfile.ZipFile(zip_path, 'r') as z:
    file_list = z.namelist()
    print(f"Total de arquivos no zip: {len(file_list)}")
    print("\nPrimeiros 20 arquivos no zip:")
    for f in file_list[:20]:
        print(f"  {f}")
        
    print("\nBuscando imagens especificas que estavam faltando:")
    targets = [
        "ChatGPT_Image_8_de_mai_de_2026_11_10_36.png",
        "maxresdefault_1.jpg",
        "ChatGPT_Image_25_de_mai_de_2026_17_47_23.png",
        "ChatGPT_Image_14_de_dez_de_2025_16_15_28.png",
        "bbcsvetlana-alexievich-escreve-seu-proximo-livro-no-exilio-em-berlim-alemanha-uq0ll4l6_oKeBtmN.jpg",
        "Captura_de_tela_26-12-2025_183741_buchigire-anime_com.jpeg",
        "81abJdVrdSL_AC_UF1000_1000_QL80.jpg",
        "71XqmYTtS1L_AC_UF1000_1000_QL80.jpg",
        "duna_1.jpg",
        "filters_quality_95_format_webp_1.jpg",
        "O_Bruxo.png",
        "dbit_01_TPgqK8R.jpeg"
    ]
    
    for t in targets:
        matches = [f for f in file_list if t.lower() in f.lower()]
        if matches:
            print(f"  [ACHOU] '{t}' como:")
            for m in matches:
                print(f"    - {m}")
        else:
            print(f"  [NAO ACHOU] '{t}'")
