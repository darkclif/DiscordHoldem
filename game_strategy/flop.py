from game_strategy.in_game import InGameStrategy
from logger import global_log
from game_state import *
from card import *


class FlopStrategy(InGameStrategy):
    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        # Show 3 cards
        game = self.game
        game.cards_to_table(3)
        await game.search_best_hand()
        await game.notify_view()

        for p in game.in_game_players:
            p.round_reset()
        game.set_first_player()

        global_log("dbg", "T[{}] Flop begin.".format(game.table_id))
        game.log("game", "NEW_PHASE_START", PHASE="Flop")

        # Force next round
        if len(game.get_able_players()) == 1:
            await self.end_phase()

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
    async def end_phase(self):
        await self.game.change_state(GameState.TURN)
