# stonks
Cross-platform web scraper/CLI Tool & Discord bot for returning clickable
stock tickers with recent purchases in your terminal or discord server 

### Description
Python Web Scraper with support for both MacOS/Linux/Windows and Discord. 

### Prerequisites
Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Usage

**MacOS/Linux:**
```bash
./run.sh
```

**Windows PowerShell:**
```powershell
.\run.ps1
```

### Output
The output is clickable links in your terminal that route to the corresponding ticker on Yahoo Finance. 

Two csv's are also created 
```
congress_trading_data.csv
insider_trading_data.csv
```

### Contributing
Submit a pull request with improvements or additional features.

The goal of this code is to speed up the retrieval of recent insider and congressional stock purchases 
via obtaining the data programmatically & outputting clickable links to tickers in your terminal. 

**NOTE: Please aim to keep the code simple, lightweight, and portable (aka easy for anyone to use on any machine)** 

You may fork this and turn it into a spaceship if your heart desires. 
