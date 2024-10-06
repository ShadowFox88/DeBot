from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord

from .errors import AlreadyBlacklisted, BlacklistedGuild, BlacklistedUser, NotBlacklisted

__all__ = ('Blacklist',)

if TYPE_CHECKING:
    import datetime

    from discord.abc import Snowflake

    from bot import DeBot

    from .context import DeContext
    from .types import BlacklistBase


class Blacklist:
    blacklists: dict[Snowflake, BlacklistBase]

    def __init__(self, bot: DeBot) -> None:
        self.blacklists = {}
        self.bot = bot
        self.bot.check_once(self.check)

    async def check(self, ctx: DeContext) -> Literal[True]:
        if ctx.guild and self.is_blacklisted(ctx.guild):
            raise BlacklistedGuild(
                ctx.guild,
                reason=self.blacklists[ctx.guild]['reason'],
                until=self.blacklists[ctx.guild]['lasts_until'],
            )
        if ctx.author and self.is_blacklisted(ctx.author):
            raise BlacklistedUser(
                ctx.author,
                reason=self.blacklists[ctx.author]['reason'],
                until=self.blacklists[ctx.author]['lasts_until'],
            )

        return True

    def is_blacklisted(self, snowflake: discord.Member | discord.User | discord.Guild) -> bool:
        return bool(self.blacklists.get(snowflake))

    async def add(
        self,
        snowflake: discord.User | discord.Guild,
        *,
        reason: str = 'No reason provided',
        lasts_until: datetime.datetime | None = None,
    ) -> dict[Snowflake, BlacklistBase]:
        if self.is_blacklisted(snowflake):
            raise AlreadyBlacklisted(
                snowflake,
                reason=self.blacklists[snowflake]['reason'],
                until=self.blacklists[snowflake]['lasts_until'],
            )

        sql = """INSERT INTO Blacklists (snowflake, reason, lasts_until, blacklist_type) VALUES ($1, $2, $3, $4);"""
        param = 'user' if isinstance(snowflake, discord.User) else 'guild'
        await self.bot.pool.execute(
            sql,
            snowflake.id,
            reason,
            lasts_until,
            param,
        )
        self.blacklists[snowflake] = {'reason': reason, 'lasts_until': lasts_until, 'blacklist_type': param}
        return self.blacklists

    async def remove(self, snowflake: discord.User | discord.Guild) -> dict[Snowflake, BlacklistBase]:
        if not self.is_blacklisted(snowflake):
            raise NotBlacklisted(snowflake)

        sql = """DELETE FROM Blacklists WHERE snowflake = $1"""
        param: str = 'user' if isinstance(snowflake, discord.User) else 'guild'
        await self.bot.pool.execute(
            sql,
            snowflake.id,
            param,
        )

        self.blacklists.pop(snowflake)
        return self.blacklists

    def __repr__(self) -> str:
        return str(self.blacklists)
