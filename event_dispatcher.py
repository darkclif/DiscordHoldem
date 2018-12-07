from game_server import instance as games_server
from server_utils import *


class Dispatcher:
    _commands = {
        # Command -> func(msg, cmd)

        # Game management
        'init':     games_server.set_table,
        'close':    games_server.close_table,

        # Misc
        'help':     show_help
    }

    def __init__(self):
        pass

    async def on_message(self, msg):
        cmd = msg.content.split()[1:]

        first = cmd[0].lower()
        if first in Dispatcher._commands.keys():
            await Dispatcher._commands[first](msg, cmd[1:])

    async def on_reaction(self, reaction, user):
        await games_server.on_reaction(reaction, user)


dispatcher = Dispatcher()
