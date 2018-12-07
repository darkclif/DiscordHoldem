import discord
import _token
import asyncio

instance = discord.Client()

from event_dispatcher import dispatcher
from logger import global_log

@instance.event
async def on_ready():
    global_log("info", "Logged in as {} ({})".format(instance.user.name, instance.user.id))


@instance.event
async def on_message(msg):
    if msg.content.startswith('!a'):
        await dispatcher.on_message(msg)


@instance.event
async def on_reaction_add(reaction, user):
    await dispatcher.on_reaction(reaction, user)

instance.run(_token.token)
