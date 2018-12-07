class Player:
    """
        Class representing a Player at the table.
        Same discord account may be playing on different tables.
    """
    def __init__(self, discord_user, money_in):
        # Discords API
        self.discord_user = discord_user

        # Game data
        self.money = money_in   # TODO: Check if Player have enough money!
        self.pot_money = 0    # Money that player transferred to stake in current game

        self.ready = False
        self.playing = False    # Some players could be sitting at the table but not playing yet
        self.all_in = False

        self.cards = []

    # In game logic
    def take_cards(self):
        ret_cards = self.cards
        self.cards = []
        return ret_cards

    def give_cards(self, cards):
        self.cards = cards

    def give_money(self, money):
        self.money += money

    def move_money_to_stake(self, money=0):
        # All in
        money = money if money else self.money

        if (self.money - money) >= 0:
            self.money -= money
            self.pot_money += money
            return True
        else:
            return False

    def take_stake_money(self, money):
        if (self.pot_money - money) >= 0:
            self.pot_money -= money
            return True
        else:
            return False

    def make_playing(self):
        self.playing = True

