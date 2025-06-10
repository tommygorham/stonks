import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

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
        line = line.strip()
        if not line or line.startswith("python"):
            continue
        parts = line.split()
        if len(parts) >= 3:
            ticker = parts[0]
            sales = int(parts[1])
            purchases = int(parts[2])
            ticker_data.append({
                'ticker': ticker,
                'sales': sales,
                'purchases': purchases
            })
    
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

def print_summary(analysis):
    """Print a summary of the analysis."""
    print("\n===== INSIDER TRADING SUMMARY =====")
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

def generate_visualizations(analysis, output_prefix="insider_trading"):
    """Generate visualizations of the data."""
    df = analysis['dataframe']
    
    # 1. Bar chart of top 10 tickers by sales
    plt.figure(figsize=(12, 6))
    top_sales = analysis['sales_sorted'].head(10)
    sns.barplot(x='ticker', y='sales', hue='ticker', data=top_sales, palette='Reds_r', legend=False)
    plt.title('Top 10 Tickers by Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_top_sales.png")
    
    # 2. Bar chart of top 10 tickers by purchases
    plt.figure(figsize=(12, 6))
    top_purchases = analysis['purchases_sorted'].head(10)
    if not top_purchases.empty and top_purchases['purchases'].sum() > 0:
        sns.barplot(x='ticker', y='purchases', hue='ticker', data=top_purchases, palette='Greens_r', legend=False)
        plt.title('Top 10 Tickers by Purchases')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_prefix}_top_purchases.png")
    
    # 3. Net activity (purchases - sales)
    plt.figure(figsize=(14, 7))
    net_activity = df.sort_values('net_activity')
    colors = ['green' if x > 0 else 'red' for x in net_activity['net_activity']]
    # Create a new column for coloring
    net_activity['color_group'] = ['positive' if x > 0 else 'negative' for x in net_activity['net_activity']]
    sns.barplot(x='ticker', y='net_activity', hue='color_group', data=net_activity, palette={'positive': 'green', 'negative': 'red'}, legend=False)
    plt.title('Net Insider Activity by Ticker (Purchases - Sales)')
    plt.xticks(rotation=90)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_net_activity.png")
    
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
    
    print(f"\nVisualizations saved with prefix: {output_prefix}")

def export_data(analysis, output_file="insider_trading_data.csv"):
    """Export the analyzed data to a CSV file."""
    analysis['dataframe'].to_csv(output_file, index=False)
    print(f"\nData exported to {output_file}")

def main():
    """Main function to run the analysis."""
    if len(sys.argv) > 1:
        ticker_data = parse_ticker_data(sys.argv[1])
    else:
        ticker_data = parse_ticker_data()
    
    analysis = analyze_ticker_data(ticker_data)
    print_summary(analysis)
    
    try:
        generate_visualizations(analysis)
        export_data(analysis)
    except Exception as e:
        print(f"Error generating visualizations or exporting data: {e}")
        print("Summary analysis completed without visualizations.")

if __name__ == "__main__":
    main()
