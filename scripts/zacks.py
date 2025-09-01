import requests
import bs4
import sys
from datetime import datetime
from typing import List, Optional

def make_yahoo_finance_link(ticker: str) -> str:
    """
    Convert a ticker symbol into a clickable terminal link to Yahoo Finance.
    
    Args:
        ticker: Ticker symbol (string)
        
    Returns:
        Formatted string with clickable link for terminals that support 
        OSC 8 hyperlink escape sequences.
    """
    # Clean the ticker symbol (remove any whitespace)
    clean_ticker = ticker.strip()
    
    # Yahoo Finance URL format
    url = f"https://finance.yahoo.com/quote/{clean_ticker}"
    
    # OSC 8 escape sequence format for terminal hyperlinks
    # Format: \033]8;;URL\033\\TEXT\033]8;;\033\\
    clickable = f"\033]8;;{url}\033\\{clean_ticker}\033]8;;\033\\"
    
    return clickable

def fetch_page_content(url: str) -> Optional[str]:
    # Using a User-Agent header is crucial to mimic a browser and avoid being blocked
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}", file=sys.stderr)
        return None

def extract_zacks_tickers(html_content: str) -> List[str]:
    soup = bs4.BeautifulSoup(html_content, "html.parser")
    tickers = []
    target_section = soup.find("section", id="zacks_number_one_rank_additions")
    if not target_section:
        print("Could not find the 'zacks_number_one_rank_additions' section.", file=sys.stderr)
        return []
    # Find all 'a' tags with a 'rel' attribute within the target section.
    ticker_links = target_section.select("a.hoverquote-container-od[rel]")
    for link in ticker_links:
        rel_value = link.get("rel")
        if rel_value:
            # The 'rel' attribute value is a list; we want the first element.
            tickers.append(rel_value[0])
    return tickers

if __name__ == "__main__":
    ZACKS_URL = "https://www.zacks.com/"
    html_content = fetch_page_content(ZACKS_URL)
    if html_content:
        extracted_tickers = extract_zacks_tickers(html_content)
        if extracted_tickers:
            # Get current date and format as MM-DD-YYYY
            current_date = datetime.now().strftime("%m-%d-%Y")
            print(f"\n--- Zacks #1 Rank Additions ({current_date}) ---")
            # Sort tickers alphabetically and convert to clickable links
            sorted_tickers = sorted(extracted_tickers)
            for ticker in sorted_tickers:
                clickable_ticker = make_yahoo_finance_link(ticker)
                print(clickable_ticker)
        else:
            print("\nCould not find any tickers in the specified section.")
    else:
        print("\nFailed to retrieve webpage. Cannot extract tickers.")
