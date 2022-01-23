import copy
import re
from util import max_by

from const import WORDLE_LENGTH
from pygtrie import StringTrie

def wordles_to_substr_frequencies(wordles):
    trie = StringTrie()
    for wordle in wordles:
        for start_i in range(WORDLE_LENGTH - 1):
            for end_i in range(start_i + 1, WORDLE_LENGTH + 1):
                key = wordle[start_i:end_i]
                trie[key] = trie.setdefault(key, 0) + 1
    return {k: v for k, v in trie.iteritems()}

class Game:
    def __init__(self, wordles):
        self._default_confirmed = [None for _ in range(WORDLE_LENGTH)]

        self.candidates = copy.copy(wordles)
        self.confirmed = copy.copy(self._default_confirmed)
        self.eliminated = set()
        self.substr_to_freq = wordles_to_substr_frequencies(wordles)

    def apply(self, guess, result):
        for i in range(WORDLE_LENGTH):
            g = guess[i].lower()
            r = result[i]
            if r >= 'A' and r <= 'Z':
                self.confirm(g, i)
            elif r >= 'a' and r <= 'z':
                # TODO
                pass
            else:
                self.eliminate(g)
        return self.best_candidate()

    def best_candidate(self):
        self._validate_candidates()
        return max_by(self.candidates, self._score)

    def best_candidates(self):
        self._validate_candidates()
        pairs = [(wordle, self._score(wordle)) for wordle in self.candidates]
        pairs.sort(key=lambda pair: -pair[1])
        return pairs

    def confirm(self, letter, i):
        l = letter.lower()
        if self.confirmed[i] is not None and self.confirmed[i] != l:
            raise ValueError(f"already confirmed index {i} as {self.confirmed[i]}")
        else:
            self.confirmed[i] = l

    def eliminate(self, letter):
        self.eliminated.add(letter.lower())

    def _score(self, wordle):
        return sum(self.substr_to_freq[c] for c in set(wordle))

    def _validate_candidates(self):
        if self.confirmed == self._default_confirmed:
            unconfirmed_letter = '.'
        else:
            unconfirmed_letter = f"[^{''.join(c for c in self.confirmed if c is not None)}{''.join(self.eliminated)}]"
        candidate_re = re.compile(''.join(c if c is not None else unconfirmed_letter for c in self.confirmed))
        self.candidates = [wordle for wordle in self.candidates if candidate_re.match(wordle)]