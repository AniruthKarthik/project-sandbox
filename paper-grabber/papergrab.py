import sys
from urllib.parse import urlparse, parse_qs, unquote
from scopus_api import fetch_scopus_data
from excel_writer import save_to_excel

def extract_eid_from_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'eid' in query:
        return query['eid'][0]
    elif 'publications' in parsed.path:
        eid = parsed.path.strip('/').split('/')[-1]
        return f"2-s2.0-{eid}"
    return None

def process_url(url):
    url = unquote(url.strip())
    eid = extract_eid_from_url(url)
    if not eid:
        print("Could not extract EID from URL.")
        return

    print(f"Fetching paper data for EID: {eid}...")
    paper = fetch_scopus_data(eid)
    if not paper:
        print("Failed to fetch or parse paper data.")
        return

    save_to_excel(paper)
    print("Paper saved to Excel!")

if __name__ == "__main__":
    print("PaperGrab CLI Tool")
    print("──────────────────────────────")
    while True:
        try:
            url = input("Enter Scopus paper URL (or type 'exit' to quit): ").strip()
            if url.lower() == "exit":
                print("Exiting PaperGrab.")
                break
            if not url:
                continue
            process_url(url)
        except KeyboardInterrupt:
            print("\nExiting due to Ctrl+C")
            break
        except Exception as e:
            print(f"Error: {e}")

