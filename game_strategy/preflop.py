from game_strategy.in_game import InGameStrategy
from logger import global_log
from game_state import *
from card import *

from random import shuffle


class PreflopStrategy(InGameStrategy):
    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        await self.begin_game()
        await self.game.notify_view()

    async def close(self):
        """ Close a new strategy """
        pass

    #
    #   API: External Events
    #
    pass

    #
    # GAME LOGIC FUNCTIONS
    #
    async def begin_game(self):
        """ Begin new game """
        game = self.game
        game.game_id += 1

        # Prepare players
        game.in_game_players = [p for p in game.players if game.player_can_play(p)]

        # Prepare deck
        game.table_cards = []
        game.deck = Card.create_deck()
        shuffle(game.deck)

        # Pass two cards and reset state
        for p in game.in_game_players:
            p.reset()
            p.cards = [game.deck.pop(), game.deck.pop()]

        await game.search_best_hand()

        # Mark starting player
        game.dealer_index = 0
        if len(game.in_game_players) == 2:
            game.curr_player_index = 0
            game.take_blinds(game.dealer_index)
        else:
            game.curr_player_index = (game.dealer_index + 3) % len(game.in_game_players)
            game.take_blinds(game.dealer_index + 1)

    async def end_phase(self):
        await self.game.change_state(GameState.FLOP)
