import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
            if not line or line.startswith("python"):
                continue

            # Try to parse the line more intelligently
            parts = line.split()

            # Handle case where we have too many parts (likely a hyphenated ticker)
            if len(parts) > 3:
                # Find the last two items which should be numbers
                # Everything before that is the ticker
                if parts[-1].isdigit() and parts[-2].isdigit():
                    ticker = ' '.join(parts[:-2])  # Join all parts except last two
                    sales = int(parts[-2])
                    purchases = int(parts[-1])
                else:
                    # If we can't determine which parts are numbers, skip the line
                    print(f"Warning: Could not parse line: {line}", file=sys.stderr)
                    continue
            elif len(parts) == 3:
                # Standard case: ticker sales purchases
                ticker = parts[0]
                sales = int(parts[1])
                purchases = int(parts[2])
            else:
                # Not enough parts
                print(f"Warning: Invalid format in line: {line}", file=sys.stderr)
                continue

            ticker_data.append({
                'ticker': ticker,
                'sales': sales,
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

    # Calculate totals
    total_sales = df['sales'].sum()
    total_purchases = df['purchases'].sum()

    # Find tickers with most sales and purchases
    most_sales = df.loc[df['sales'].idxmax()] if not df['sales'].empty else None
    most_purchases = df.loc[df['purchases'].idxmax()] if not df['purchases'].empty else None

    # Calculate net activity (purchases - sales)
    df['net_activity'] = df['purchases'] - df['sales']

    # Sort dataframes for various views
    sales_sorted = df.sort_values('sales', ascending=False)
    purchases_sorted = df.sort_values('purchases', ascending=False)
    net_activity_sorted = df.sort_values('net_activity')

    return {
        'dataframe': df,
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'most_sales': most_sales,
        'most_purchases': most_purchases,
        'sales_sorted': sales_sorted,
        'purchases_sorted': purchases_sorted,
        'net_activity_sorted': net_activity_sorted
    }

def print_summary(analysis, cfg):
    """Print a summary of the analysis."""
    print(f"\n===== {cfg['title']} TRADING SUMMARY =====")
    print(f"Total transactions analyzed: {len(analysis['dataframe'])}")
    print(f"Total sales: {analysis['total_sales']}")
    print(f"Total purchases: {analysis['total_purchases']}")

    if analysis['most_sales'] is not None:
        print(f"\nTicker with most sales: {analysis['most_sales']['ticker']} ({analysis['most_sales']['sales']} sales)")

    if analysis['most_purchases'] is not None:
        print(f"Ticker with most purchases: {analysis['most_purchases']['ticker']} ({analysis['most_purchases']['purchases']} purchases)")

    # Top 5 by sales
    print("\nTop 5 Tickers by Sales:")
    for i, (_, row) in enumerate(analysis['sales_sorted'].iloc[:5].iterrows(), 1):
        if row['sales'] > 0:
            print(f"{i}. {row['ticker']}: {row['sales']} sales")

    # Top 5 by purchases
    print("\nTop 5 Tickers by Purchases:")
    for i, (_, row) in enumerate(analysis['purchases_sorted'].iloc[:5].iterrows(), 1):
        if row['purchases'] > 0:
            print(f"{i}. {row['ticker']}: {row['purchases']} purchases")

    # Calculate buy/sell ratio for the market
    if analysis['total_sales'] > 0:
        buy_sell_ratio = analysis['total_purchases'] / analysis['total_sales']
        market_sentiment = "Bullish" if buy_sell_ratio > 1 else "Bearish"
        print(f"\nMarket Buy/Sell Ratio: {buy_sell_ratio:.2f} ({market_sentiment})")

def generate_visualizations(analysis, cfg):
    """Generate visualizations of the data."""
    df = analysis['dataframe']
    output_prefix = cfg['prefix']
    title = cfg['title']

    # Set matplotlib backend to avoid GUI issues
    plt.switch_backend('Agg')

    # 1. Bar chart of top 10 tickers by sales
    plt.figure(figsize=(12, 6))
    top_sales = analysis['sales_sorted'].head(10)
    if not top_sales.empty and top_sales['sales'].sum() > 0:
        # Use simple barplot without hue to avoid compatibility issues
        plt.bar(range(len(top_sales)), top_sales['sales'], color='red', alpha=0.7)
        plt.title('Top 10 Tickers by Sales')
        plt.xlabel('Tickers')
        plt.ylabel('Sales Count')
        plt.xticks(range(len(top_sales)), top_sales['ticker'], rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_prefix}_top_sales.png")
        plt.close()

    # 2. Bar chart of top 10 tickers by purchases
    plt.figure(figsize=(12, 6))
    top_purchases = analysis['purchases_sorted'].head(10)
    if not top_purchases.empty and top_purchases['purchases'].sum() > 0:
        # Use simple barplot without hue to avoid compatibility issues
        plt.bar(range(len(top_purchases)), top_purchases['purchases'], color='green', alpha=0.7)
        plt.title('Top 10 Tickers by Purchases')
        plt.xlabel('Tickers')
        plt.ylabel('Purchases Count')
        plt.xticks(range(len(top_purchases)), top_purchases['ticker'], rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_prefix}_top_purchases.png")
        plt.close()

    # 3. Net activity (purchases - sales)
    plt.figure(figsize=(14, 7))
    net_activity = df.sort_values('net_activity')
    if not net_activity.empty:
        # Create colors based on net activity
        colors = ['green' if x > 0 else 'red' for x in net_activity['net_activity']]

        # Use simple barplot
        bars = plt.bar(range(len(net_activity)), net_activity['net_activity'], color=colors, alpha=0.7)
        plt.title(f'Net {title} Activity by Ticker (Purchases - Sales)')
        plt.xlabel('Tickers')
        plt.ylabel('Net Activity (Purchases - Sales)')
        plt.xticks(range(len(net_activity)), net_activity['ticker'], rotation=90)
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_prefix}_net_activity.png")
        plt.close()

    # 4. Pie chart of total sales vs purchases
    plt.figure(figsize=(8, 8))
    labels = ['Sales', 'Purchases']
    sizes = [analysis['total_sales'], analysis['total_purchases']]
    colors = ['#ff9999','#66b3ff']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Sales vs Purchases Distribution')
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_distribution.png")
    plt.close()

def export_data(analysis, cfg):
    """Export the analyzed data to a CSV file."""
    output_file = cfg['csv']
    analysis['dataframe'].to_csv(output_file, index=False)
    print(f"\nData exported to {output_file}")

def main():
    """Main function to run the analysis."""
    p = argparse.ArgumentParser(description='Analyze trading data')
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
        generate_visualizations(analysis, cfg)
        export_data(analysis, cfg)
    except Exception as e:
        print(f"Error generating visualizations or exporting data: {e}")
        print("Summary analysis completed without visualizations.")

if __name__ == "__main__":
    main()
