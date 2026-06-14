import os
import requests

downloads = {
    # target_filename -> video_id
    "gjIIkr9-8qc.jpg": "gjIIkr9-8qc",
    "gjIIkr9-8qc_qIDKroz.jpg": "gjIIkr9-8qc",
    "xUDobyOVM7Q.jpg": "xUDobyOVM7Q",
    "6LjNvjOyk6M.jpg": "6LjNvjOyk6M",
    "6LjNvjOyk6M_zY0gW90.jpg": "6LjNvjOyk6M",
    "0rzaGbx3V5s_UGxfw3M.jpg": "0rzaGbx3V5s",
    "maxresdefault_1.jpg": "m08TxIsFTRI"  # Devoradores de Estrelas video id
}

os.makedirs("temp_youtube_downloads", exist_ok=True)

print("Iniciando downloads do YouTube...")
for filename, video_id in downloads.items():
    print(f"Baixando thumbnail para o video {video_id} -> {filename}...")
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    ]
    success = False
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 1000:
                with open(os.path.join("temp_youtube_downloads", filename), "wb") as f:
                    f.write(r.content)
                print(f"  [SUCESSO] Salvo em temp_youtube_downloads/{filename} ({len(r.content)} bytes)")
                success = True
                break
        except Exception as e:
            print(f"  [ERRO] Tentativa com {url} falhou: {e}")
    if not success:
        print(f"  [FALHA] Nao foi possivel baixar a thumbnail para {video_id}")
