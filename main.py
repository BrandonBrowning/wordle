
# TODO: deal with duplicate letters, confirmed vs in word

import csv
import re

from const import WORDLE_LENGTH
from game import Game
from pygtrie import StringTrie
from repl import Repl

DEBUG = True

GOOGLE_CORPUS_MIN_COUNT = 100_000
WORD_FREQUENCIES_PATH = 'frequency-alpha-gcide.txt'
WORDS_PATH = 'words.csv'

WORDLE_RE = re.compile(f"^[a-z]{{{WORDLE_LENGTH}}}$")

def fetch_wordles_from_etc_words():
    with open(WORDS_PATH, encoding='utf-8') as f:
        return set(line[0].lower() for line in csv.reader(f) if WORDLE_RE.match(line[0]))

def fetch_wordles_from_google_corpus_by_count(min_count):
    with open(WORD_FREQUENCIES_PATH, encoding='utf-8') as f:
        pairs = list()
        iterator = iter(f)
        next(iterator) # skip header
        for line in iterator:
            word = line[11:35].strip().lower()
            if WORDLE_RE.match(word):
                count = int(line[35:51].strip().replace(',', ''))
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
    wordles = fetch_wordles_from_google_corpus_by_count(GOOGLE_CORPUS_MIN_COUNT)
    substr_to_freq = wordles_to_substr_frequencies(wordles)
    Repl(lambda: Game(wordles, substr_to_freq)).repl()
    if DEBUG:
        breakpoint()
        input('Press your any key to continue')
