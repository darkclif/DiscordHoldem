from server import GameServer
from server_utils import *


class Dispatcher:
    _commands = {
        # Command -> func(msg, cmd)

        # Game management
        'init':     GameServer.set_table,
        'close':    GameServer.close_table,

        # In-Game commands
        'raise':    GameServer.on_ingame_command,

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
        await GameServer.on_ingame_reaction_add(reaction, user)

    @staticmethod
    async def on_reaction_remove(reaction, user):
        await GameServer.on_ingame_reaction_remove(reaction, user)
