from game import *
from logger import global_log
import asyncio


class GameServer:
    """ Class for storing all current running games """
    games = {}              # mapper: channel_id -> game_controller
    game_id_counter = 1

    def __init__(self):
        pass

    # Handle server commands
    @classmethod
    async def set_table(cls, msg, cmd):
        """ Set game on target channel """
        # Game on this channel already exists
        if msg.channel.id in cls.games:
            global_log("info", "Init: Game on channel {} already exists. Aborted.".format(msg.channel.id))
            return

        # Create new game on this channel
        new_game = Game(msg.channel, cls.game_id_counter)
        with new_game.lock:
            await asyncio.wait({new_game.setup()})
            cls.games[msg.channel.id] = new_game.game_controller

        global_log("info", "Created new game table with id {}".format(cls.game_id_counter))
        cls.game_id_counter += 1

    @classmethod
    async def close_table(cls, msg, cmd):
        """ Close game on target table """
        # Close if exists
        if msg.channel.id in cls.games.keys():
            game_ctrl = cls.games.pop(msg.channel.id)
            global_log("info", "Closed game table with id {}".format(game_ctrl.game.game_id))
            await game_ctrl.game.close()

    # In-game API Dispatch
    @classmethod
    async def on_ingame_command(cls, msg, cmd):
        """ React to player command under one of game messages """
        # Check if command is under one of observed channel
        channel_id = msg.channel.id
        if channel_id in cls.games.keys():
            await cls.games[channel_id].on_ingame_command(msg, cmd)

    @classmethod
    async def on_ingame_reaction_add(cls, reaction, user):
        """ React to player reaction under one of game messages """
        # Check if reaction is under one of observed channel
        channel_id = reaction.message.channel.id
        if channel_id in cls.games.keys():
            await cls.games[channel_id].on_ingame_reaction_add(reaction, user)

    @classmethod
    async def on_ingame_reaction_remove(cls, reaction, user):
        """ React to player reaction removal under one of game messages """
        # Check if reaction was deleted under one of observed channel
        channel_id = reaction.message.channel.id
        if channel_id in cls.games.keys():
            await cls.games[channel_id].on_ingame_reaction_remove(reaction, user)
