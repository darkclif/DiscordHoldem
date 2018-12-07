""" Server utilities """
from discord_client import instance as discord_api


async def show_help(msg, cmd):
    """ Show help"""
    help_string = "```"
    help_string += "Create/Close poker table:"
    help_string += "  '!a init' - on channel with BOT"
    help_string += "  '!a close' - on channel with created table"
    help_string += "Create/Close poker table:"
    help_string += "```"

    await discord_api.send_message(msg.author, help_string)
