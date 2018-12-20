from player import Player
from game_strategy.game_strategy import GameStrategy
from logger import global_log

from abc import *


class InGameStrategy(GameStrategy):
    def __init__(self, game):
        super().__init__(game)

    # @abstractmethod
    # async def setup(self):
    #     """ Bootstrap a new strategy """
    #     pass
    #
    # @abstractmethod
    # async def close(self):
    #     """ Close a new strategy """
    #     pass

    #
    #   API: External Events
    #
    async def on_player_sit(self, user, money_in=10000):
        """ Player sits at the table """
        game = self.game

        # Player already at table
        if game.get_player(user.id):
            global_log("dbg", "T[{}] Player {} tried to sit. He is already there.".format(game.table_id, user.name))
            return

        # No empty seats
        free_seats = list(set(range(0, 10)) - set([p.seat_num for p in self.game.players]))
        if not len(free_seats):
            global_log("dbg", "T[{}] Player {} tried to sit. Table is full.".format(game.table_id, user.name))
            return

        # SUCCESS
        game.players.append(Player(user, money_in, free_seats[0]))

        await game.notify_view("all")
        global_log("dbg", "T[{}] Player {} sat.".format(game.table_id, user.name))

    async def on_player_quit(self, user):
        """ Player stands from the table """
        game = self.game

        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            global_log("dbg", "T[{}] Player {} want to quit but he's not at the table.".format(player.name(), game.table_id))
            return

        # Cannot stand up because game is in progress
        if user.id in [p.id() for p in game.in_game_players]:
            global_log("dbg", "T[{}] Player {} queued for quit.".format(game.table_id, user.name))

            # Queue for stand up on WAITING state
            game.pending_quits.append(player)
            return

        # SUCCESS
        game.players.remove(player)

        await game.notify_view("all")
        global_log("dbg", "T[{}] Player {} stand up.".format(game.table_id, user.name))

    async def on_player_ready(self, user):
        """ Player checks ready for a game. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = True

        await game.notify_view("all")
        global_log("dbg", "T[{}] Player {} is ready.".format(game.table_id, user.name))

    async def on_player_unready(self, user):
        """ Player checks unready for a game. """
        game = self.game

        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = False

        await game.notify_view("all")
        global_log("dbg", "T[{}] Player {} is unready.".format(game.table_id, user.name))

    # @abstractmethod
    # async def on_player_fold(self, user):
    #     """ Player fold. """
    #     pass
    #
    # @abstractmethod
    # async def on_player_check(self, user):
    #     """ Player checks current bid. """
    #     pass
    #
    # @abstractmethod
    # async def on_player_raise(self, user, money=None):
    #     """ Player raise his bid by given amount """
    #     pass

    #
    # GAME LOGIC FUNCTIONS
    #
