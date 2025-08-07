import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

# Load .env file
load_dotenv()
SCOPUS_API_KEY = os.environ.get("SCOPUS_API_KEY")

def extract_abstract_text(abstract_data):
    """
    Enhanced abstract extraction to handle all possible formats
    """
    if not abstract_data:
        return "N/A"
    
    # Handle string format
    if isinstance(abstract_data, str):
        return abstract_data.strip()
    
    # Handle dictionary format
    if isinstance(abstract_data, dict):
        # Try 'para' field first
        if 'para' in abstract_data:
            para = abstract_data['para']
            if isinstance(para, str):
                return para.strip()
            elif isinstance(para, list):
                return " ".join(str(p).strip() for p in para if p)
        
        # Try 'ce:para' field
        if 'ce:para' in abstract_data:
            para = abstract_data['ce:para']
            if isinstance(para, str):
                return para.strip()
            elif isinstance(para, list):
                return " ".join(str(p).strip() for p in para if p)
        
        # Try direct text content
        if '#text' in abstract_data:
            return str(abstract_data['#text']).strip()
        
        # If it's a dict with text content, try to extract it
        for key, value in abstract_data.items():
            if isinstance(value, str) and len(value) > 50:  # Likely abstract text
                return value.strip()
    
    # Handle list format
    if isinstance(abstract_data, list):
        texts = []
        for item in abstract_data:
            if isinstance(item, str):
                texts.append(item.strip())
            elif isinstance(item, dict):
                extracted = extract_abstract_text(item)
                if extracted != "N/A":
                    texts.append(extracted)
        return " ".join(texts) if texts else "N/A"
    
    return "N/A"

def fetch_scopus_data(url):
    if not SCOPUS_API_KEY:
        print("SCOPUS_API_KEY not set in environment.")
        return None
    
    # Extract EID from URL
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    eid = query.get("eid", [None])[0]
    
    if not eid:
        print("Invalid or missing EID in URL.")
        return None
    
    api_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": SCOPUS_API_KEY
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"API error {response.status_code}: {response.text}")
            return None
        
        data = response.json().get("abstracts-retrieval-response", {})
        
        # Debug: Print the structure to see what we're working with
        print("🔍 Checking abstract locations...")
        
        core = data.get("coredata", {})
        authors_raw = data.get("authors", {}).get("author", [])
        
        # ENHANCED ABSTRACT EXTRACTION - Check multiple locations
        abstract = "N/A"
        
        # Location 1: coredata.dc:description (most common)
        if "dc:description" in core:
            abstract = extract_abstract_text(core["dc:description"])
            print(f"Found abstract in coredata.dc:description")
        
        # Location 2: item.bibrecord.head.abstracts
        if abstract == "N/A":
            bibrecord = data.get("item", {}).get("bibrecord", {})
            head = bibrecord.get("head", {})
            abstracts = head.get("abstracts", {})
            
            if "abstract" in abstracts:
                abstract = extract_abstract_text(abstracts["abstract"])
                print(f"Found abstract in bibrecord.head.abstracts")
        
        # Location 3: Direct in abstracts-retrieval-response
        if abstract == "N/A" and "abstracts" in data:
            abstract = extract_abstract_text(data["abstracts"])
            print(f"Found abstract in root abstracts")
        
        # Location 4: item.bibrecord.head.abstract (alternative path)
        if abstract == "N/A":
            try:
                head = data.get("item", {}).get("bibrecord", {}).get("head", {})
                if "abstract" in head:
                    abstract = extract_abstract_text(head["abstract"])
                    print(f"Found abstract in bibrecord.head.abstract")
            except:
                pass
        
        # Location 5: Check for 'enhancement' field (sometimes contains abstract)
        if abstract == "N/A" and "enhancement" in data:
            enhancement = data["enhancement"]
            if isinstance(enhancement, dict) and "abstract" in enhancement:
                abstract = extract_abstract_text(enhancement["abstract"])
                print(f"Found abstract in enhancement")
        
        # Final fallback: Search for any field containing substantial text
        if abstract == "N/A":
            def search_for_abstract(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, str) and len(value) > 100 and any(word in value.lower() for word in ['abstract', 'summary', 'introduction', 'conclusion']):
                            print(f"🔍 Potential abstract found at {current_path}")
                            return value.strip()
                        elif isinstance(value, (dict, list)):
                            result = search_for_abstract(value, current_path)
                            if result:
                                return result
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        result = search_for_abstract(item, f"{path}[{i}]")
                        if result:
                            return result
                return None
            
            fallback_abstract = search_for_abstract(data)
            if fallback_abstract:
                abstract = fallback_abstract
                print(f"Found abstract via fallback search")
        
        if abstract == "N/A":
            print("No abstract found in any expected location")
            # Debug: Print available keys
            print("Available top-level keys:", list(data.keys()))
            if "coredata" in data:
                print("Coredata keys:", list(data["coredata"].keys()))
        
        # Parse authors
        authors = []
        if authors_raw:
            for author in authors_raw:
                name = author.get("ce:indexed-name") or author.get("preferred-name", {}).get("ce:indexed-name") or "Unknown"
                authors.append(name)
        
        return {
            "title": core.get("dc:title", "Unknown"),
            "authors": authors or ["Unknown"],
            "abstract": abstract,
            "year": core.get("prism:coverDate", "Unknown")[:4] if core.get("prism:coverDate") else "Unknown",
            "citations": core.get("citedby-count", "0"),
            "doi": core.get("prism:doi", "N/A"),
            "publicationName": core.get("prism:publicationName", "N/A"),
            "aggregationType": core.get("prism:aggregationType", "N/A"),
            "issn": core.get("prism:issn", "N/A"),
            "volume": core.get("prism:volume", "N/A"),
            "issue": core.get("prism:issueIdentifier", "N/A"),
            "pages": core.get("prism:pageRange", "N/A"),
            "eid": core.get("eid", eid),
            "url": url
        }
        
    except Exception as e:
        print(f"Exception during API call: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test function to help debug abstract extraction
def debug_abstract_structure(url):
    """
    Debug function to print the full JSON structure to help identify where abstracts are located
    """
    if not SCOPUS_API_KEY:
        print("SCOPUS_API_KEY not set in environment.")
        return
    
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    eid = query.get("eid", [None])[0]
    
    if not eid:
        print("Invalid or missing EID in URL.")
        return
    
    api_url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    headers = {
        "Accept": "application/json",
        "X-ELS-APIKey": SCOPUS_API_KEY
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            print(f"API error {response.status_code}")
            return
        
        data = response.json()
        
        # Pretty print the structure
        import json
        print("🔍 Full API Response Structure:")
        print(json.dumps(data, indent=2)[:2000] + "..." if len(json.dumps(data, indent=2)) > 2000 else json.dumps(data, indent=2))
        
    except Exception as e:
        print(f" Exception: {e}")

# Example usage:
# result = fetch_scopus_data("your_scopus_url_here")
# if result:
#     print(f"Abstract: {result['abstract']}")
# 
# # For debugging:
# debug_abstract_structure("your_scopus_url_here")
