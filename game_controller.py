from discord_client import instance as discord_api
from logger import global_log


class GameController:
    """ MVC: Game Controller """

    def __init__(self, game_model):
        self.game = game_model

    # Constructor / Destructor
    async def setup(self):
        pass

    async def close(self):
        pass

    #
    #   Handlers
    #
    async def handle_reaction_add(self, reaction, user):
        """ Handle reaction under main message """
        if reaction.emoji == "✅":
            money = 10000
            await self.game.on_player_sit(user, money)
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        elif reaction.emoji == "❌":
            await self.game.on_player_quit(user)
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        elif reaction.emoji == "🇷":
            await self.game.on_player_ready(user)

        elif reaction.emoji == "⤵":
            await self.game.on_player_fold(user)
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        elif reaction.emoji == "➡":
            await self.game.on_player_check(user)
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        elif reaction.emoji == "↗":
            await self.game.on_player_raise(user, 0, bb=True)
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        elif reaction.emoji == "🅰":
            await self.game.on_player_raise(user, 0, all_in=True)
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

        else:
            # Delete unknown reaction
            await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

    async def handle_reaction_remove(self, reaction, user):
        """ Handle reaction removal under main message """
        if reaction.emoji == "🇷":
            await self.game.on_player_unready(user)

    # API
    async def on_ingame_reaction_add(self, reaction, user):
        """ Checks if reaction is under one of hooked messages and handles it """
        for k, m in self.game.hooked_msg.items():
            # Is not my hooked message!
            if not m or m.id != reaction.message.id:
                continue

            # Is my main message!
            if k == "main":
                await self.handle_reaction_add(reaction, user)
            else:
                # Delete reaction on wrong message
                await discord_api.remove_reaction(reaction.message, reaction.emoji, user)

    async def on_ingame_reaction_remove(self, reaction, user):
        """ Checks if reaction is under one of hooked messages and handles it """
        for k, m in self.game.hooked_msg.items():
            # Is not my hooked message!
            if not m or m.id != reaction.message.id:
                continue

            # Is my main message!
            if k == "main":
                await self.handle_reaction_remove(reaction, user)

    async def on_ingame_command(self, msg, cmd):
        global_log("dbg", "Player {} command: {}".format(msg.user.name, ''.join(cmd)))
