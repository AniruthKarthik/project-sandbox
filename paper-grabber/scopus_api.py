import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SCOPUS_API_KEY")

def fetch_scopus_data(eid):
    headers = {"X-ELS-APIKey": API_KEY, "Accept": "application/json"}
    url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print("❌ API error:", resp.status_code)
        return None

    data = resp.json().get('abstracts-retrieval-response', {})
    core = data.get('coredata', {})

    return {
        "title": core.get("dc:title", "Unknown"),
        "authors": [a['ce:indexed-name'] for a in data.get('authors', {}).get('author', [])] if data.get('authors') else ["Unknown"],
        "abstract": core.get("dc:description", "N/A"),
        "year": core.get("prism:coverDate", "Unknown")[:4],
        "citations": core.get("citedby-count", "0"),
        "url": core.get("prism:url", ""),
        "eid": eid
    }

