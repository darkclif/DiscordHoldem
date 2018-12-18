from server import instance as games_server
from server_utils import *


class Dispatcher:
    _commands = {
        # Command -> func(msg, cmd)

        # Game management
        'init':     games_server.set_table,
        'close':    games_server.close_table,

        # In-Game commands
        'raise':     games_server.on_ingame_command,

        # Misc
        'help':     show_help
    }

    @staticmethod
    async def on_message(msg):
        # Delete "!a "
        cmd = msg.content.split()[1:]

        # Check command
        first = cmd[0].lower()
        if first in Dispatcher._commands.keys():
            await Dispatcher._commands[first](msg, cmd)

    @staticmethod
    async def on_reaction_add(reaction, user):
        await games_server.on_ingame_reaction_add(reaction, user)

    @staticmethod
    async def on_reaction_remove(reaction, user):
        await games_server.on_ingame_reaction_remove(reaction, user)
