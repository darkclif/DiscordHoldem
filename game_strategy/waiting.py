from player import Player
from game_strategy.game_strategy import GameStrategy
from logger import global_log
from game_state import *


class WaitingStrategy(GameStrategy):
    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        # Remove players that wanted to quit during game
        for p in self.game.pending_quits:
            self.game.players.remove(p)

    async def on_player_sit(self, user, money_in=10000):
        """ Player sits at the table """
        # Player already at table
        if self.game.get_player(user.id):
            global_log("dbg", "Player {} tried to sit at {} but he is already there.".format(user.name, self.game.table_id))
            return

        # No empty seats
        free_seats = list(set(range(0, 10)) - set([p.get_seat_num() for p in self.game.players]))
        if not len(free_seats):
            global_log("dbg", "Player {} tried to sit at {} but table is full.".format(user.name, self.game.table_id))
            return

        # SUCCESS
        self.game.players.append(Player(user, money_in, free_seats[0]))

        await self.game.notify_view("all")
        global_log("dbg", "Player {} sit at {}.".format(user.name, self.game.table_id))

    async def on_player_quit(self, user):
        """ Player stands from the table """
        # Player not at the table
        if not self.game.get_player(user.id):
            global_log("dbg", "Player {} want to quit from {} but he's not at the table.".format(user.name, self.game.table_id))
            return

        # SUCCESS
        self.game.players = [p for p in self.game.players if p.id() != user.id]

        await self.game.notify_view("all")
        global_log("dbg", "Player {} stand up from {}.".format(user.name, self.game.table_id))

    async def on_player_ready(self, user):
        """ Player checks ready for a game. """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.set_ready()
        await self.check_game_start()

        await self.game.notify_view("all")
        global_log("dbg", "Player {} is ready.".format(user.name, self.game.table_id))

    async def on_player_unready(self, user):
        """ Player checks unready for a game. """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.set_ready(False)

        await self.game.notify_view("all")
        global_log("dbg", "Player {} is unready.".format(user.name, self.game.table_id))

    async def on_player_fold(self, user):
        """ Player fold. """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "Player {} tried to fold but game is off.".format(user.name, self.game.table_id))

    async def on_player_check(self, user):
        """ Player checks current bid. """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "Player {} tried to check but game is off.".format(user.name, self.game.table_id))

    async def on_player_raise(self, user, money=None):
        """ Player raise his bid by given amount """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        global_log("dbg", "Player {} tried to raise but game is off.".format(user.name, self.game.table_id))

    #
    # GAME LOGIC FUNCTIONS
    #
    def player_can_play(self, player):
        return player.is_ready() and player.get_money() >= self.game.get_bb()

    async def check_game_start(self):
        """ Game should start if two or more players are ready and have money """
        ready_players = [p for p in self.game.players if self.player_can_play(p)]

        if len(ready_players) < 2:
            global_log("dbg", "Game tried to start but not enough players ready.")
            return

        # SUCCESS
        self.game.active_players = ready_players
        await self.game.change_state(GameState.PRE_FLOP)
