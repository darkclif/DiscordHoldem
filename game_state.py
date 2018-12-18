from enum import Enum


class GameState(Enum):
    WAITING = 0  # Players are waiting for game beginning
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    END_GAME = 5  # Temporary state at the end
