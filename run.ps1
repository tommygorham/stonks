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
