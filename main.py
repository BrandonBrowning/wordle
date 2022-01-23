
# TODO: deal with duplicate letters, confirmed vs in word

import csv
import re

from const import WORDLE_LENGTH
from repl import Repl
from game import Game

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

if __name__ == '__main__':
    wordles = fetch_wordles_from_google_corpus_by_count(GOOGLE_CORPUS_MIN_COUNT)
    Repl(Game(wordles)).repl()
    if DEBUG:
        breakpoint()
        input('Press your any key to continue')
