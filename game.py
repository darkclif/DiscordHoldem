from functools import reduce
from threading import RLock

from player import *
from game_view import *
from game_controller import *
from game_state import *
from cards_evaluator import Evaluator

from game_strategy.waiting import *
from game_strategy.preflop import *


class Game:
    """ MVC: Game Model """
    # Map GameState to game strategy class
    strategy_mapper = {
        GameState.WAITING:  WaitingStrategy,
        GameState.PRE_FLOP: PreflopStrategy
    }

    def __init__(self, channel, table_id):
        """ Create game on given table """
        self.channel = channel
        self.players = []       # Max 9 players

        # IDs
        self.table_id = table_id
        self.game_id = 0

        # Table state
        self.table_cards = []   # max 5
        self.deck = []          # max 2

        self.small_blind = 10
        self.dealer_index = 0

        self.curr_player_index = 0      # Index of current deciding player
        self.in_game_players = []       # List of players taking part in current game
        self.game_state = GameState.WAITING

        self.pending_quits = []         # Players wanting to quit from table after current game

        # Discord API hooks
        self.hooked_msg = {}

        # MVC
        self.game_view = None
        self.game_controller = None

        # Strategy
        self.game_strategy = None

        # Threading
        self.lock = RLock()
        self.delayed_start = None
        self.start_delay = 5

    # Setup / Close
    async def setup(self):
        """ Setup MVC classes """
        # Setup MVC
        self.game_view = GameView(self)
        self.game_controller = GameController(self)

        await self.game_view.setup()
        await self.game_controller.setup()

        # Set state
        await self.change_state(GameState.WAITING)

    async def close(self):
        """ Close MVC classes """
        self.game_view.close()
        self.game_controller.close()

    # Messages
    async def notify_view(self, msg):
        """ Notify View about change of the game state """
        await self.game_view.notify(msg)

    # Strategy
    async def change_state(self, state):
        if not isinstance(state, GameState):
            raise Exception("Bad state passed to change_state(state) function.")

        self.game_state = state

        if self.game_strategy:
            await self.game_strategy.close()
        self.game_strategy = Game.strategy_mapper[state](self)
        await self.game_strategy.setup()

    # Game helpers
    def get_sb(self):
        return self.small_blind

    def get_bb(self):
        return 2 * self.small_blind

    def take_blinds(self, sb_ind):
        """ Take Small Blind and Big Blind from active players starting from given player index """
        bb_ind = (sb_ind + 1) % len(self.in_game_players)

        self.in_game_players[sb_ind].move_to_pot(self.get_sb())
        self.in_game_players[bb_ind].move_to_pot(self.get_bb())
        self.in_game_players[bb_ind].bb_can_decide = True

    def player_can_play(self, player):
        return player.ready and player.money >= self.get_bb()

    def get_pot(self):
        """ Return sum of money in the pot """
        return reduce(sum, [p.pot_money for p in self.in_game_players])

    def get_highest_bid(self):
        """ Return max current bid in pot """
        return reduce(max, [p.pot_money for p in self.in_game_players])

    def set_player_ready(self, player_id):
        """ Set player state as ready to start a game """
        player = list(filter(lambda p: p.id() == player_id, self.players))

        if len(player):
            player[0].ready = True

    def search_best_hand(self):
        result = Evaluator.table_evaluate([p.cards for p in self.in_game_players], self.table_cards.copy())
        for p, r in zip(self.in_game_players, result):
            p.best_hand = r

    def get_player(self, user_id):
        players = [p for p in self.players if p.id() == user_id]
        return players[0] if players else None

    def get_current_player(self):
        return self.in_game_players[self.curr_player_index]

    #
    #   API: External Events
    #
    async def on_player_sit(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_sit(*args, **kwargs)

    async def on_player_quit(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_quit(*args, **kwargs)

    async def on_player_ready(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_ready(*args, **kwargs)

    async def on_player_unready(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_unready(*args, **kwargs)

    async def on_player_fold(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_fold(*args, **kwargs)

    async def on_player_check(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_check(*args, **kwargs)

    async def on_player_raise(self, *args, **kwargs):
        with self.lock:
            await self.game_strategy.on_player_raise(*args, **kwargs)
