import sys
import os
from urllib.parse import urlparse, parse_qs, unquote
from scopus_fetcher import fetch_scopus_data  # Fixed import
from excel_writer import save_to_excel

def extract_eid_from_url(url):
    """Extract EID from various Scopus URL formats"""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    
    # Check for eid parameter in query string
    if 'eid' in query:
        eid = query['eid'][0]
        # Ensure EID has proper format
        if not eid.startswith('2-s2.0-'):
            eid = f"2-s2.0-{eid}"
        return eid
    
    # Check for EID in URL path
    if 'publications' in parsed.path:
        eid = parsed.path.strip('/').split('/')[-1]
        if not eid.startswith('2-s2.0-'):
            eid = f"2-s2.0-{eid}"
        return eid
    
    # Try to extract from display.uri pattern
    if 'display.uri' in url:
        import re
        match = re.search(r'eid=([^&]+)', url)
        if match:
            eid = match.group(1)
            if not eid.startswith('2-s2.0-'):
                eid = f"2-s2.0-{eid}"
            return eid
    
    return None

def process_url(url):
    """Process a Scopus URL and extract paper data"""
    try:
        # Clean and decode URL
        url = unquote(url.strip())
        print(f"🔗 Processing URL: {url}")
        
        # Extract EID
        eid = extract_eid_from_url(url)
        if not eid:
            print("❌ Could not extract EID from URL.")
            print("   Make sure you're on a Scopus paper page with a valid EID.")
            return False

        print(f"📝 Extracted EID: {eid}")
        print(f"🔍 Fetching paper data...")
        
        # Fetch data from Scopus API
        paper = fetch_scopus_data(url)
        if not paper:
            print("❌ Failed to fetch or parse paper data.")
            print("   Check your API key and internet connection.")
            return False

        print(f"📄 Found paper: {paper['title'][:60]}...")
        
        # Save to Excel
        save_to_excel(paper)
        print("✅ Paper saved successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error processing URL: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔬 PaperGrab CLI Tool")
    print("═" * 50)
    
    # Check if URL provided as command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"📥 Processing URL from command line...")
        success = process_url(url)
        if success:
            print("\n🎉 Done! Check ~/Documents/papers/research_papers.xlsx")
        else:
            print("\n❌ Failed to process the URL")
        return
    
    # Interactive mode
    print("💡 Tip: You can also run with a URL as argument:")
    print("   python papergrab.py \"https://www.scopus.com/record/display.uri?eid=...\"\n")
    
    while True:
        try:
            url = input("📎 Enter Scopus paper URL (or 'exit' to quit): ").strip()
            
            if url.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not url:
                print("⚠️  Please enter a valid URL")
                continue
                
            if 'scopus.com' not in url.lower():
                print("⚠️  This doesn't look like a Scopus URL")
                continue
                
            success = process_url(url)
            if success:
                print("🎉 Success! Check ~/Documents/papers/research_papers.xlsx\n")
            else:
                print("❌ Failed to process this URL\n")
                
        except KeyboardInterrupt:
            print("\n👋 Exiting due to Ctrl+C")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
