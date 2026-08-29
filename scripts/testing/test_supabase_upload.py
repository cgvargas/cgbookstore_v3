from supabase import create_client, Client
import os

url = "https://xmrnlckrazptjbnmmhjj.supabase.co"
key = None  # Loaded from env in main scripts

print("Conectando ao Supabase Oregon...")
try:
    client: Client = create_client(url, key)
    storage = client.storage
    print("Conectado com sucesso.")
    
    print("\nListando buckets existentes:")
    buckets = storage.list_buckets()
    for b in buckets:
        print(f"  - ID: {b.id} | Public: {b.public}")
        
    # Check if 'book-covers' bucket exists, if not create it
    bucket_ids = [b.id for b in buckets]
    if 'book-covers' not in bucket_ids:
        print("\nCriando bucket 'book-covers'...")
        storage.create_bucket('book-covers', options={'public': True})
        print("  Bucket criado.")
    else:
        print("  Bucket 'book-covers' ja existe.")
        
except Exception as e:
    print(f"Erro: {e}")
