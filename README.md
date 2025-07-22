# stonks
MacOS web scraper/CLI Tool to get recent stock activity

### Description
Python Web Scraper, csv/png generator

### Setup

#### Virtual Environment Setup

**Windows:**
```powershell
# Create and setup virtual environment
.\setup.ps1 setup

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**Unix/Linux/macOS:**
```bash
# Make setup script executable
chmod +x setup.sh

# Create and setup virtual environment
./setup.sh setup

# Activate virtual environment
source venv/bin/activate
```

#### Manual Setup (Alternative)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows: .\venv\Scripts\Activate.ps1
# Unix/Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

**Windows:**
```powershell
.\run.ps1
```

**Unix/Linux/macOS:**
```bash
./run.sh
```

### Output
```
congress_trading_data.csv
congress_trading_distribution.png
congress_trading_net_activity.png
congress_trading_top_purchases.png
congress_trading_top_sales.png

insider_trading_data.csv
insider_trading_distribution.png
insider_trading_net_activity.png
insider_trading_top_purchases.png
insider_trading_top_sales.png
```

### Contributing
Submit a pull request with the powershell version of ./run.sh.

That way this can be supported on Windows.

### Virtual Environment Management

**Windows:**
```powershell
# Create virtual environment
.\setup.ps1 create

# Activate virtual environment
.\setup.ps1 activate

# Install dependencies
.\setup.ps1 install

# Remove virtual environment
.\setup.ps1 remove
```

**Unix/Linux/macOS:**
```bash
# Create virtual environment
./setup.sh create

# Activate virtual environment
./setup.sh activate

# Install dependencies
./setup.sh install

# Remove virtual environment
./setup.sh remove
```

### Troubleshooting

#### Common Issues

**1. Package Installation Errors**
If you encounter errors like "No matching distribution found", try:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install dependencies
pip install -r requirements.txt
```

**2. Python Version Compatibility**
This project requires Python 3.7+. If you have an older version:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: Use `brew install python@3.9`
- **Linux**: Use your package manager or pyenv

**3. Virtual Environment Issues**
If virtual environment creation fails:
```bash
# Remove existing venv
rm -rf venv

# Create fresh environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

**4. Permission Denied Errors (Windows)**
If you get "Permission denied" errors:
- **Run PowerShell as Administrator**
- **Close any applications** that might be using the virtual environment
- **Check antivirus software** - it might be blocking the operation
- **Try a different location** if the current directory has permission issues
- **Use the setup script** which handles these issues automatically:
  ```powershell
  .\setup.ps1 setup
  ```

#### Getting Help
- Check that Python 3.7+ is installed: `python --version`
- Ensure pip is up to date: `python -m pip install --upgrade pip`
- Try installing packages individually to identify problematic dependencies

_Word of wisdom_: Less code is better code
