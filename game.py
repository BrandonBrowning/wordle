import copy
import re
import sys
from typing import Dict, Set

from const import WORDLE_LENGTH
from util import max_by

class Game:
    def __init__(self, wordles, substr_to_freq, wordle_to_usage=None, debug=False):
        self._candidates = copy.copy(wordles)
        self._candidates_dirty = False
        
        self.confirmed = [None for _ in range(WORDLE_LENGTH)]
        self.debug = debug
        self.eliminated: Set[str] = set()
        self.somewhere_else: Dict[int, Set[str]] = {}
        self.substr_to_freq: Dict[str, int] = substr_to_freq
        self.wordle_to_usage: Dict[str, int] = wordle_to_usage or {}

    def apply_caps(self, guess, result):
        for i in range(WORDLE_LENGTH):
            g = guess[i].lower()
            r = result[i]
            if r >= 'A' and r <= 'Z':
                self.confirm(g, i)
            elif r >= 'a' and r <= 'z':
                self.somewhere(g, i)
            else:
                self.eliminate(g)
        return self.best_candidate()

    def apply_colors(self, guess, result) -> bool:
        for i in range(WORDLE_LENGTH):
            g = guess[i].lower()
            r = result[i]
            if r.lower() == 'g':
                self.confirm(g, i)
            elif r.lower() == 'y':
                self.somewhere(g, i)
            elif r.lower() == 'b' or r == '_' or r == ' ':
                self.eliminate(g)
            else:
                return False
        return True

    def best_candidate(self):
        if len(self.candidates) == 0:
            return None
        else:
            return max_by(self.candidates, self._score)

    def best_candidates(self):
        pairs = [(wordle, self._score(wordle)) for wordle in self.candidates]
        pairs.sort(key=lambda pair: -pair[1])
        return pairs

    def best_candidates_to_finish(self):
        pairs = [(wordle, self.wordle_to_usage.get(wordle, -sys.maxsize + self._score(wordle))) for wordle in self.candidates]
        pairs.sort(key=lambda pair: -pair[1])
        return pairs

    @property
    def candidates(self):
        if self._candidates_dirty:
            self._validate_candidates()
            self._candidates_dirty = False
        return self._candidates

    def confirm(self, letter, i):
        l = letter.lower()
        if self.confirmed[i] is not None and self.confirmed[i] != l:
            raise ValueError(f"already confirmed index {i} as {self.confirmed[i]}")
        else:
            self.confirmed[i] = l
        self._candidates_dirty = True

    def eliminate(self, letter):
        self.eliminated.add(letter.lower())
        self._candidates_dirty = True

    def remove_candidate(self, wordle):
        self._candidates.remove(wordle)
        self._candidates_dirty = True

    def somewhere(self, letter, i):
        self.somewhere_else.setdefault(i, set()).add(letter.lower())
        self._candidates_dirty = True

    def _score(self, wordle):
        return sum(self.substr_to_freq[c] for c in set(wordle))

    def _validate_candidates(self):
        candidate_regex = ''
        somewheres = set()
        for i in range(WORDLE_LENGTH):
            if self.confirmed[i] is not None:
                candidate_regex += self.confirmed[i]
            else:
                excluded = set(self.eliminated)
                # for c in self.confirmed:
                #     if c is not None:
                #         excluded.add(c)
                for j, letters in self.somewhere_else.items():
                    if i == j:
                        for letter in letters:
                            somewheres.add(letter)
                            excluded.add(letter)
                candidate_regex += f"[^{''.join(excluded)}]" if len(excluded) > 0 else '.'

        if self.debug:
            print('candidate regex is', candidate_regex)
        candidate_re = re.compile(candidate_regex)
        self._candidates = [wordle for wordle in self._candidates if candidate_re.match(wordle)]

        somewheres_count = len(somewheres)
        if somewheres_count > 0:
            new_candidates = []
            for wordle in self._candidates:
                if sum(1 if l in wordle else 0 for l in somewheres) == somewheres_count:
                    new_candidates.append(wordle)
            if self.debug:
                removed = len(self._candidates) - len(new_candidates)
                if removed == 0:
                    print('no wordles eliminated due to yellows')
                else:
                    print(removed, 'of', len(self._candidates), 'wordles eliminated due to yellows')
            self._candidates = new_candidates
