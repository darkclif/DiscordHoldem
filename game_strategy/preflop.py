from game_strategy.waiting import WaitingStrategy
from logger import global_log
from card import *

from random import shuffle


class PreflopStrategy(WaitingStrategy):
    def __init__(self, game):
        super().__init__(game)

    # async def on_player_sit(self, user, money_in=10000):
    # async def on_player_ready(self, user):
    # async def on_player_unready(self, user):

    async def setup(self):
        """ Bootstrap a new strategy """
        await self.begin_game()

    async def on_player_quit(self, user):
        """ Player stands from the table """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            global_log("dbg", "T[{}] Player {} want to quit but he's not at the table.".format(player.get_name(), self.game.table_id))
            return

        # Cannot stand up because game is in progress
        if user.id in [p.id() for p in self.game.active_players]:
            global_log("dbg", "T[{}] Player {} queued for quit.".format(user.name, self.game.table_id))

            # Queue for stand up on WAITING state
            self.game.pending_quits.append(player)
            return

        # SUCCESS
        self.game.players.remove(player)

        await self.game.notify_view("all")
        global_log("dbg", "Player {} stand up from {}.".format(user.name, self.game.table_id))

    async def on_player_fold(self, user):
        """ Player fold. """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # Check for current turn
        if not self.game.get_current_player() == player:
            return

        # SUCCESS
        await self.player_fold(player)
        global_log("dbg", "Player {} folded.".format(user.name, self.game.table_id))

    async def on_player_check(self, user):
        """ Player checks current bid. """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # Check for current turn
        if not self.game.get_current_player() == player:
            return

        # SUCCESS
        await self.player_check(player)
        global_log("dbg", "Player {} checked.".format(user.name, self.game.table_id))

    async def on_player_raise(self, user, money=None):
        """ Player raise his bid by given amount """
        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # Check for current turn
        if not self.game.get_current_player() == player:
            return

        # SUCCESS
        await self.player_raise(player)
        global_log("dbg", "Player {} raised.".format(user.name, self.game.table_id))

    #
    # GAME LOGIC FUNCTIONS
    #
    async def begin_game(self):
        """ Begin new game """
        game = self.game

        # Prepare deck
        game.deck = Card.create_deck()
        shuffle(game.deck)

        # Pass two cards to players
        for p in game.active_players:
            p.set_cards([game.deck.pop(), game.deck.pop()])

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
        """ Player check to highest bid """
        game = self.game

        diff = game.get_highest_bid() - player.get_pot_money()
        if not player.take_pot_money(diff):
            player.set_all_in()
            global_log("dbg", "Player {} have not enough money. Assuming all in.".format(player.get_name()))

        player.move_to_pot(diff)
        game.next_player()
        await self.game.notify_view("all")

    async def player_fold(self, player):
        pass

    async def player_raise(self, player):
        pass
