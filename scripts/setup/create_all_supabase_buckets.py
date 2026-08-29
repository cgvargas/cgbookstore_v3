import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL", "https://xmrnlckrazptjbnmmhjj.supabase.co")
key = os.environ.get("SUPABASE_SERVICE_KEY", "")  # Service key for admin operations - set via env var

print("Conectando ao Supabase Oregon...")
try:
    client: Client = create_client(url, key)
    storage = client.storage
    print("Conectado.")
    
    buckets_to_ensure = ["book-covers", "user-avatars", "author-photos"]
    
    existing_buckets = [b.id for b in storage.list_buckets()]
    print(f"Buckets existentes: {existing_buckets}")
    
    for bucket in buckets_to_ensure:
        if bucket not in existing_buckets:
            print(f"Criando bucket '{bucket}'...")
            storage.create_bucket(bucket, options={'public': True})
            print(f"  Bucket '{bucket}' criado com sucesso e configurado como publico.")
        else:
            print(f"Bucket '{bucket}' ja existe.")
            
    print("\nLista final de buckets:")
    for b in storage.list_buckets():
        print(f"  - ID: {b.id} | Public: {b.public}")
        
except Exception as e:
    print(f"Erro ao gerenciar buckets no Supabase: {e}")
