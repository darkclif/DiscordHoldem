from random import shuffle
from enum import Enum
from functools import reduce
from discord_client import instance as discord_api
import asyncio

from card import *
from player import *
from logger import global_log
from locale import locales


class GameState(Enum):
    IDLE = 0        # Players are waiting for game beginning
    PRE_FLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4


class Game:
    # Statics
    api_reactions = ["✅", "❌", "🇷", "⤵", "➡", "↗"]

    # Methods
    def __init__(self, channel, game_id):
        """ Create game on given table """
        self._channel = channel
        self._players = {}      # 9 players
        for i in range(10):
            self._players[i] = None

        # Prepare table
        self.table_id = 0
        self.game_id = 0

        self.table_cards = []   # max 5
        self.deck = []          # max 2

        self.small_blind = 10
        self.dealer_index = None

        self.curr_player_index = 0
        self.active_players = []
        self.game_state = GameState.IDLE

        # Logs
        self.logs = {
            "info": {"count": 3, "lines": []},
            "game": {"count": 5, "lines": []},
        }

        # Discord API hooks
        self.hooked_msg = {}

    async def setup(self):
        # Print message to channel
        msg = [await discord_api.send_message(self._channel, '[{}] I will keep this message for myself!'.format(k)) for k in range(3)]
        self.hooked_msg = {n: msg[k] for k, n in enumerate(["info_log", "main", "game_log"])}

        # Add reactions to main message
        for r in Game.api_reactions:
            await asyncio.wait({discord_api.add_reaction(self.hooked_msg["main"], r)}, return_when="ALL_COMPLETED")

        # Render
        await self.update_message("main")

    async def close(self):
        await discord_api.edit_message(self.hooked_msg["main"], '=== Game closed. ===')
        await discord_api.edit_message(self.hooked_msg["game_log"], '=== Game closed. ===')
        await discord_api.edit_message(self.hooked_msg["info_log"], '=== Game closed. ===')

    def begin_game(self):
        """ Begin new game """
        # Get list of playing players
        players = {k: v for k, v in self._players.items() if v and v.money >= 2 * self.small_blind}

        # There is no players at the table
        if not players:
            return False

        # Prepare deck
        self.deck = Card.create_deck()
        shuffle(self.deck)

        # Move dealer coin
        player_ind = [k for k, v in players]
        if self.dealer_index is None:
            self.dealer_index = player_ind[0]
        else:
            self.dealer_index = player_ind[(self.dealer_index + 1) % len(player_ind)]

        # Pass two cards to players
        for k, v in players.items():
            v.give_cards([self.deck.pop(), self.deck.pop()])

        # Mark starting player
        self.active_players = player_ind
        self.curr_player_index = (self.dealer_index + 3) % len(player_ind)

        self.game_state = GameState.PRE_FLOP
        return True

    def get_state_main(self):
        """ Send state of current game to the Discord Channel """
        # Generate player string
        """ STATUS = ALL_IN | FOLD | CHECK | - | RAISE """
        """ No. BG/SB Player_name STATUS Cash Diff Turn_Indicator"""

        # Generate player information
        player_string = '{N: >2}. {NAME: <10} {STATUS: <10} {MONEY_IN: <6}  {MONEY_DIFF: <6}\n'
        player_string = player_string.format(N="No", NAME="Name", STATUS="Status", MONEY_IN="Pot", MONEY_DIFF="Diff.")

        for k, p in self._players.items():
            if not p:
                continue

            l_str = '{N: >2}. {NAME: <10} {STATUS: <10} ${MONEY_IN: <6} ${MONEY_DIFF: <6}\n'
            l_str = l_str.format(N=k+1, NAME=p.discord_user.name, STATUS="NONE", MONEY_IN=200, MONEY_DIFF=30)

            player_string += l_str

        # Generate card tops
        table = [list(map(lambda x: x.get_ascii(), self.table_cards[s:e])) for s, e in [(0, 3), (3, 4), (4, 5)]]
        table_string = " | ".join([" ".join(s) for s in table])

        # Generate final string
        ret_str = '```'\
            '======= TABLE No.{TABLE_ID: >3}, GAME No.{GAME_ID: >4} =======\n\n'\
            '{CARD_TOPS: ^42}\n\n'\
            '{CARDS}\n\n'\
            '{PLAYERS}\n'\
            '```'

        ret_str = ret_str.format(
            TABLE_ID=self.table_id,
            GAME_ID=self.game_id,
            CARD_TOPS=table_string,
            CARDS="---",
            PLAYERS=player_string
        )

        return ret_str

    def get_pot(self):
        """ Return sum of money bids in pot """
        return reduce(sum, [self._players[i].pot_money for i in self.active_players])

    def get_pot_highest(self):
        """ Return max current bid in pot """
        return reduce(max, [self._players[i].pot_money for i in self.active_players])

    async def on_channel_reaction(self, reaction, user):
        """ Check if reaction is under one of hooked messages and handle it """
        for k, m in self.hooked_msg.items():
            # Its not my supervised message!
            if not m or m.id != reaction.message.id:
                continue

            # It is my message!
            if k == "main":
                await self.handle_reaction(reaction, user)
            else:
                # Delete reaction on wrong message
                await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

    async def handle_reaction(self, reaction, user):
        """ Handle reaction under main message """
        # global_log("info", "Emoji {} handled".format(reaction.emoji))
        to_func = {
            "✅":    self.on_player_sit,
            "❌":    self.on_player_quit,
            "🇷":    self.on_player_ready,
            "⤵":    self.on_player_fold,
            "➡":    self.on_player_check,
            "↗":    self.on_player_raise
        }

        if reaction.emoji in to_func.keys():
            await to_func[reaction.emoji](reaction, user)
        else:
            # Delete unknown reaction
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

    def add_log(self, log_name, locale_str, *args):
        self.logs[log_name]["lines"].append(locales.get_string(locale_str).format(*args))

    def get_state_log(self, log_name):
        if log_name in self.logs.keys():
            return "\n".join(self.logs[log_name]["lines"][-5:])

    async def update_message(self, msg_name="all"):
        if msg_name in ["main", "all"]:
            await discord_api.edit_message(self.hooked_msg["main"], self.get_state_main())
        elif msg_name in ["info_log", "all"]:
            await discord_api.edit_message(self.hooked_msg["info_log"], self.get_state_log("info"))
        elif msg_name in ["game_log", "all"]:
            await discord_api.edit_message(self.hooked_msg["game_log"], self.get_state_log("game"))
        else:
            global_log("error", "Wrong message name to push updates ({})".format(msg_name))

    # API: Handle events
    async def on_player_sit(self, reaction, user, money_in=10000):
        """ Player sits at the table """
        await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        # Player already at table
        my_seats = list(filter(lambda ply: ply[1] and ply[1].discord_user.id == user.id, self._players.items()))
        if len(my_seats) >= 1:
            global_log("dbg", "Player {} tried to sit at {} but he is already there.".format(user.name, self.table_id))
            return

        # No empty seats
        empty_seats = list(filter(lambda ply: not ply[1], self._players.items()))
        if not len(empty_seats):
            global_log("dbg", "Player {} tried to sit at {} but table is full.".format(user.name, self.table_id))
            return

        # SUCCESS
        self._players[empty_seats[0][0]] = Player(user, money_in)

        await self.update_message("main")
        global_log("dbg", "Player {} sit at {}.".format(user.name, self.table_id))

    async def on_player_quit(self, reaction, user):
        """ Player stands from the table """
        await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        # Player not at the table
        my_seats = list(filter(lambda ply: ply[1] and ply[1].discord_user.id == user.id, self._players.items()))
        if not len(my_seats):
            global_log("dbg", "Player {} want to quit from {} but he's not at the table.".format(user.name, self.table_id))
            return

        # SUCCESS
        my_seat = my_seats[0]
        self._players[my_seat[0]] = None

        await self.update_message("main")
        global_log("dbg", "Player {} stand up from {}.".format(user.name, self.table_id))

    async def on_player_ready(self, reaction, user):
        pass

    async def on_player_fold(self, reaction, user):
        pass

    async def on_player_check(self, reaction, user):
        pass

    async def on_player_raise(self, reaction, user):
        pass
