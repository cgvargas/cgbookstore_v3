import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gutendex_strict(query):
    print(f"\n--- Testing Gutendex STRICT (Query: '{query}') ---")
    url = "https://gutendex.com/books"
    # EXACT params from ereader/services/gutenberg.py
    params = {
        'search': query,
        'languages': 'pt,en,es',
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
                print(f"First result: {results[0].get('title')}")
            else:
                print("No results found with strict filters.")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

def test_openlibrary_strict(query):
    print(f"\n--- Testing Open Library STRICT (Query: '{query}') ---")
    url = "https://openlibrary.org/search.json"
    # EXACT params from ereader/services/openlibrary.py
    params = {
        'q': query,
        'limit': 20,
        'has_fulltext': 'true',
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
            
            # Simulate parsing logic
            parsed_count = 0
            for item in docs:
                # Logic from _parse_search_result
                key = item.get('key', '')
                work_id = key.replace('/works/', '') if key else ''
                if not work_id:
                    continue
                
                # Check for ebook access (logic that was seemingly unused but might be relevant)
                has_ebook = item.get('ebook_access', '') in ['borrowable', 'public']
                
                # Check for IA ID (crucial for epub_url)
                ia_ids = item.get('ia', [])
                
                if ia_ids:
                    parsed_count += 1
            
            print(f"Parsed {parsed_count} valid books (with IA IDs) out of {len(docs)} docs returned.")
            
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    # Test with a specific book the user might be looking for, or a generic one
    queries = ["Dom Casmurro", "Machado de Assis", "Pride and Prejudice"]
    for q in queries:
        test_gutendex_strict(q)
        test_openlibrary_strict(q)
