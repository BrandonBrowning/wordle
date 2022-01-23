# http://wordlist.aspell.net/scowl-readme/
./mk-list english 80 | grep -E '^[a-zA-Z]{5}\s$' | awk '{print tolower($0)}' | sort | uniq | > data/wordles.csv