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
        await self.close_game()

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
            global_log("dbg", "T[{}] Player {} tried to sit. He is already there.".format(game.table_id, user.name))
            return

        # No empty seats
        free_seats = list(set(range(0, 10)) - set([p.seat_num for p in self.game.players]))
        if not len(free_seats):
            global_log("dbg", "T[{}] Player {} tried to sit. Table is full.".format(game.table_id, user.name))
            return

        # SUCCESS
        game.players.append(Player(user, money_in, free_seats[0]))

        await game.notify_view()
        global_log("dbg", "T[{}] Player {} sat.".format(game.table_id, user.name))

    async def on_player_quit(self, user):
        """ Player stands from the table """
        game = self.game

        # Player not at the table
        player = game.get_player(user.id)
        if not player:
            global_log("dbg", "T[{}] Player {} want to quit. He is not at the table.".format(game.table_id, user.name))
            return

        # SUCCESS
        game.players.remove(player)

        global_log("dbg", "T[{}] Player {} stand up.".format(game.table_id, user.name))
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

        global_log("dbg", "T[{}] Player {} is ready.".format(game.table_id, user.name))
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

        global_log("dbg", "T[{}] Player {} is unready.".format(game.table_id, user.name))
        await game.notify_view()

    #
    # GAME LOGIC FUNCTIONS
    #
    async def close_game(self):
        global_log("dbg", "Game ended!")
        game = self.game

        # Calculate outcome
        players = [p for p in game.in_game_players if not p.fold]
        players.sort(key=lambda p: p.best_hand, reverse=True)

        player = players[0]
        hand_name = HandNamer.name_hand(player.best_hand)
        cards = " ".join([Card.get_string(c) for c in player.cards])
        game.log("game", "PLAYER_WON", PLAYER_NAME=player.name(), MONEY=game.get_pot(), HAND_VALUE=hand_name, CARDS=cards)

        await self.game.change_state(GameState.WAITING)
