
from enum import Enum
from typing import Callable, Tuple

from const import WORDLE_LENGTH
from game import Game

PRINT_N_BEST_CANDIDATES = 8
PRINT_N_WORST_CANDIDATES = 2

class CommandResult(Enum):
    SUCCESS = 0
    HELP = 1
    EXIT = 2
    NOOP = 3
    RESET = 4

class Repl:
    def __init__(self, game_factory: Callable[[], Game]):
        self.game_factory = game_factory
        self.guess: str = None
        self._game: Game = None

    @property
    def game(self):
        if self._game is None:
            self._game = self.game_factory()
        return self._game

    def repl(self):
        loop = True
        self.update_and_display_recommended_guess()
        while loop:
            result = self.repl_command()
            if result == CommandResult.HELP:
                print('commands:')
                print('  result WOr_s')
                print('    apply the result of the recommended guess')
                print('    upper case = green')
                print('    lower case = yellow')
                print('    otherwise  = gray')
                print('  guess wordl')
                print('    override the recommended guess with the given wordle')
                print('  candidates')
                print('    print out the best candidates')
                print('  reset')
                print('  exit')
            elif result == CommandResult.RESET:
                self._game = None
                self.update_and_display_recommended_guess()
            elif result == CommandResult.EXIT:
                loop = False

    def repl_command(self) -> Tuple[bool, bool]:
        line = input('> ').strip()
        tokens = line.split(' ')
        if not tokens or len(tokens) == 0:
            return CommandResult.HELP
        if tokens[0].lower() == 'result' and len(tokens) == 2:
            self.game.apply(self.guess, tokens[1])
            self.update_and_display_recommended_guess()
            return CommandResult.SUCCESS
        elif tokens[0].lower() == 'guess' and len(tokens) == 2:
            wordle = tokens[1].lower()
            if len(wordle) == WORDLE_LENGTH:
                self.guess = wordle
                return CommandResult.SUCCESS
            else:
                print('error: wordle length must be', WORDLE_LENGTH)
                return CommandResult.NOOP
        elif tokens[0].lower() == 'candidates' and len(tokens) == 1:
            best_candidates = self.game.best_candidates()
            best_slice = best_candidates[:PRINT_N_BEST_CANDIDATES]
            print('best candidates:')
            for pair in best_slice:
                print(pair[0], pair[1])
            worst_slice = best_candidates[len(best_candidates) - PRINT_N_WORST_CANDIDATES:]
            if worst_slice != best_slice:
                print('worst candidates:')
                for pair in worst_slice:
                    print(pair[0], pair[1])
            return CommandResult.SUCCESS
        elif tokens[0].lower() == 'reset':
            return CommandResult.RESET
        elif tokens[0].lower() == 'exit':
            return CommandResult.EXIT
        else:
            return CommandResult.HELP

    def update_and_display_recommended_guess(self):
        self.guess = self.game.best_candidate()
        print('recommended guess is', self.guess)