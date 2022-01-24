
from enum import Enum
from typing import Callable, Tuple

from const import WORDLE_LENGTH
from game import Game

class CommandResult(Enum):
    SUCCESS = 0
    HELP = 1
    EXIT = 2
    NOOP = 3
    RESET = 4

class GuessMode(Enum):
    ELIMINATE = 0
    FINISH = 1

DEFAULT_MODE = GuessMode.ELIMINATE
MINIMUM_COUNT_TO_FINISH = 25
MINIMUM_GREENS_TO_FINISH = WORDLE_LENGTH - 2
PRINT_N_BEST_CANDIDATES = 8
PRINT_N_BEST_FINISH_CANDIDATES = 5
PRINT_N_WORST_CANDIDATES = 2

class Repl:
    def __init__(self, game_factory: Callable[[], Game]):
        self.game_factory = game_factory
        self.guess: str = None
        self.mode = DEFAULT_MODE
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
                print("""
commands:
  result _g_y_
    apply the result of the recommended guess (green, yellow, and missing)
  guess wordl
    override the recommended guess with the given wordle
  candidates | wordles
    print out the best candidates
  mode finish | mode eliminate
    manually switch the mode to finish or eliminate (starts as eliminate)
  reset | restart
    begin a new game
  denied | invalid
    remove best guess as a valid word and try again
  break
    trigger a breakpoint
  debug
    toggle debug mode
  help | ?
    display this help text
  exit
""".strip())
            elif result == CommandResult.RESET:
                self._game = None
                self.set_mode(DEFAULT_MODE)
                print()
                self.update_and_display_recommended_guess()
            elif result == CommandResult.EXIT:
                loop = False

    def repl_command(self) -> Tuple[bool, bool]:
        line = input('> ').strip()
        try:
            index = line.index(' ')
            tokens = [line[0:index], line[index+1:]]
        except ValueError:
            tokens = [line] if line else []
        if not tokens or len(tokens) == 0:
            return CommandResult.HELP
        command = tokens[0].lower()
        if command == 'result' and len(tokens) == 2:
            result = tokens[1]
            result += ' ' * (WORDLE_LENGTH - len(result)) # space pad
            success = self.game.apply_colors(self.guess, result)
            if success:
                return self.update_and_display_recommended_guess()
            else:
                print('error: invalid format')
                return CommandResult.NOOP
        elif command == 'guess' and len(tokens) == 2:
            wordle = tokens[1].lower()
            if len(wordle) == WORDLE_LENGTH:
                self.guess = wordle
                return CommandResult.SUCCESS
            else:
                print('error: wordle length must be', WORDLE_LENGTH)
                return CommandResult.NOOP
        elif command in ['candidates', 'wordles'] and len(tokens) == 1:
            return self.repl_command_candidates()
        elif command == 'mode' and len(tokens) == 2:
            try:
                self.mode = GuessMode[tokens[1].upper()]
                return self.update_and_display_recommended_guess()
            except KeyError:
                pass
        elif command in ['reset', 'restart', 'retry', 'begin']:
            return CommandResult.RESET
        elif command in ['denied', 'invalid']:
            self.game.remove_candidate(self.guess)
            self.repl_command_candidates()
            return self.update_and_display_recommended_guess()
        elif command == 'break':
            breakpoint()
            return CommandResult.NOOP
        elif command == 'debug':
            self.game.debug = not self.game.debug
            print('debug mode is now', 'on' if self.game.debug else 'off')
            return CommandResult.NOOP
        elif command == 'exit':
            return CommandResult.EXIT
        return CommandResult.HELP

    def repl_command_candidates(self):
        best_candidates = self.game.best_candidates()
        best_slice = best_candidates[:PRINT_N_BEST_CANDIDATES]
        print('best candidates:')
        for pair in best_slice:
            print('', pair[0], pair[1])
        worst_slice = best_candidates[len(best_candidates) - PRINT_N_WORST_CANDIDATES:]
        if worst_slice != best_slice:
            print('worst candidates:')
            for pair in worst_slice:
                print('', pair[0], pair[1])
        return CommandResult.SUCCESS

    def set_mode(self, mode):
        if mode != self.mode:
            self.mode = mode
            print('mode set to', self.mode.name.lower())

    def update_and_display_recommended_guess(self):
        n_candidates = len(self.game.candidates)
        if n_candidates == 0:
            print('error: no wordles left; resetting')
            return CommandResult.RESET

        if self.mode == DEFAULT_MODE:
            if n_candidates <= MINIMUM_COUNT_TO_FINISH:
                print('mode switched to finish since no more than', MINIMUM_COUNT_TO_FINISH, 'candidates')
                self.mode = GuessMode.FINISH
            elif sum(1 if l is not None else 0 for l in self.game.confirmed) >= MINIMUM_GREENS_TO_FINISH:
                print('mode switched to finish since at least', MINIMUM_GREENS_TO_FINISH, 'greens')
                self.mode = GuessMode.FINISH

        if self.mode == GuessMode.ELIMINATE:
            self.guess = self.game.best_candidate()
        else:
            best_candidates_to_finish = self.game.best_candidates_to_finish()
            if n_candidates > 1:
                best_slice = best_candidates_to_finish[:PRINT_N_BEST_FINISH_CANDIDATES]
                print('best finish candidates:')
                for pair in best_slice:
                    print('', pair[0], pair[1])
            self.guess = best_candidates_to_finish[0][0]

        if n_candidates == 1:
            print(self.guess, 'is the only remaining wordle')
        else:
            print(self.guess, 'is the recommended guess of', n_candidates, 'wordles')
        return CommandResult.SUCCESS