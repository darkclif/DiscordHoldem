from game import *
from logger import global_log
import asyncio


class GameServer:
    """ Class for storing all current running games """

    def __init__(self):
        self.games = {}     # map: channel_id -> game_controller

        self.game_id_counter = 1

    # Handle server commands
    async def set_table(self, msg, cmd):
        """ Set game on target channel """
        if msg.channel.id in self.games:
            global_log("info", "Init: Game on channel {} already exists. Aborted.".format(msg.channel.id))
            return

        new_game = Game(msg.channel, self.game_id_counter)
        await asyncio.wait({new_game.setup()})

        self.games[msg.channel.id] = new_game.game_controller

        global_log("info", "Created new game table with id {}".format(self.game_id_counter))
        self.game_id_counter += 1

    async def close_table(self, msg, cmd):
        """ Close game on target table """
        game = None
        if msg.channel.id in self.games.keys():
            game = self.games.pop(msg.channel.id)
            await game.close()

        global_log("info", "Closed game table with id {}".format(game.game_id))

    # In-game API Dispatch
    async def on_ingame_command(self, msg, cmd):
        """ React to player reaction under one of game messages """
        # Check if reaction is under one of observed channel
        channel_id = msg.channel.id
        if channel_id in self.games.keys():
            await self.games[channel_id].on_ingame_command(msg, cmd)

    async def on_ingame_reaction_add(self, reaction, user):
        """ React to player reaction under one of game messages """
        # Check if reaction is under one of observed channel
        channel_id = reaction.message.channel.id
        if channel_id in self.games.keys():
            await self.games[channel_id].on_ingame_reaction_add(reaction, user)

    async def on_ingame_reaction_remove(self, reaction, user):
        """ React to player reaction removal under one of game messages """
        # Check if reaction was deleted under one of observed channel
        channel_id = reaction.message.channel.id
        if channel_id in self.games.keys():
            await self.games[channel_id].on_ingame_reaction_remove(reaction, user)

instance = GameServer()
