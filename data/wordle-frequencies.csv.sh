# https://github.com/hackerb9/gwordlist/blob/master/frequency-alpha-gcide.txt
< frequency-alpha-gcide.txt grep -E '^[0-9]+\s+[a-zA-Z]{5}\s+' | tr -d '\t' | tr -s ' ' | cut -d ' ' -f 2,3 | tr -d ',' | tr ' ' ',' > wordle-frequencies.csv