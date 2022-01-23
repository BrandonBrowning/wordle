
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
                print("""
commands:
  result _g_y_
    apply the result of the recommended guess (green, yellow, and missing)
  guess wordl
    override the recommended guess with the given wordle
  candidates
    print out the best candidates
  reset | restart
    begin a new game
  denied
    remove best guess as a valid word and try again
  debug
    trigger a breakpoint
  exit
""".strip())
            elif result == CommandResult.RESET:
                self._game = None
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
        elif command == 'candidates' and len(tokens) == 1:
            return self.repl_command_candidates()
        elif command in ['reset', 'restart', 'retry', 'begin']:
            return CommandResult.RESET
        elif command == 'denied':
            self.game.remove_candidate(self.guess)
            self.repl_command_candidates()
            return self.update_and_display_recommended_guess()
        elif command == 'debug':
            breakpoint()
            return CommandResult.NOOP
        elif command == 'exit':
            return CommandResult.EXIT
        else:
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

    def update_and_display_recommended_guess(self):
        self.guess = self.game.best_candidate()
        if self.guess:
            print('recommended guess is', self.guess)
            return CommandResult.SUCCESS
        else:
            print('error: no wordles left; resetting')
            return CommandResult.RESET