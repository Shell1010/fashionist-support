from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import discord
from discord import app_commands
from discord.ext import commands


if TYPE_CHECKING:
    from ..bot import FashionThing


class Char(commands.Cog):
    def __init__(self, bot: FashionThing) -> None:
        self.bot = bot

    @app_commands.command(name="char", description="Generates character based on char page")
    @app_commands.describe(username="Player to generate")
    async def test(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer()
        page = await self.bot.get_char_page(username)
        with open("image.html", "a+") as f:
            f.write(page)
        await interaction.followup.send("ok")


async def setup(bot: FashionThing):
    await bot.add_cog(Char(bot))

