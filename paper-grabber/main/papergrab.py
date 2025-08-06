#!/usr/bin/env python3
# papergrab.py

import traceback
import sys
import os
import argparse
from urllib.parse import unquote
from web_scraper import extract
from excel_writer import save_to_excel, get_paper_count, export_summary

def print_banner():
    """Print a nice banner"""
    print("=" * 60)
    print("📚 PAPERGRAB - Academic Paper Bookmarklet Tool")
    print("=" * 60)

def validate_url(url):
    """Validate and clean the URL"""
    if not url:
        return None
    
    # Remove bookmarklet prefix if present
    if url.startswith("papergrab:"):
        url = url.replace("papergrab:", "")
    
    # URL decode
    url = unquote(url)
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url.strip()

def handle_bookmarklet_mode(url):
    """Handle URL passed from bookmarklet"""
    print_banner()
    print(f"📖 Processing bookmarklet request...")
    print(f"🔗 URL: {url}")
    print("-" * 60)
    
    try:
        # Extract paper data
        print("🔍 Extracting paper information...")
        data = extract(url)
        
        if not data:
            print("❌ Failed to extract paper information.")
            return False
        
        # Display extracted information
        print("\n📋 Extracted Information:")
        print(f"  Title: {data.get('title', 'Unknown')}")
        print(f"  Authors: {', '.join(data.get('authors', ['Unknown']))}")
        print(f"  Year: {data.get('year', 'Unknown')}")
        print(f"  Citations: {data.get('citations', 'Unknown')}")
        print(f"  Domain: {data.get('domain', 'Unknown')}")
        
        # Save to Excel
        print(f"\n💾 Saving to database...")
        success = save_to_excel(data)
        
        if success:
            total_papers = get_paper_count()
            print(f"✅ Success! Total papers in database: {total_papers}")
        else:
            print("❌ Failed to save to database.")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        traceback.print_exc()
        return False

def handle_interactive_mode():
    """Handle interactive mode"""
    print_banner()
    
    while True:
        print("\n📚 PaperGrab Interactive Mode")
        print("1. Add paper from URL")
        print("2. View database summary")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            url = input("Enter paper URL: ").strip()
            if url:
                url = validate_url(url)
                if url:
                    handle_bookmarklet_mode(url)
                else:
                    print("❌ Invalid URL provided.")
        
        elif choice == '2':
            export_summary()
        
        elif choice == '3':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please choose 1-3.")

def create_bookmarklet():
    """Generate the bookmarklet code"""
    bookmarklet_code = """javascript:(function(){
    var url = window.location.href;
    var title = document.title;
    var paperGrabUrl = 'papergrab:' + encodeURIComponent(url);
    
    // Try to detect if this is an academic paper page
    var isAcademicSite = /scopus|pubmed|ieee|acm|springer|elsevier|wiley|nature|science|arxiv|researchgate/i.test(window.location.hostname);
    
    if (!isAcademicSite) {
        var confirm = window.confirm('This doesn\'t appear to be an academic paper site. Continue anyway?');
        if (!confirm) return;
    }
    
    // Create a form to submit to the Python script
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = 'http://localhost:8080/papergrab';  // Adjust port as needed
    form.target = '_blank';
    
    var urlInput = document.createElement('input');
    urlInput.type = 'hidden';
    urlInput.name = 'url';
    urlInput.value = url;
    
    form.appendChild(urlInput);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
    
    // Fallback: copy to clipboard
    if (navigator.clipboard) {
        navigator.clipboard.writeText(paperGrabUrl).then(function() {
            alert('Paper URL copied to clipboard! Paste it into PaperGrab.');
        });
    } else {
        prompt('Copy this URL and paste it into PaperGrab:', paperGrabUrl);
    }
})();"""
    
    return bookmarklet_code.replace('\n', '').replace('    ', '')

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='PaperGrab - Academic Paper Bookmarklet Tool')
    parser.add_argument('url', nargs='?', help='URL to process (can include papergrab: prefix)')
    parser.add_argument('--bookmarklet', action='store_true', help='Generate bookmarklet code')
    parser.add_argument('--summary', action='store_true', help='Show database summary')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    try:
        if args.bookmarklet:
            print("📚 PaperGrab Bookmarklet Code:")
            print("-" * 60)
            print(create_bookmarklet())
            print("-" * 60)
            print("Copy the above code and create a new bookmark with it as the URL.")
            return
        
        if args.summary:
            export_summary()
            return
        
        if args.url:
            url = validate_url(args.url)
            if url:
                success = handle_bookmarklet_mode(url)
                sys.exit(0 if success else 1)
            else:
                print("❌ Invalid URL provided.")
                sys.exit(1)
        
        # Default to interactive mode if no arguments
        if args.interactive or len(sys.argv) == 1:
            handle_interactive_mode()
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        if not args.interactive:
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
