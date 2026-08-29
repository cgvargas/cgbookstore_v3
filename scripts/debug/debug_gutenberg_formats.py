import requests
import json
import logging
import sys

# Redirecionar stdout para arquivo UTF-8
sys.stdout = open('debug_formats_utf8.txt', 'w', encoding='utf-8')

def debug_gutenberg_formats(query):
    print(f"\n--- Debugging Gutenberg Formats (Query: '{query}') ---")
    url = "https://gutendex.com/books"
    params = {'search': query}
    headers = {'User-Agent': 'CGBookStore/1.0 (Debug Script)'}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            print("No results found.")
            return

        print(f"Found {len(results)} books. Inspecting top 3:")
        
        for i, book in enumerate(results[:3]):
            print(f"\nBook #{i+1}: {book.get('title')} (ID: {book.get('id')})")
            print("Formats:")
            formats = book.get('formats', {})
            for mime, link in formats.items():
                print(f"  - {mime}: {link}")
                
            # Simulate our current logic
            current_epub = formats.get('application/epub+zip', '')
            print(f"Current Logic selected: {current_epub}")
            
            # Check fallback URL
            gid = book.get('id')
            fallback = f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.epub"
            print(f"Fallback URL would be: {fallback}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with a book likely to have issues or the one user tried
    debug_gutenberg_formats("Dom Casmurro")
    debug_gutenberg_formats("Pride and Prejudice")
