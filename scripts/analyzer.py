import sys
import pandas as pd
from collections import defaultdict
import argparse

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
    """Print a summary of the analysis."""
    # Top 5 by purchases
    print(f"--- Top 5 {cfg['title'].capitalize()} Purchases ---")
    for _, row in analysis['purchases_sorted'].iloc[:5].iterrows():
        print(row['ticker'])

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
        print(f"Error exporting data: {e}")
        print("Summary analysis completed without data export.")

if __name__ == "__main__":
    main()
