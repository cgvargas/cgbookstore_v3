import os
import sys
import django
import json
import requests

sys.path.append(r'c:\ProjectDjango\cgbookstore_v3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgbookstore.settings')
django.setup()

url = "https://www.googleapis.com/books/v1/volumes?q=harry+potter&maxResults=5"
response = requests.get(url)
data = response.json()

for item in data.get('items', []):
    vol = item.get('volumeInfo', {})
    title = vol.get('title')
    avg_rating = vol.get('averageRating')
    ratings_count = vol.get('ratingsCount')
    print(f"Título: {title}")
    print(f"avg: {avg_rating}, count: {ratings_count}")
    print("---")
