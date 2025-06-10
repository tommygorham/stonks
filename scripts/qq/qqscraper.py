import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import sys

def parse_insider_trading(url):
    """ Parse data from url, 
        Count sales & purchases by ticker, 
        Return dict [sales_count, purchases_count]
    """ 
    try:
        # Send HTTP request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the insider trading table
        table = soup.select_one('table.insider-trading-table')
        if not table:
            print("Error: Could not find insider trading table", file=sys.stderr)
            return {}
        
        # Initialize dictionary to store counts
        ticker_counts = defaultdict(lambda: [0, 0])  # [sales, purchases]
        
        # Iterate over rows in the table body
        tbody = table.find('tbody')
        if not tbody:
            print("Error: Table body not found", file=sys.stderr)
            return {}
            
        for row in tbody.find_all('tr'):
            try:
                # Extract ticker
                ticker_element = row.select_one("td a")
                if not ticker_element:
                    continue
                ticker = ticker_element.text.strip()
                
                # Extract action (sale or purchase)
                action_element = row.select_one("td:nth-of-type(3)")
                if not action_element:
                    continue
                action = action_element.text.strip()
                
                # Increment count based on action
                if action.lower() == 'sale':
                    ticker_counts[ticker][0] += 1
                elif action.lower() == 'purchase':
                    ticker_counts[ticker][1] += 1
                
            except Exception as e:
                print(f"Error processing row: {e}", file=sys.stderr)
                continue
        
        return ticker_counts
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return {}

def main():
    # URL of the webpage containing insider trading data
    url = "https://www.quiverquant.com/insiders/" 

    # Parse insider trading data
    ticker_counts = parse_insider_trading(url)
    
    # Print results in the required format: <ticker> <num-sales> <num-purchases>
    for ticker, counts in ticker_counts.items():
        print(f"{ticker} {counts[0]} {counts[1]}")

if __name__ == "__main__":
    main()
