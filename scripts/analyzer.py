import sys
import pandas as pd
from collections import defaultdict
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

CONFIG = {
    'insider': {
        'title': 'insider',
        'prefix': 'insider_trading',
        'csv': 'insider_trading_data.csv'
    },
    'congress': {
        'title': 'congress',
        'prefix': 'congress_trading',
        'csv': 'congress_trading_data.csv'
    }
}

def make_yahoo_finance_links(tickers):
    """
    Convert a list of ticker symbols into clickable terminal links to Yahoo Finance.
    
    Args:
        tickers: List of ticker symbols (strings)
        
    Returns:
        List of formatted strings with clickable links for terminals that support 
        OSC 8 hyperlink escape sequences.
    """
    clickable_tickers = []
    
    for ticker in tickers:
        # Clean the ticker symbol (remove any whitespace)
        clean_ticker = ticker.strip()
        
        # Yahoo Finance URL format
        url = f"https://finance.yahoo.com/quote/{clean_ticker}"
        
        # OSC 8 escape sequence format for terminal hyperlinks
        # Format: \033]8;;URL\033\\TEXT\033]8;;\033\\
        clickable = f"\033]8;;{url}\033\\{clean_ticker}\033]8;;\033\\"
        
        clickable_tickers.append(clickable)
    
    return clickable_tickers

def make_yahoo_finance_link(ticker):
    """
    Convert a single ticker symbol into a clickable terminal link to Yahoo Finance.
    """
    clean_ticker = ticker.strip()
    url = f"https://finance.yahoo.com/quote/{clean_ticker}"
    return f"\033]8;;{url}\033\\{clean_ticker}\033]8;;\033\\"

def fetch_table(url, selector):
    """Fetch HTML table from URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.select_one(selector)
    except Exception as e:
        print(f"Error fetching table: {e}", file=sys.stderr)
        return None

def extract_congress_data(table):
    """
    Extract data from congress trading table into structured format.
    
    Returns:
        List of dictionaries containing transaction data
    """
    data = []
    
    if not table:
        return data
        
    tbody = table.find('tbody')
    if not tbody:
        return data
    
    for row in tbody.find_all('tr'):
        try:
            cells = row.find_all('td', recursive=False)
            if len(cells) < 5:  # Ensure we have enough cells
                continue
                
            # Extract ticker
            ticker_span = (cells[0].find('span', class_='positive') or 
                          cells[0].find('span', class_='negative') or 
                          cells[0].find('span'))
            ticker = ticker_span.get_text(strip=True) if ticker_span else None
            if ticker == '-' or not ticker:
                continue
                
            # Extract transaction type
            transaction_span = cells[1].find('span')
            transaction = transaction_span.get_text(strip=True) if transaction_span else None
            
            # Extract politician name
            politician = cells[2].get_text(strip=True)
            
            # Extract filing date
            filed_date = cells[3].get_text(strip=True)
            
            # Extract trade date
            trade_date = cells[4].get_text(strip=True)
            
            # Create data entry
            entry = {
                'Stock': ticker,
                'Transaction': transaction,
                'Politician': politician,
                'Filed': filed_date,
                'Traded': trade_date
            }
            
            data.append(entry)
            
        except Exception as e:
            print(f"Error parsing row: {e}", file=sys.stderr)
            continue
            
    return data

def get_recent_congress_purchases():
    """
    Fetch recent congress purchases and return formatted data
    
    Returns:
        List of formatted strings for recent congress purchases
    """
    url = 'https://www.quiverquant.com/congresstrading/'
    selector = 'table.table-congress.table-politician'
    
    table = fetch_table(url, selector)
    data = extract_congress_data(table)
    
    if not data:
        return []
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(data)
    
    # Convert dates to datetime if needed
    try:
        df['Traded'] = pd.to_datetime(df['Traded'], errors='coerce')
    except:
        pass
    
    # Filter for purchases only
    df = df[df['Transaction'].str.contains('Purchase', case=False, na=False)]
    
    # Sort by most recent trades first
    if not df.empty:
        df = df.sort_values(by='Traded', ascending=False)
    
    # Get top 5 recent purchases
    recent_purchases = []
    for _, row in df.head(5).iterrows():
        # Format the date nicely
        try:
            if pd.notna(row['Traded']):
                formatted_date = row['Traded'].strftime('%Y-%m-%d')
            else:
                formatted_date = str(row['Traded'])
        except:
            formatted_date = str(row['Traded'])
        
        # Create clickable ticker link
        clickable_ticker = make_yahoo_finance_link(row['Stock'])
        
        # Format the line
        formatted_line = f"{clickable_ticker}    {row['Transaction']}    {row['Politician']} {formatted_date}"
        recent_purchases.append(formatted_line)
    
    return recent_purchases

def parse_ticker_data(input_file=None):
    """Parse ticker data from file or stdin and return as a dictionary."""
    ticker_data = []
    
    # Read from file if specified, otherwise from stdin
    lines = []
    if input_file:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    
    # Process each line
    for line in lines:
        try:
            line = line.strip()
            if not line or line.startswith("---") or line.startswith("python"):
                continue
                
            # Parse the line: ticker purchases
            parts = line.split()
            
            if len(parts) == 2:
                # Standard case: ticker purchases
                ticker = parts[0]
                purchases = int(parts[1])
            else:
                # Handle tickers with spaces
                if parts and parts[-1].isdigit():
                    ticker = ' '.join(parts[:-1])
                    purchases = int(parts[-1])
                else:
                    print(f"Warning: Invalid format in line: {line}", file=sys.stderr)
                    continue
                
            ticker_data.append({
                'ticker': ticker,
                'purchases': purchases
            })
        except ValueError as e:
            print(f"Warning: Could not parse numbers in line: {line} - {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"Warning: Error processing line: {line} - {e}", file=sys.stderr)
            continue
    
    return ticker_data

def analyze_ticker_data(ticker_data):
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(ticker_data)
    
    if df.empty:
        return {
            'dataframe': df,
            'total_purchases': 0,
            'most_purchases': None,
            'purchases_sorted': df
        }
    
    # Calculate totals
    total_purchases = df['purchases'].sum()
    
    # Find ticker with most purchases
    most_purchases = df.loc[df['purchases'].idxmax()] if not df['purchases'].empty else None
    
    # Sort by purchases
    purchases_sorted = df.sort_values('purchases', ascending=False)
    
    return {
        'dataframe': df,
        'total_purchases': total_purchases,
        'most_purchases': most_purchases,
        'purchases_sorted': purchases_sorted
    }

def print_summary(analysis, cfg):
    """Print a summary of the analysis with clickable Yahoo Finance links."""
    # Get current date and format as MM-DD-YYYY
    current_date = datetime.now().strftime("%m-%d-%Y")
    
    if cfg['title'] == 'congress':
        # For congress, show recent detailed purchases
        print(f"--- Recent {cfg['title'].capitalize()} Purchases ({current_date}) ---")
        recent_purchases = get_recent_congress_purchases()
        for purchase in recent_purchases:
            print(purchase)
    else:
        # For insider, show top 5 tickers as before but with "Recent" in title
        print(f"--- Recent {cfg['title'].capitalize()} Purchases ({current_date}) ---")
        
        # Get top 5 tickers
        top_tickers = []
        for _, row in analysis['purchases_sorted'].iloc[:5].iterrows():
            top_tickers.append(row['ticker'])
        
        # Convert to clickable links
        clickable_tickers = make_yahoo_finance_links(top_tickers)
        
        # Print each clickable ticker
        for ticker in clickable_tickers:
            print(ticker)

def export_data(analysis, cfg):
    """Export the analyzed data to a CSV file."""
    output_file = cfg['csv']
    analysis['dataframe'].to_csv(output_file, index=False)
    #print(f"\nData exported to {output_file}")

def main():
    """Main function to run the analysis."""
    p = argparse.ArgumentParser(description='Analyze trading purchase data')
    p.add_argument('source', choices=CONFIG.keys(), help='Which dataset to analyze')
    p.add_argument('input_file', nargs='?', help='Input file (reads from stdin if not provided)')
    args = p.parse_args()
    cfg = CONFIG[args.source]
    
    if args.input_file:
        ticker_data = parse_ticker_data(args.input_file)
    else:
        ticker_data = parse_ticker_data()
    
    analysis = analyze_ticker_data(ticker_data)
    print_summary(analysis, cfg)
    
    try:
        export_data(analysis, cfg)
    except Exception as e:
        print(f"Error exporting data: {e}", file=sys.stderr)
        print("Summary analysis completed without data export.", file=sys.stderr)

if __name__ == "__main__":
    main()
