from game import *
from logger import global_log


class GameServer:
    """ Class for storing all current running games """
    def __init__(self):
        self.games = {}     # channel_id -> game

        self.game_id_counter = 1

    async def set_table(self, msg, cmd):
        if msg.channel.id in self.games:
            global_log("info", "Init: Game on channel {} already exists. Aborted.".format(msg.channel.id))
            return

        new_game = Game(msg.channel, self.game_id_counter)
        await new_game.setup()

        self.games[msg.channel.id] = new_game

        global_log("info", "Created new game table with id {}".format(self.game_id_counter))
        self.game_id_counter += 1

    async def close_table(self, msg, cmd):
        game = None
        if msg.channel.id in self.games.keys():
            game = self.games.pop(msg.channel.id)
            await game.close()

        global_log("info", "Closed game table with id {}".format(game.game_id))

    async def on_reaction(self, reaction, user):
        # Check if reaction is under one of our channel
        channel_id = reaction.message.channel.id
        if channel_id in self.games.keys():
            await self.games[channel_id].on_channel_reaction(reaction, user)


instance = GameServer()
