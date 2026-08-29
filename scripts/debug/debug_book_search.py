import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gutendex(query):
    print(f"\n--- Testing Gutendex (Query: '{query}') ---")
    url = "https://gutendex.com/books"
    params = {
        'search': query,
        # 'languages': 'pt,en,es', # Commented out to test without lang filter first
    }
    try:
        print(f"Requesting {url} with params {params}...")
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            results = data.get('results', [])
            print(f"Found {count} results.")
            if results:
                print(f"First result: {results[0].get('title')} by {results[0].get('authors', [{}])[0].get('name')}")
            else:
                print("No results in list.")
        else:
            print(f"Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

def test_openlibrary(query):
    print(f"\n--- Testing Open Library (Query: '{query}') ---")
    url = "https://openlibrary.org/search.json"
    params = {
        'q': query,
        'limit': 5,
        # 'has_fulltext': 'true', # Commented out to test availability
    }
    try:
        print(f"Requesting {url} with params {params}...")
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            num_found = data.get('numFound', 0)
            docs = data.get('docs', [])
            print(f"Found {num_found} results.")
            if docs:
                first = docs[0]
                print(f"First result: {first.get('title')} (Key: {first.get('key')})")
                print(f"Ebook Access: {first.get('ebook_access')}")
                print(f"Has Fulltext: {first.get('has_fulltext')}")
            else:
                print("No docs returned.")
        else:
            print(f"Error response: {response.text[:200]}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_query = "Dom Casmurro"
    test_gutendex(test_query)
    test_openlibrary(test_query)
