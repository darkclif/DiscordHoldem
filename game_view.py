import asyncio

from discord_client import instance as discord_api
from logger import global_log
from locale import locales
from card import Card


class GameView:
    """ MVC: Game Controller """
    api_reactions = ["✅", "❌", "🇷", "⤵", "➡", "↗"]

    def __init__(self, game_model):
        self.game = game_model

        # Logs
        self.logs = {
            "info": {"count": 3, "lines": []},
            "game": {"count": 5, "lines": []},
        }

    # Setup / Close
    async def setup(self):
        """ Setup object """
        # Print messages to channel
        msg = [await discord_api.send_message(self.game.channel, '[{}] I will keep this message for myself!'.format(k)) for k in range(3)]
        self.game.hooked_msg = {n: msg[k] for k, n in enumerate(["info_log", "main", "game_log"])}

        # Add reactions to main message
        for r in GameView.api_reactions:
            await asyncio.wait({discord_api.add_reaction(self.game.hooked_msg["main"], r)}, return_when="ALL_COMPLETED")

        # Render
        await self.notify("all")

    async def close(self):
        """ Close object """
        await discord_api.edit_message(self.game.hooked_msg["main"], '=== Game closed. ===')
        await discord_api.edit_message(self.game.hooked_msg["game_log"], '=== Game closed. ===')
        await discord_api.edit_message(self.game.hooked_msg["info_log"], '=== Game closed. ===')

        # TODO: Clear reactions

    # State renderers
    def print_ingame_players(self):
        """ Print information about current playing users """
        game = self.game

        # Generate in-game players header
        f_header = '{N: >2}. DT {NAME: <10} {STATUS: <10} {MONEY_POT: <6}  {MONEY_DIFF: <6}\n'
        s_header = f_header.format(N="No", NAME="Name", STATUS="Status", MONEY_POT="Pot", MONEY_DIFF="Diff.")

        # Generate in-game players
        s_player = ""
        f_player = '{N: >2}. {D: <1}{T: <1} {NAME: <10} {STATUS: <10} ${MONEY_POT: <6} ${MONEY_DIFF: <6}\n'
        for k, p in enumerate(game.active_players):
            s_player += f_player.format(
                N=p.seat_num+1,
                D="D" if k == game.dealer_index else " ",
                T=">" if k == game.curr_player_index else " ",
                NAME=p.name(10),
                STATUS="NONE",
                MONEY_POT=p.pot_money,
                MONEY_DIFF=game.get_highest_bid() - p.pot_money
            )

        return s_header + s_player

    def print_waiting_players(self):
        """ Print information about waiting playing users """
        game = self.game

        # Generate waiting players header
        f_header = '{N: >2}. {NAME: <10} {STATUS: <10}\n'
        s_header = f_header.format(N="No", NAME="Name", STATUS="Status")

        # Generate waiting players
        s_player = ""
        f_player = '{N: >2}. {NAME: <10} {STATUS: <10}\n'
        for p in list(set(game.players) - set(game.active_players)):
            status = "READY" if p.ready else "-"
            s_player += f_player.format(N=p.seat_num+1, NAME=p.name(), STATUS=status)

        return s_header + s_player

    def print_main(self):
        """ Print current state of the table """
        game = self.game

        # Generate card tops
        cards = [list(map(lambda c: Card.get_string(c), game.table_cards[s:e])) for s, e in [(0, 3), (3, 4), (4, 5)]]
        cards_string = " | ".join([" ".join(c) for c in cards])

        # Generate final string
        return_format = '```'\
            '======= TABLE No.{TABLE_ID: >3}, GAME No.{GAME_ID: >4} =======\n\n'\
            '{CARDS: ^42}\n\n'\
            'GAME______________________________________\n'\
            '{PLAYERS_IN}\n\n'\
            'TABLE_____________________________________\n'\
            '{PLAYERS_OUT}\n'\
            '```'

        return_string = return_format.format(
            TABLE_ID=self.game.table_id,
            GAME_ID=self.game.game_id,
            CARDS=cards_string,
            PLAYERS_IN=self.print_ingame_players(),
            PLAYERS_OUT=self.print_waiting_players()
        )

        return return_string

    def print_log(self, log_name):
        if log_name in self.game.logs.keys():
            return "\n".join(self.game.logs[log_name]["lines"][-5:])
        else:
            return ""

    # API
    def log(self, log_name, locale_str, *args):
        self.logs[log_name]["lines"].append(locales.get_string(locale_str).format(*args))

    async def notify(self, msg_name):
        """ Push current state to hooked messages """
        if msg_name in ["main", "all"]:
            await discord_api.edit_message(self.game.hooked_msg["main"], self.print_main())
        elif msg_name in ["info_log", "all"]:
            await discord_api.edit_message(self.game.hooked_msg["info_log"], self.print_log("info"))
        elif msg_name in ["game_log", "all"]:
            await discord_api.edit_message(self.game.hooked_msg["game_log"], self.print_log("game"))
        else:
            global_log("error", "Wrong message name to push updates ({}) - abort.".format(msg_name))
