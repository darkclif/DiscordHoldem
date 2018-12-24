import asyncio
import time
import datetime

from discord_client import instance as discord_api
from hand_namer import HandNamer
from locale import locales
from card import Card


class GameView:
    """ MVC: Game Controller """
    api_reactions = ["✅", "❌", "🇷", "⤵", "➡", "↗", "🅰"]

    def __init__(self, game_model):
        self.game = game_model

        # Logs
        self.logs = {
            "info": {"count": 3, "lines": [], "change": True},
            "game": {"count": 5, "lines": [], "change": True},
        }

        # Printers
        self.printer_mappers = {
            "ingame": {
                "standard": self.__print_ingame_players,
                "end":      self.__print_ingame_players_end
            },
            "waiting": {
                "standard": self.__print_waiting_players,
            }
        }

        self.printers = {
            "ingame": self.printer_mappers["ingame"]["standard"],
            "waiting": self.printer_mappers["waiting"]["standard"]
        }

    # Setup / Close
    async def setup(self):
        """ Setup object """
        # Print messages to channel
        content = '[{}] I will keep this message for myself!'
        msg = [await discord_api.send_message(self.game.channel, content.format(k)) for k in range(3)]
        self.game.hooked_msg = {n: msg[k] for k, n in enumerate(["info_log", "main", "game_log"])}

        # Add reactions to main message
        for r in GameView.api_reactions:
            await asyncio.wait({discord_api.add_reaction(self.game.hooked_msg["main"], r)}, return_when="ALL_COMPLETED")

        # Print state
        await self.notify()

    async def close(self):
        """ Close object """
        await discord_api.edit_message(self.game.hooked_msg["main"], '=== Game closed. ===')
        await discord_api.edit_message(self.game.hooked_msg["game_log"], '=== Game closed. ===')
        await discord_api.edit_message(self.game.hooked_msg["info_log"], '=== Game closed. ===')

        await discord_api.clear_reactions(self.game.hooked_msg["main"])

    # API
    def change_printer(self, chunk, printer):
        """ Change printer for chunk of information """
        self.printers[chunk] = self.printer_mappers[chunk][printer]

    def log(self, log_name, locale_str, **kwargs):
        """
        Print localized message from locale module to one of game log.
        See *.loc files.

        :param log_name: ID of log. (eg. "game" or "info")
        :param locale_str: ID of a localized string. (eg. PLAYER_FOLD)
        :param kwargs: Parameters to fill a string.
        :return: None
        """
        log = locales.get_string(locale_str).format(**kwargs)
        stp = time.time()

        self.logs[log_name]["lines"].append((stp, log))
        self.logs[log_name]["change"] = True

    async def notify(self):
        """ Push current state to hooked messages """
        await discord_api.edit_message(self.game.hooked_msg["main"], self.__print_main())
        await self.notify_log()

    async def notify_log(self):
        """ Push current state of logs to hooked messages """
        if self.logs["info"]["change"]:
            await discord_api.edit_message(self.game.hooked_msg["info_log"], self.__print_log("info"))
            self.logs["info"]["change"] = False

        if self.logs["game"]["change"]:
            await discord_api.edit_message(self.game.hooked_msg["game_log"], self.__print_log("game"))
            self.logs["game"]["change"] = False

    # State printers
    def __print_ingame_players(self):
        """ Print information about current playing users """
        game = self.game

        # Generate in-game players header
        f_header = '{N: >2} DT {NAME: <10} {STATUS: <10} {MONEY: <7} {MONEY_DIFF: <7} \n'
        s_header = f_header.format(N="No", NAME="Name", STATUS="Status", MONEY="Money", MONEY_DIFF="Pot")

        # Generate in-game players
        s_player = ""
        f_player = '{N: >2} {D: <1}{T: <1} {NAME: <10} {STATUS: <10} ${MONEY: <6} ${MONEY_POT: <6}\n'
        for k, p in enumerate(game.in_game_players):
            status = "FOLD" if p.fold else "ALL IN" if p.all_in else "IN GAME"

            s_player += f_player.format(
                N=p.seat_num+1,
                D="D" if k == game.dealer_index else " ",
                T=">" if k == game.curr_player_index else " ",
                NAME=p.name(10),
                STATUS=status,
                MONEY=p.money,
                MONEY_POT=p.pot_money
            )

        return s_header + s_player

    def __print_ingame_players_end(self):
        """ Print information about current playing users """
        game = self.game

        # Generate in-game players header
        f_header = '{N: >2} {NAME: <9} {CARDS: <6} {VALUE: <16} {PRIZE: <5} \n'
        s_header = f_header.format(N="No", NAME="Name", CARDS="Cards", VALUE="Value", PRIZE="Prize")

        # Generate in-game players
        s_player = ""
        f_player = '{N: >2} {NAME: <9} {CARDS: <6} {VALUE: <16} ${PRIZE: >4} \n'
        for k, p in enumerate(game.in_game_players):
            s_player += f_player.format(
                N=p.seat_num+1,
                NAME=p.name(9),
                CARDS="".join([Card.get_string(c) for c in p.cards]),
                VALUE=HandNamer.name_hand(p.best_hand),
                PRIZE=p.prize
            )

        return s_header + s_player

    def __print_waiting_players(self):
        """ Print information about waiting playing users """
        game = self.game

        # Generate waiting players header
        f_header = '{N: >2} {NAME: <10} {STATUS: <10}\n'
        s_header = f_header.format(N="No", NAME="Name", STATUS="Status")

        # Generate waiting players
        s_player = ""
        f_player = '{N: >2} {NAME: <10} {STATUS: <10}\n'
        for p in list(set(game.players) - set(game.in_game_players)):
            status = "READY" if p.ready else "-"
            s_player += f_player.format(N=p.seat_num+1, NAME=p.name(), STATUS=status)

        return s_header + s_player

    def __print_main(self):
        """ Print current state of the table """
        game = self.game

        # Generate card tops
        cards = [Card.get_string(c) for c in game.table_cards] + ["_" for _ in range(5-len(game.table_cards))]
        cards_string = " | ".join(cards)

        # Generate final string
        return_format = '```'\
            '======= TABLE No.{TABLE_ID: >3}, GAME No.{GAME_ID: >4} =======\n\n'\
            '{CARDS: ^42}\n'\
            'Pot Total: ${POT}\n'\
            'GAME______________________________________\n'\
            '{PLAYERS_IN}\n\n'\
            'TABLE_____________________________________\n'\
            '{PLAYERS_OUT}\n'\
            '```'

        return_string = return_format.format(
            TABLE_ID=self.game.table_id,
            GAME_ID=self.game.game_id,
            CARDS=cards_string,
            POT=self.game.get_pot(),
            PLAYERS_IN=self.printers["ingame"](),
            PLAYERS_OUT=self.printers["waiting"]()
        )

        return return_string

    def __print_log(self, log_name):
        if log_name in self.logs.keys() and len(self.logs[log_name]["lines"]):
            logs = self.logs[log_name]["lines"][-4:][::-1]
            logs = ["["+datetime.datetime.fromtimestamp(l[0]).strftime("%H:%M")+"] "+l[1] for l in logs]

            return "```"+"\n".join(logs)+"```"
        else:
            return "```\n```"
