# stonks
Simple CLI Tools to obtain, analyze, visualize, or track data related to stocks 
## Directory: scripts/qq
This directory contains web scraping scripts written in Python to obtain stock data
### Usage
```
python qqscraper.py | python qqanalyzer.py
```
or
```
python qqscraper.py > ticker_data.txt
python qqanalyzer.py ticker_data.txt
```
### Files 
**qqscraper.py** scrapes insider stock activity from https://www.quiverquant.com/insiders/

**qqanalyzer.py** transforms the output from qqscraper.py into  visualizations
