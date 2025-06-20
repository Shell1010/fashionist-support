from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, override

import discord
from discord import app_commands
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from ..bot import FashionThing


class Aqw(commands.Cog):
    def __init__(self, bot: FashionThing) -> None:
        self.bot = bot

    # @app_commands.command(name="char", description="Generates character based on char page")
    # @app_commands.describe(username="Player to generate, doesn't work yet ignore")
    # async def test(self, interaction: discord.Interaction, username: str):
    #     if interaction.user.id in self.bot.admins.values():
    #         await interaction.response.defer()
    #         page = await self.bot.get_char_page(username)
    #         with open("image.html", "a+") as f:
    #             f.write(page)
    #         await interaction.followup.send("ok")
    #     else:
    #         await interaction.response.send_message(embed=self.bot.base_embed("Unauthorized", "You're too stinky..."))

    def cog_unload(self) -> None:
        self.friday_check.cancel()
        self.daily_check.cancel()

    @tasks.loop(seconds=30)
    async def friday_check(self):
        if self.bot.is_florida_friday_start():
            channel = self.bot.get_channel(878693420909068339)
            
            await channel.send(
                content="<@&1385747900390183072>",
                embed=self.bot.base_embed("Weekly Reset", "It's now the weekly reset, log into AQW and complete your daily and weekly quests!")
                .set_image(url="https://media.discordapp.net/attachments/1223684772413444218/1358373404033417287/photo-output.png")) # type: ignore

    @tasks.loop(seconds=30)
    async def daily_check(self):
        if self.bot.is_florida_midnight():
            channel = self.bot.get_channel(878693420909068339)
            await channel.send(
                content="<@&1385747900390183072>",
                embed=self.bot.base_embed("Weekly Reset", "It's now the weekly reset, log into AQW and complete your daily and weekly quests!")
                .set_image(url="https://media.discordapp.net/attachments/1223684772413444218/1358373404033417287/photo-output.png")) # type: ignore





async def setup(bot: FashionThing):
    await bot.add_cog(Aqw(bot))
