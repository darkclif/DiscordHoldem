import asyncio

from card import Card
from game_state import GameState
from game_strategy.out_game import OutGameStrategy
from hand_namer import HandNamer
from logger import global_log
from player import Player


class EndGameStrategy(OutGameStrategy):
    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        self.game.game_view.change_printer("ingame", "end")
        await self.close_game()
        await self.game.notify_view()

    async def close(self):
        """ Close a new strategy """
        pass

    #
    #   API: External Events
    #
    async def on_player_sit(self, user, money_in=10000):
        """ Player sits at the table """
        game = self.game

        # Player already at table
        if game.get_player(user.id):
            global_log("dbg", "[{}] Player {} tried to sit. He is already there.".format(game.table_id, user.name))
            return

        # No empty seats
        free_seats = list(set(range(0, 10)) - set([p.seat_num for p in self.game.players]))
        if not len(free_seats):
            global_log("dbg", "[{}] Player {} tried to sit. Table is full.".format(game.table_id, user.name))
            return

        # SUCCESS
        game.players.append(Player(user, money_in, free_seats[0]))

        await game.notify_view()
        global_log("dbg", "[{}] Player {} sat.".format(game.table_id, user.name))

    async def on_player_quit(self, user):
        """ Player stands from the table """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            global_log("dbg", "[{}] Player {} want to quit. He is not at the table.".format(game.table_id, user.name))
            return

        # SUCCESS
        game.players.remove(player)

        global_log("dbg", "[{}] Player {} stand up.".format(game.table_id, user.name))
        await game.notify_view()

    async def on_player_ready(self, user):
        """ Player checks ready for a game. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = True

        global_log("dbg", "[{}] Player {} is ready.".format(game.table_id, user.name))
        await game.notify_view()

    async def on_player_unready(self, user):
        """ Player checks unready for a game. """
        game = self.game

        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = False

        global_log("dbg", "[{}] Player {} is unready.".format(game.table_id, user.name))
        await game.notify_view()

    #
    # GAME LOGIC FUNCTIONS
    #
    @staticmethod
    async def delayed_end(game):
        await asyncio.sleep(game.end_time)

        with game.lock:
            await game.change_state(GameState.WAITING)

    async def close_game(self):
        global_log("dbg", "Game ended!")
        game = self.game

        # TODO: Split pot among players when tie.

        # Calculate outcome
        players = [p for p in game.in_game_players if not p.fold]
        players.sort(key=lambda p: p.best_hand, reverse=True)

        winner = players[0]

        # Print winner
        hand_name = HandNamer.name_hand(winner.best_hand)
        cards = " ({})".format(" ".join(Card.get_string(c) for c in winner.best_cards))
        game.log("game", "PLAYER_WON", PLAYER_NAME=winner.name(), MONEY=game.get_pot(), HAND_VALUE=hand_name+cards)

        # Give money
        amount = sum(p.pot_money for p in game.in_game_players)
        for p in game.in_game_players:
            p.pot_money = 0
        winner.money += amount
        winner.prize = amount

        # Clean up
        game.in_game_players = [p for p in game.players if game.player_can_play(p)]

        asyncio.create_task(self.delayed_end(game))

