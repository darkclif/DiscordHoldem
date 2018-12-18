from enum import Enum

from discord_client import instance as discord_api
from card import Card
from hand_namer import *


class PlayerState(Enum):
    IN_GAME = 0
    FOLD = 1
    ALL_IN = 2
    IDLE = 3


class Player:
    """
        Class representing a Player at the table.
        Same discord account may be playing on different tables.
    """
    def __init__(self, discord_user, money_in, seat):
        # Discords API
        self.discord_user = discord_user

        # Game data
        self.money = money_in   # TODO: Check if Player have enough money!

        self.seat_num = seat
        self.ready = False

        # Cards
        self.best_hand = None
        self.cards = []
        self.card_message = None

        self.all_in = False
        self.pot_money = 0          # Money that player transferred to stake in current game
        self.bb_can_raise = False   # On PreFlop person on big-blind can decide at least once

    # Getter
    def id(self):
        return self.discord_user.id

    def get_seat_num(self):
        return self.seat_num

    def get_name(self, length=100):
        if len(self.discord_user.name) <= length:
            return self.discord_user.name
        else:
            return self.discord_user.name[:length-3] + "..."

    def is_ready(self):
        return self.ready

    # In game logic
    def reset(self):
        self.set_cards([])
        self.all_in = False
        self.pot_money = 0
        self.bb_can_raise = False

    def set_ready(self, value=True):
        self.ready = value

    def set_all_in(self, value=True):
        self.all_in = value

    def set_bb_raise(self, value=True):
        self.bb_can_raise = value

    def can_play(self, big_blind):
        return self.ready and self.money >= big_blind

    # Money
    def get_money(self):
        return self.money

    def get_pot_money(self):
        return self.pot_money

    def move_to_pot(self, money=0):
        # All in
        money = money if money else self.money

        if (self.money - money) >= 0:
            self.money -= money
            self.pot_money += money
            return True
        else:
            return False

    def take_pot_money(self, money):
        if (self.pot_money - money) >= 0:
            self.pot_money -= money
            return True
        else:
            return False

    # Card manage
    def get_cards(self):
        return self.cards.copy()

    def set_cards(self, cards):
        self.cards = cards
        self.card_message = None
        self.best_hand = None

    def set_best_hand(self, hand):
        self.best_hand = hand

    async def update_card_message(self, game):
        text = "[Table {}][Game {}]  ".format(game.table_id, game.game_id)
        text += " ".join([Card.get_string(c) for c in self.cards])
        text += "({})".format(HandNamer.name_hand(self.best_hand))

        if not self.card_message:
            self.card_message = await discord_api.send_message(self.discord_user, text)
        else:
            await discord_api.edit_message(self.card_message, text)

