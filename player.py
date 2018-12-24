from discord_client import instance as discord_api
from card import Card
from hand_namer import *


class Player:
    """
        Class representing a Player at the table.
        Same discord account may be playing on different tables.
    """
    def __init__(self, discord_user, money_in, seat):
        # Discords API
        self.discord_user = discord_user

        # Game data
        self.money = money_in       # TODO: Check if Player have enough money!

        self.seat_num = seat
        self.ready = False

        # Cards
        self.best_hand = ()
        self.best_cards = []

        self._cards = []
        self.card_message = None    # Discord message hook for updating card info

        self.fold = False
        self.all_in = False
        self.pot_money = 0          # Money that player transferred to stake in current game
        self.prize = 0              # Prize won at the end of the game
        self.can_decide = False     # Every person can decide at least once

    def id(self):
        return self.discord_user.id

    def name(self, length=100):
        if len(self.discord_user.name) <= length:
            return self.discord_user.name
        else:
            return self.discord_user.name[:length-3] + "..."

    # In game logic
    def reset(self):
        self.all_in = False
        self.fold = False
        self.can_decide = True

        self.pot_money = 0
        self.prize = 0

        self._cards = []
        self.best_hand = ()
        self.best_cards = []

    def phase_reset(self):
        self.can_decide = True

    def is_active(self):
        return not (self.all_in or self.fold)

    # Money
    def move_to_pot(self, money, all_in=False):
        # All in
        money = self.money if all_in else money

        if (self.money - money) >= 0:
            self.money -= money
            self.pot_money += money
            return True
        else:
            return False

    # Card manage
    @property
    def cards(self):
        return self._cards

    @cards.setter
    def cards(self, cards):
        self._cards = cards
        self.card_message = None
        self.best_hand = None

    async def update_card_message(self, game):
        text = "[Table {}][Game {}]  ".format(game.table_id, game.game_id)
        text += " ".join([Card.get_string(c) for c in self.cards])
        text += "({})".format(HandNamer.name_hand(self.best_hand))

        if not self.card_message:
            self.card_message = await discord_api.send_message(self.discord_user, text)
        else:
            await discord_api.edit_message(self.card_message, text)

