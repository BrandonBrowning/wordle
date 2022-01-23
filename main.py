
# TODO: deal with duplicate letters, confirmed vs in word
# TODO: detect final guess and re-incorperate google word frequency for most likely

import csv
import re

from const import WORDLE_LENGTH
from game import Game
from pygtrie import StringTrie
from repl import Repl

WORDLE_RE = re.compile(f"^[a-z]{{{WORDLE_LENGTH}}}$")
WORDLES_PATH = 'data/wordles.csv'

def fetch_wordles_from_csv(path):
    with open(path, encoding='utf-8') as f:
        return set(line[0].lower() for line in csv.reader(f) if WORDLE_RE.match(line[0]))

def fetch_wordles_from_csv_with_minimum_count(path, min_count):
    with open(path, encoding='utf-8') as f:
        pairs = list()
        for line in csv.reader(f):
            word = line[0].strip().lower()
            if WORDLE_RE.match(word):
                count = int(line[1].strip().replace(',', ''))
                if count >= min_count:
                    pairs.append([word, count])
        pairs.sort(key=lambda pair: -pair[1])
        return [pair[0] for pair in pairs]

def wordles_to_substr_frequencies(wordles):
    trie = StringTrie()
    for wordle in wordles:
        for start_i in range(WORDLE_LENGTH - 1):
            for end_i in range(start_i + 1, WORDLE_LENGTH + 1):
                key = wordle[start_i:end_i]
                trie[key] = trie.setdefault(key, 0) + 1
    return {k: v for k, v in trie.iteritems()}

if __name__ == '__main__':
    wordles = fetch_wordles_from_csv(WORDLES_PATH)
    substr_to_freq = wordles_to_substr_frequencies(wordles)
    Repl(lambda: Game(wordles, substr_to_freq)).repl()
