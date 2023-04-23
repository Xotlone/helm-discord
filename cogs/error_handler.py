import logging

import disnake
from disnake.ext import commands as dis_commands

log = logging.getLogger('logs')


class ErrorHandler(dis_commands.Cog):
    def __init__(self, bot: dis_commands.Bot):
        self.bot = bot

    @dis_commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction,
                                     error: dis_commands.CommandError):
        log.error(repr(error), exc_info=True)


def setup(bot: dis_commands.Bot):
    bot.add_cog(ErrorHandler(bot))
