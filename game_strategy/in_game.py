from player import Player
from game_strategy.game_strategy import GameStrategy
from logger import global_log

from abc import *


class InGameStrategy(GameStrategy):
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
        player = Player(user, money_in, free_seats[0])
        game.players.append(player)
        game.log("info", "PLAYER_SIT", PLAYER_NAME=player.name())
        await game.notify_view()

        global_log("dbg", "[{}] Player {} sat.".format(game.table_id, user.name))

    async def on_player_quit(self, user):
        """ Player stands from the table """
        game = self.game

        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            global_log("dbg", "[{}] Player {} want to quit but he's not at the table.".format(player.name(), game.table_id))
            return

        # Cannot stand up because game is in progress
        if user.id in [p.id() for p in game.in_game_players]:
            global_log("dbg", "[{}] Player {} queued for quit.".format(game.table_id, user.name))

            # Queue for stand up on WAITING state
            game.pending_quits.append(player)
            return

        # SUCCESS
        game.players.remove(player)
        game.log("info", "PLAYER_STAND", PLAYER_NAME=player.name())

        await game.notify_view()
        global_log("dbg", "[{}] Player {} stand up.".format(game.table_id, user.name))

    async def on_player_ready(self, user):
        """ Player checks ready for a game. """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = True

        await game.notify_view()
        global_log("dbg", "[{}] Player {} is ready.".format(game.table_id, user.name))

    async def on_player_unready(self, user):
        """ Player checks unready for a game. """
        game = self.game

        # Player not at the table
        player = self.game.get_player(user.id)
        if not player:
            return

        # SUCCESS
        player.ready = False

        await game.notify_view()
        global_log("dbg", "[{}] Player {} is unready.".format(game.table_id, user.name))

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

    async def on_player_raise(self, user, money, all_in=False, bb=False):
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
        await self.player_raise(player, money, all_in, bb)

    #
    # GAME LOGIC FUNCTIONS
    #
    async def player_check(self, player):
        game = self.game
        diff = game.get_highest_bid() - player.pot_money

        if diff < player.money:
            player.move_to_pot(diff)
            if diff:
                game.log("game", "PLAYER_CALLED", PLAYER_NAME=player.name())
                global_log("dbg", "[{}] Player {} called.".format(game.table_id, player.name()))
            else:
                game.log("game", "PLAYER_CHECKED", PLAYER_NAME=player.name())
                global_log("dbg", "[{}] Player {} checked.".format(game.table_id, player.name()))
        else:
            player.all_in = True
            player.move_to_pot(0, all_in=True)
            global_log("dbg", "[{}] Player {} do not have enough money. Assuming all in.".format(game.table_id, player.name()))

        player.can_decide = False
        await self.next_player()
        await game.notify_view()

    async def player_fold(self, player):
        game = self.game

        player.fold = True
        player.can_decide = False
        game.log("game", "PLAYER_FOLD", PLAYER_NAME=player.name())
        await self.next_player()

        await game.notify_view()
        global_log("dbg", "[{}] Player {} folded.".format(game.table_id, player.name()))

    async def player_raise(self, player, money, all_in, bb):
        game = self.game

        # Calculate money
        if bb:
            money = game.get_highest_bid() + game.get_bb() - player.pot_money

        # Try to take money
        if player.move_to_pot(money, all_in=all_in):
            if player.money == 0:
                # All in
                player.all_in = True
                global_log("dbg", "[{}] Player {} went all in.".format(game.table_id, player.name()))
                game.log("game", "PLAYER_ALL_IN", PLAYER_NAME=player.name())
            else:
                global_log("dbg", "[{}] Player {} raised by ${}.".format(game.table_id, player.name(), money))
                game.log("game", "PLAYER_RAISED", PLAYER_NAME=player.name(), MONEY=money)

            player.can_decide = False
            await self.next_player()
        else:
            global_log("dbg", "[{}] Player {} do not have enough money to rise (${}).".format(game.table_id, player.name(), money))

        await game.notify_view()

    @abstractmethod
    async def end_phase(self):
        pass

    async def next_player(self):
        game = self.game
        able_players = game.get_able_players()

        # Find next able players
        curr_n = (game.curr_player_index + 1) % len(game.in_game_players)
        next_players = game.in_game_players[curr_n:] + game.in_game_players[:curr_n]
        next_players = [p for p in next_players if p in able_players]

        # End phase
        active = game.get_active_players()
        if len(active) == 1 and active[0].pot_money >= game.get_highest_bid():
            await self.end_phase()
            return
        if not len(able_players):
            await self.end_phase()
            return

        # Set next
        game.curr_player_index = game.in_game_players.index(next_players[0])

