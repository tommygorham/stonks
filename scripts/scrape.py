# Python script that can return recent insider or congress purchases 
# USAGE: python scrape.py congress
#        python scrape.py insider
# 
import argparse
from scraper import (
    fetch_table, count_transactions,
    congress_ticker_extractor, congress_sale_detector,
    insider_ticker_extractor, insider_sale_detector
)

CONFIG = {
    'congress': {
        'url': 'https://www.quiverquant.com/congresstrading/',
        'selector': 'table.table-congress.table-politician',
        'ticker_extractor': congress_ticker_extractor,
        'sale_detector': congress_sale_detector,
    },
    'insider': {
        'url': 'https://www.quiverquant.com/insiders/', 
        'selector': 'table.insider-trading-table',
        'ticker_extractor': insider_ticker_extractor,
        'sale_detector': insider_sale_detector,
    },
}

def main():
    p = argparse.ArgumentParser(description='Scrape and count trading transactions.')
    p.add_argument('source', choices=CONFIG.keys(), help='Which dataset to scrape')
    args = p.parse_args()
    
    cfg = CONFIG[args.source]
    table = fetch_table(cfg['url'], cfg['selector'])
    if not table:
        print(f"Error: Could not find table for {args.source}")
        return
    
    counts = count_transactions(
        table, 
        cfg['ticker_extractor'], 
        cfg['sale_detector']
    )
    
    # Add a header to indicate the source of the purchases.
    print(f"--- {args.source.capitalize()} Purchases ---")
    
    # Set purchase threshold based on source
    purchase_threshold = 2 if args.source == 'congress' else 0
    
    # Print purchases, sorted by ticker
    for ticker in sorted(counts):
        sales, purchases = counts[ticker]
        if purchases > purchase_threshold:
            print(f"{ticker} {purchases}")
            #print(f"{ticker} {sales} {purchases}")

if __name__ == '__main__':
    main()
