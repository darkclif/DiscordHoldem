import discord
import _token
import asyncio

instance = discord.Client()

from event_dispatcher import *
from logger import global_log


@instance.event
async def on_ready():
    global_log("info", "Logged in as {} ({})".format(instance.user.name, instance.user.id))


@instance.event
async def on_message(msg):
    if msg.content.startswith('!a'):
        await Dispatcher.on_message(msg)


@instance.event
async def on_reaction_add(reaction, user):
    await Dispatcher.on_reaction_add(reaction, user)


@instance.event
async def on_reaction_remove(reaction, user):
    await Dispatcher.on_reaction_remove(reaction, user)

instance.run(_token.token)
