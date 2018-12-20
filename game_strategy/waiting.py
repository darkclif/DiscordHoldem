from player import Player
from game_strategy.game_strategy import GameStrategy
from logger import global_log
from game_state import *

import asyncio


class WaitingStrategy(GameStrategy):
    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        # Remove players that wanted to quit during game
        for p in self.game.pending_quits:
            self.game.players.remove(p)
        self.game.pending_quits = []

        # Check if game should start again
        await self.check_game_start()

    async def close(self):
        """ Close a new strategy """
        if self.game.delayed_start:
            # self.game.delayed_start.cancel()
            self.game.delayed_start = None

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
        if not game.get_player(user.id):
            global_log("dbg", "T[{}] Player {} want to quit. He is not at the table.".format(game.table_id, user.name))
            return

        # SUCCESS
        game.players = [p for p in game.players if p.id() != user.id]

        global_log("dbg", "T[{}] Player {} stand up.".format(game.table_id, user.name))
        await self.check_game_start()
        await game.notify_view("all")

    async def on_player_ready(self, user):
        """ Player checks ready for a game. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = True

        global_log("dbg", "T[{}] Player {} is ready.".format(game.table_id, user.name))
        await self.check_game_start()
        await game.notify_view("all")

    async def on_player_unready(self, user):
        """ Player checks unready for a game. """
        game = self.game

        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = False

        global_log("dbg", "T[{}] Player {} is unready.".format(game.table_id, user.name))
        await self.check_game_start()
        await game.notify_view("all")

    async def on_player_fold(self, user):
        """ Player fold. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "T[{}] Player {} tried to fold but game is off.".format(game.table_id, user.name))

    async def on_player_check(self, user):
        """ Player checks current bid. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "T[{}] Player {} tried to check but game is off.".format(game.table_id, user.name))

    async def on_player_raise(self, user, money, all_in=False, bb=False):
        """ Player raise his bid by given amount """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "T[{}] Player {} tried to raise but game is off.".format(game.table_id, user.name))

    #
    # GAME LOGIC FUNCTIONS
    #
    @staticmethod
    async def delayed_start(game):
        await asyncio.sleep(game.start_delay)

        with game.lock:
            ready_players = [p for p in game.players if game.player_can_play(p)]
            if len(ready_players) >= 2:
                await game.change_state(GameState.PRE_FLOP)

    async def check_game_start(self):
        """ Game should start if two or more players are ready and have money """
        game = self.game
        ready_players = [p for p in game.players if game.player_can_play(p)]

        if len(ready_players) < 2:
            if game.delayed_start:
                game.delayed_start.cancel()
                game.delayed_start = None
            global_log("dbg", "Game not started. Timer suspended.")
        else:
            if not self.game.delayed_start:
                game.delayed_start = asyncio.create_task(self.delayed_start(game))
            global_log("dbg", "Game will start in {} sec.".format(game.start_delay))
