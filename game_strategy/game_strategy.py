from abc import *


class GameStrategy(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    async def setup(self):
        """ Bootstrap a new strategy """

    @abstractmethod
    async def close(self):
        """ Close a new strategy """

    #
    #   API: External Events
    #
    @abstractmethod
    async def on_player_sit(self, user, money_in=10000):
        """
        Player sits at the table.

        :param user: User taking action
        :param money_in: Amount of money to
        :return: None
        """

    @abstractmethod
    async def on_player_quit(self, user):
        """
        Player stands from the table.

        :param user: User taking action.
        :return: None
        """

    @abstractmethod
    async def on_player_ready(self, user):
        """
        Player checks ready for a game.

        :param user: User taking action
        :return: None
        """

    @abstractmethod
    async def on_player_unready(self, user):
        """
        Player checks unready for a game.

        :param user: User taking action
        :return: None
        """

    @abstractmethod
    async def on_player_fold(self, user):
        """
        Player fold.

        :param user: User taking action
        :return: None
        """

    @abstractmethod
    async def on_player_check(self, user):
        """
        Player checks current bid.

        :param user: User taking action
        :return: None
        """

    @abstractmethod
    async def on_player_raise(self, user, money=None):
        """
        Player raise his bid by given amount

        :param user: User taking action
        :param money: Amount of money to rise; None - BB
        :return: None
        """