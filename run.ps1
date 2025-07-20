# run.ps1

# Check if virtual environment exists and activate it
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $venvPath
} else {
    Write-Host "Warning: Virtual environment not found. Make sure to run setup.ps1 first." -ForegroundColor Yellow
    Write-Host "Continuing with system Python..." -ForegroundColor Yellow
}

# Change to scripts directory
Set-Location -Path ".\scripts"

# Create analysis directory with timestamp
$timestamp = Get-Date -Format "MM-dd-yyyy_HH-mm-ss"
$analysisDir = "..\data\qq\$timestamp"
New-Item -ItemType Directory -Path $analysisDir -Force | Out-Null

# Run Zacks script
python zacks.py

# Run insider trading analysis
python scrape.py insider | python analyzer.py insider
if ($LASTEXITCODE -eq 0) {
    # Move insider results to analysis directory
    Get-ChildItem -Path . -Filter "insider_trading*.png" -ErrorAction SilentlyContinue | Move-Item -Destination $analysisDir -ErrorAction SilentlyContinue
    Move-Item -Path "insider_trading_data.csv" -Destination $analysisDir -ErrorAction SilentlyContinue
} else {
    Write-Host "Error: insider analysis failed." -ForegroundColor Red
    exit 1
}

# Run congress trading analysis
python scrape.py congress | python analyzer.py congress
if ($LASTEXITCODE -eq 0) {
    # Move congress results to analysis directory
    Get-ChildItem -Path . -Filter "congress_trading*.png" -ErrorAction SilentlyContinue | Move-Item -Destination $analysisDir -ErrorAction SilentlyContinue
    Move-Item -Path "congress_trading_data.csv" -Destination $analysisDir -ErrorAction SilentlyContinue
} else {
    Write-Host "Error: Congress analysis failed." -ForegroundColor Red
    exit 1
}

# Print output path
Write-Host "`nGenerated files in $analysisDir"

# PowerShell script equivalent to run.sh
# Change to scripts directory
Set-Location -Path "scripts"

# Create a directory to store today's analysis with time in data/qq
$ANALYSIS_DIR = "../data/qq/$(Get-Date -Format 'MM-dd-yyyy_HH-mm-ss')"
New-Item -ItemType Directory -Path $ANALYSIS_DIR -Force | Out-Null

# Run zacks.py
python zacks.py

# Run insider trading analysis pipeline
$insiderResult = python scrape.py insider | python analyzer.py insider

# Check if insider analysis was successful
if ($LASTEXITCODE -eq 0) {
    # Move insider files to the analysis directory
    Move-Item -Path "insider_trading*.png" -Destination $ANALYSIS_DIR -ErrorAction SilentlyContinue
    Move-Item -Path "insider_trading_data.csv" -Destination $ANALYSIS_DIR -ErrorAction SilentlyContinue
} else {
    Write-Host "Error: insider analysis failed." -ForegroundColor Red
    exit 1
}

# Run congress trading analysis pipeline
$congressResult = python scrape.py congress | python analyzer.py congress

# Check if congress analysis was successful
if ($LASTEXITCODE -eq 0) {
    # Move congress files to the analysis directory
    Move-Item -Path "congress_trading*.png" -Destination $ANALYSIS_DIR -ErrorAction SilentlyContinue
    Move-Item -Path "congress_trading_data.csv" -Destination $ANALYSIS_DIR -ErrorAction SilentlyContinue
} else {
    Write-Host "Error: Congress analysis failed." -ForegroundColor Red
    exit 1
}

# Display a message about the output files
Write-Host "`nGenerated files in $ANALYSIS_DIR:" -ForegroundColor Green
