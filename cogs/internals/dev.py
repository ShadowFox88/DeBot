from __future__ import annotations

from pkgutil import iter_modules
from typing import TYPE_CHECKING

from discord.ext import commands

from utils import LagContext, better_string

if TYPE_CHECKING:
    from bot import Lagrange


class Developer(commands.Cog):
    def __init__(self, bot: Lagrange) -> None:
        self.bot: Lagrange = bot

    @commands.command(name='reload', aliases=['re'], hidden=True)
    async def reload_cogs(self, ctx: LagContext) -> None:
        cogs = [m.name for m in iter_modules(['cogs'], prefix='cogs.')]
        messages: list[str] = []
        for cog in cogs:
            try:
                await self.bot.reload_extension(str(cog))
            except commands.ExtensionError as error:
                messages.append(f'Failed to reload {cog}\n```py{error}```')
            else:
                messages.append(f'Reloaded {cog}')
        await ctx.send(content=better_string(messages, seperator='\n'))