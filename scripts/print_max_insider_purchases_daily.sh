#!/usr/bin/env bash
# Script that prints max insider purchase from each 
# insider csv within each subfolder of data/qq 

cd ../data/qq/
for dir in */; do
  [ -d "$dir" ] || continue
  file="$dir"insider_trading_data.csv
  if [[ ! -f "$file" ]]; then
    echo "${dir%/}: no insider_purchases.csv"
    continue
  fi

  best=$(awk -F, '
    NR==1 {
      for(i=1;i<=NF;i++) if($i=="purchases") c=i
    }
    NR>1 {
      p = $c + 0
      if (p>max) { max=p; tick=$1 }
    }
    END { print tick, max }
  ' "$file")

  echo "${dir%/}: $best"
done

