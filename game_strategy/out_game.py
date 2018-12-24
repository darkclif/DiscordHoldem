from game_strategy.game_strategy import GameStrategy
from logger import global_log

from abc import *


class OutGameStrategy(GameStrategy):
    def __init__(self, game):
        super().__init__(game)

    @abstractmethod
    async def setup(self):
        """ Bootstrap a new strategy """
        pass

    @abstractmethod
    async def close(self):
        """ Close a new strategy """
        pass

    #
    #   API: External Events
    #
    @abstractmethod
    async def on_player_sit(self, user, money_in=10000):
        """ Player sits at the table """
        pass

    @abstractmethod
    async def on_player_quit(self, user):
        """ Player stands from the table """
        pass

    @abstractmethod
    async def on_player_ready(self, user):
        """ Player checks ready for a game. """
        pass

    @abstractmethod
    async def on_player_unready(self, user):
        """ Player checks unready for a game. """
        pass

    async def on_player_fold(self, user):
        """ Player fold. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "[{}] Player {} tried to fold but game is off.".format(game.table_id, user.name))

    async def on_player_check(self, user):
        """ Player checks current bid. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "[{}] Player {} tried to check but game is off.".format(game.table_id, user.name))

    async def on_player_raise(self, user, money, all_in=False, bb=False):
        """ Player raise his bid by given amount """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "[{}] Player {} tried to raise but game is off.".format(game.table_id, user.name))
    #
    # GAME LOGIC FUNCTIONS
    #
    pass
