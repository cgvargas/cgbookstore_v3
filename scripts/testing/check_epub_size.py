import requests
import sys

# Redirecionar stdout para arquivo UTF-8
sys.stdout = open('check_epub_size_utf8.txt', 'w', encoding='utf-8')

def check_url_size(name, url):
    print(f"\nChecking: {name}")
    print(f"URL: {url}")
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        size = int(response.headers.get('Content-Length', 0))
        content_type = response.headers.get('Content-Type', 'unknown')
        print(f"Status: {response.status_code}")
        print(f"Size: {size / 1024:.2f} KB")
        print(f"Type: {content_type}")
        print(f"Final URL: {response.url}")
    except Exception as e:
        print(f"Error: {e}")

id = "55752" # Dom Casmurro
urls = [
    ("API Result", f"https://www.gutenberg.org/ebooks/{id}.epub3.images"),
    ("Direct Images", f"https://www.gutenberg.org/cache/epub/{id}/pg{id}-images.epub"),
    ("Direct No-Images", f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.epub"),
    ("Direct Epub3", f"https://www.gutenberg.org/cache/epub/{id}/pg{id}-images.epub3"),
]

for name, url in urls:
    check_url_size(name, url)
