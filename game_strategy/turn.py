from game_strategy.in_game import InGameStrategy
from logger import global_log
from game_state import *
from card import *


class TurnStrategy(InGameStrategy):
    def __init__(self, game):
        super().__init__(game)

    async def setup(self):
        """ Bootstrap a new strategy """
        # Show 3 cards
        game = self.game
        game.cards_to_table(1)
        await game.search_best_hand()
        await game.notify_view()

        for p in game.in_game_players:
            p.phase_reset()

        global_log("dbg", "[{}] Turn begin.".format(game.table_id))
        game.log("game", "NEW_PHASE_START", PHASE="Turn")

        # Set first player
        if game.get_able_players():
            game.set_first_player()
        else:
            await self.end_phase()
            return

        # Force next round
        active = game.get_active_players()
        if len(active) == 1 and active[0].pot_money >= game.get_highest_bid():
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
        await self.game.change_state(GameState.RIVER)

