import os

targets = {
    # News content images (from old Supabase URLs)
    "chatgpt_image_8_de_mai_de_2026_11_10_36.png",
    "maxresdefault_1.jpg",
    "chatgpt_image_25_de_mai_de_2026_17_47_23.png",
    "chatgpt_image_14_de_dez_de_2025_16_15_28.png",
    "bbcsvetlana-alexievich-escreve-seu-proximo-livro-no-exilio-em-berlim-alemanha-uq0ll4l6_okebtmn.jpg",
    "captura_de_tela_26-12-2025_183741_buchigire-anime_com.jpeg",
    "81abjdvrdsl_ac_uf1000_1000_ql80.jpg",
    "71xqmytts1l_ac_uf1000_1000_ql80.jpg",
    "duna_1.jpg",
    "filters_quality_95_format_webp_1.jpg",
    
    # Missing R2 files (from active news_article, core_video, core_literaryuniverse)
    "gjiikr9-8qc.jpg",
    "gjiikr9-8qc_qidkroz.jpg",
    "xudobyovm7q.jpg",
    "chatgpt_image_25_de_mai_de_2026_11_06_59.png",
    "6ljnvjoyk6m.jpg",
    "filters_quality95formatwebp.jpg",
    "chatgpt_image_19_de_dez_de_2025_10_06_58.png",
    "chainsaw-man__the-movie-reze-arc-capa.png",
    "filters_quality95formatwebp.webp",
    "0rzagbx3v5s_ugxfw3m.jpg",
    "6ljnvjoyk6m_zy0gw90.jpg",
    "captura_de_tela_6-12-2025_95938_www.tiktok.com.jpeg",
    "captura_de_tela_15-11-2025_84012_www_kuaqivw.instagram.com.jpeg",
    "dbit_01_tpgqk8r.jpeg",
    "captura_de_tela_21-5-2026_161249_www_instagram_com.jpeg",
    "o_bruxo.png"
}

drives = ["C:\\", "D:\\"]
exclude_prefixes = [
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
    "c:\\users\\claud\\appdata",
    "c:\\users\\all users",
    "c:\\users\\default",
    "d:\\$recycle.bin",
    "d:\\system volume information",
    "d:\\config.msi"
]

print(f"Iniciando busca direcionada para {len(targets)} arquivos ausentes...")

found = {} # target_name_lower -> list of paths

for drive in drives:
    if not os.path.exists(drive):
        continue
    print(f"Escaneando drive {drive}...")
    for root, dirs, files in os.walk(drive):
        root_lower = root.lower()
        if any(root_lower.startswith(prefix) for prefix in exclude_prefixes):
            dirs[:] = []  # don't recurse
            continue
            
        for f in files:
            f_lower = f.lower()
            if f_lower in targets:
                if f_lower not in found:
                    found[f_lower] = []
                found[f_lower].append(os.path.join(root, f))
                print(f"  [ACHOU] {f} em: {root}")

print("\n" + "=" * 60)
print("RELATORIO DE BUSCA:")
print("=" * 60)
for t in sorted(targets):
    if t in found:
        print(f"  - {t}: ENCONTRADO em:")
        for p in found[t]:
            print(f"    {p}")
    else:
        print(f"  - {t}: NAO ENCONTRADO EM NENHUM DISCO")
print("=" * 60)
