from game_strategy.in_game import InGameStrategy
from logger import global_log
from card import *

from random import shuffle


class PreflopStrategy(InGameStrategy):
    # async def on_player_sit(self, user, money_in=10000):
    # async def on_player_ready(self, user):
    # async def on_player_unready(self, user):
    # async def on_player_quit(self, user)

    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        await self.begin_game()
        await self.game.notify_view("all")

    async def close(self):
        """ Close a new strategy """
        pass

    #
    #   API: External Events
    #
    async def on_player_fold(self, user):
        """ Player fold. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # Check for current turn
        if not game.get_current_player() == player:
            return

        # SUCCESS
        await self.player_fold(player)

    async def on_player_check(self, user):
        """ Player checks current bid. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # Check for current turn
        if not game.get_current_player() == player:
            return

        # SUCCESS
        await self.player_check(player)

    async def on_player_raise(self, user, money=None):
        """ Player raise his bid by given amount """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # Check for current turn
        if not game.get_current_player() == player:
            return

        # SUCCESS
        await self.player_raise(player)

    #
    # GAME LOGIC FUNCTIONS
    #
    async def begin_game(self):
        """ Begin new game """
        game = self.game

        # Prepare players
        game.active_players = [p for p in game.players if game.player_can_play(p)]

        # Prepare deck
        game.deck = Card.create_deck()
        shuffle(game.deck)

        # Pass two cards to players
        for p in game.active_players:
            p.cards = [game.deck.pop(), game.deck.pop()]

        game.search_best_hand()

        for p in game.active_players:
            await p.update_card_message(game)

        # Mark starting player
        game.dealer_index = 0
        if len(game.active_players) == 2:
            game.curr_player_index = 0
            game.take_blinds(game.dealer_index)
        else:
            game.curr_player_index = (game.dealer_index + 3) % len(game.active_players)
            game.take_blinds(game.dealer_index + 1)

    async def player_check(self, player):
        game = self.game
        diff = game.get_highest_bid() - player.pot_money

        if diff <= player.money:
            player.move_to_pot(diff)
            global_log("dbg", "T[{}] Player {} checked.".format(game.table_id, player.name()))
        else:
            player.all_in = True
            player.move_to_pot()
            global_log("dbg", "T[{}] Player {} do not have enough money. Assuming all in.".format(game.table_id, player.name()))

        await self.next_player()
        await game.notify_view("all")

    async def player_fold(self, player):
        game = self.game

        await self.next_player()
        global_log("dbg", "T[{}] Player {} folded.".format(game.table_id, player.name()))

    async def player_raise(self, player):
        game = self.game

        await self.next_player()
        global_log("dbg", "T[{}] Player {} raised.".format(game.table_id, player.name()))

    async def next_player(self):
        game = self.game

        game.curr_player_index = (game.curr_player_index + 1)

