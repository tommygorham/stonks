# stonks
Cross-platform web scraper/CLI tool for returning clickable stock tickers with recent purchases in your terminal.

You can also run this in a discord server i.e., `./stonksbot.py`


### Usage (this was written in Python)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

**Run on MacOS/Linux:**
```bash
./run.sh
```

**Run on Windows:**
```powershell
.\run.ps1
```

### Output
The clickable links in your terminal route to the corresponding ticker on Yahoo Finance.

**CLI**

<img width="422" height="378" alt="cli-output" src="https://github.com/user-attachments/assets/cff0a574-b1ee-4500-be03-875b078f06e4" />


**Discord** 

<img width="473" height="507" alt="discord-output" src="https://github.com/user-attachments/assets/56a39f0f-0718-45ab-af55-3b2d47213751" />

Two csv's are also created for you data analysis people
```
congress_trading_data.csv
insider_trading_data.csv
```

### Contributing
Submit a pull request with improvements or additional features. The goal of this code is to speed up the retrieval of recent insider and congressional stock purchases
via obtaining the data programmatically & outputting clickable links to tickers in your terminal.

**NOTE: Please aim to keep the code simple, lightweight, and portable (aka easy for anyone to use on any machine)**

You may fork this and turn it into a spaceship if your heart desires.
