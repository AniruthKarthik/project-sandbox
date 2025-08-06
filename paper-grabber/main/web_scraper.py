from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re
import undetected_chromedriver as uc
from seleniumwire import webdriver  # NOTE: use seleniumwire, not plain selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.binary_location = "/usr/bin/chromium-browser"  # Adjust path if needed

    seleniumwire_options = {
        'verify_ssl': False,
        'disable_encoding': True
    }

    try:
        service = Service("/usr/bin/chromedriver")  # Adjust if needed
        driver = webdriver.Chrome(
            service=service, 
            options=options,
            seleniumwire_options=seleniumwire_options
        )
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"[WebScraper] Selenium-Wire error: {e}")
        return None


def extract_scopus_data(soup):
    """Extract data specifically from Scopus-like pages."""
    try:
        def try_select(selectors):
            for sel in selectors:
                elem = soup.select_one(sel)
                if elem:
                    return elem.get_text().strip()
            return "Unknown"

        def try_select_all(selectors, limit=10):
            for sel in selectors:
                elems = soup.select(sel)
                if elems:
                    return [e.get_text().strip() for e in elems[:limit]]
            return ["Unknown"]

        title = try_select([
            'h1.Heading-module__1zub-', 
            '.documentHeader h1', 
            'h1[data-testid="document-title"]',
            'h1'
        ])

        authors = try_select_all([
            '.author-link', 
            '.DocumentHeader-module__SlKa- a', 
            '[data-testid="author-link"]',
            '.documentHeader .author'
        ])

        year_raw = try_select([
            '.PublicationYear', 
            '[data-testid="publication-year"]', 
            '.documentHeader .year'
        ])
        year_match = re.search(r'\b(19|20)\d{2}\b', year_raw)
        year = year_match.group() if year_match else "Unknown"

        citations_raw = try_select([
            '.CitedBy-module__gWgd- span', 
            '[data-testid="cited-by-count"]', 
            '.citation-count', 
            '.citedby-link'
        ])
        citations_match = re.search(r'\d+', citations_raw)
        citations = citations_match.group() if citations_match else "Unknown"

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "citations": citations
        }

    except Exception as e:
        print(f"[WebScraper] Error extracting Scopus data: {e}")
        return None

def extract_generic_data(soup):
    """Extract data from generic academic pages."""
    try:
        title = "Unknown"
        for selector in ['h1', 'title', '.title', '.paper-title', '.article-title']:
            el = soup.select_one(selector)
            if el and len(el.get_text(strip=True)) > 5:
                title = el.get_text(strip=True)
                break

        authors = ["Unknown"]
        for selector in ['.author', '.authors a', '.author-name', '[class*="author"]', '.byline a']:
            elements = soup.select(selector)
            if elements:
                authors = [e.get_text(strip=True) for e in elements[:10]]
                break

        text = soup.get_text()
        year = "Unknown"
        for pattern in [r'\b(19|20)\d{2}\b', r'Published.*?(\d{4})', r'Copyright.*?(\d{4})']:
            match = re.search(pattern, text)
            if match:
                year = match.group(1) if match.lastindex else match.group()
                break

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "citations": "Unknown"
        }

    except Exception as e:
        print(f"[WebScraper] Error extracting generic data: {e}")
        return None

def extract(url):
    """Main function to extract paper data from a given URL."""
    if not url.startswith(('http://', 'https://')):
        print("[WebScraper] Invalid URL provided")
        return None

    driver = setup_driver()
    if not driver:
        return None

    try:
        print(f"[WebScraper] Loading URL: {url}")
        driver.get(url)

        # Wait for the page to fully load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(3)  # Buffer for dynamic content

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        domain = urlparse(url).netloc.lower()

        if 'scopus' in domain:
            data = extract_scopus_data(soup)
        else:
            data = extract_generic_data(soup)

        if not data:
            print("[WebScraper] Fallback: minimal data extraction")
            data = {
                "title": soup.title.string.strip() if soup.title else "Unknown",
                "authors": ["Unknown"],
                "year": "Unknown",
                "citations": "Unknown"
            }

        data["url"] = url
        data["domain"] = domain
        return data

    except Exception as e:
        print(f"[WebScraper] Error during extraction: {e}")
        return {
            "title": "Error - Could not extract",
            "authors": ["Unknown"],
            "year": "Unknown",
            "citations": "Unknown",
            "url": url,
            "domain": urlparse(url).netloc.lower() if url else "Unknown"
        }
    finally:
        driver.quit()

# Legacy alias
def fetch_paper_data(url):
    return extract(url)

