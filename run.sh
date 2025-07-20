#!/bin/bash
cd scripts

# Create a directory to store today's analysis with time in data/qq
ANALYSIS_DIR="../data/qq/$(date +"%m-%d-%Y_%H-%M-%S")"
mkdir -p "$ANALYSIS_DIR"

python zacks.py 

# Run insider trading analysis pipeline
python scrape.py insider | python analyzer.py insider

# Check if insider analysis was successful
if [ $? -eq 0 ]; then
  # Move insider files to the analysis directory
  mv insider_trading*.png "$ANALYSIS_DIR/" 2>/dev/null
  mv insider_trading_data.csv "$ANALYSIS_DIR/" 2>/dev/null
else
  echo "Error: insider analysis failed."
  exit 1
fi

# Run congress trading analysis pipeline
python scrape.py congress | python analyzer.py congress

# Check if congress analysis was successful
if [ $? -eq 0 ]; then
  # Move congress files to the analysis directory
  mv congress_trading*.png "$ANALYSIS_DIR/" 2>/dev/null
  mv congress_trading_data.csv "$ANALYSIS_DIR/" 2>/dev/null
else
  echo "Error: Congress analysis failed."
  exit 1
fi

# Display a message about the output files
echo -e "\nGenerated files in $ANALYSIS_DIR:"
