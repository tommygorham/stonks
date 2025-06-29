#!/bin/bash
cd scripts/qq

# Create a directory to store today's analysis with time
ANALYSIS_DIR="$(date +"%m-%d-%Y_%H-%M-%S")"
mkdir -p "$ANALYSIS_DIR"

# Run insider trading analysis pipeline
echo "Running insider trading analysis..."
python scrape.py insider | python analyzer.py insider

# Check if insider analysis was successful
if [ $? -eq 0 ]; then
  echo "insider analysis completed successfully!"
  # Move insider files to the analysis directory
  mv insider_trading*.png "$ANALYSIS_DIR/" 2>/dev/null
  mv insider_trading_data.csv "$ANALYSIS_DIR/" 2>/dev/null
else
  echo "Error: insider analysis failed."
  exit 1
fi

# Run congress trading analysis pipeline
echo "Running congress trading analysis..."
python scrape.py congress | python analyzer.py congress

# Check if congress analysis was successful
if [ $? -eq 0 ]; then
  echo "Congress analysis completed successfully!"
  # Move congress files to the analysis directory
  mv congress_trading*.png "$ANALYSIS_DIR/" 2>/dev/null
  mv congress_trading_data.csv "$ANALYSIS_DIR/" 2>/dev/null
else
  echo "Error: Congress analysis failed."
  exit 1
fi

# Display a message about the output files
echo -e "\nGenerated files in $ANALYSIS_DIR:"
ls -la "$ANALYSIS_DIR/"
