#!/usr/bin/env python3
"""
Congress Trading Data Extractor
This script fetches the congress trading table from QuiverQuant and converts it
to a pandas DataFrame with key information about each transaction
"""
import argparse
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_table(url, selector):
    """Fetch HTML table from URL"""
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.select_one(selector)
    except Exception as e:
        print(f"Error fetching table: {e}")
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
            print(f"Error parsing row: {e}")
            continue
            
    return data

def get_congress_dataframe(purchases_only=False, sort_by_recent_purchases=False):
    """
    Fetch congress trading data and return as DataFrame
    
    Args:
        purchases_only (bool): If True, filter out all sales transactions
        sort_by_recent_purchases (bool): If True, sort by most recent purchases first
        
    Returns:
        pandas.DataFrame: Congress trading data
    """
    url = 'https://www.quiverquant.com/congresstrading/'
    selector = 'table.table-congress.table-politician'
    
    table = fetch_table(url, selector)
    data = extract_congress_data(table)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Additional processing
    if not df.empty:
        # Convert dates to datetime if needed
        for date_col in ['Filed', 'Traded']:
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            except:
                pass
        
        # Filter out sales if requested
        if purchases_only:
            df = df[df['Transaction'].str.contains('Purchase', case=False, na=False)]
        
        # Remove the Filed column
        df = df.drop(columns=['Filed'])
        
        # Sort by most recent trades first if requested
        if sort_by_recent_purchases and not df.empty:
            df = df.sort_values(by='Traded', ascending=False)
    
    return df

def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description='Extract Congress trading data to DataFrame')
    parser.add_argument('--output', '-o', help='Output CSV file path')
    parser.add_argument('--preview', '-p', action='store_true', help='Preview first 10 rows')
    parser.add_argument('--purchases-only', '-P', action='store_true', 
                        help='Filter out all sales transactions')
    parser.add_argument('--recent-first', '-r', action='store_true', 
                        help='Sort by most recent trades first')
    args = parser.parse_args()
    
    print("Fetching Congress trading data...")
    df = get_congress_dataframe(
        purchases_only=args.purchases_only,
        sort_by_recent_purchases=args.recent_first
    )
    
    if df.empty:
        print("No data found or error occurred.")
        return
        
    print(f"Retrieved {len(df)} Congress trading records.")
    
    if args.purchases_only:
        print("Showing purchases only (sales filtered out).")
    
    if args.recent_first:
        print("Data sorted with most recent trades at the top.")
    
    if args.preview:
        print("\nPreview of data:")
        print(df.head(10))
    
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Data saved to {args.output}")
    
    return df

if __name__ == '__main__':
    main()
