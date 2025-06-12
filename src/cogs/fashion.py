from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from ..classes import ItemPaginator
from ..classes import FashionInitView

if TYPE_CHECKING:
    from ..bot import FashionThing


class Fashion(commands.Cog):
    def __init__(self, bot: FashionThing) -> None:
        self.bot = bot

    # idk what to call it
    @app_commands.command(
        name="modals", description="Initialise embeds for support channel"
    )
    async def modals(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        embeds: List[discord.Embed] = []
        embeds.append(
            self.bot.base_embed(
                "Fashion Assistance",
                "**Need Fashion Help? Open a Ticket!**\nWelcome to Fashion Support! If you're stuck on a set, need advice, or want feedback, we've got a team ready to help.",
            ).set_thumbnail(
                url="https://images-ext-1.discordapp.net/external/3UcfzmtXltk9GAN_08ZtTL7xa0lhlmi4yLeEGVm-h4I/https/cdn.discordapp.com/icons/872171573870735410/8b0f20b167ed00efbbe1046f955068ba.png"
            )
        )
        embeds.append(
            self.bot.base_embed(
                "Fashion Help Guide",
                "Click the button below to create a private support ticket and a Fashion Helper will be pinged and join shortly, You'll have 1 hour to get support before the ticket closes automatically - so be quick and clear!\n\nPlease include in the form:\n- The task you need help on (e.g Item Hunting, IODA Suggestions, Set Suggestions, etc)\n- URL of your character's set (Optional)\n- Your AQWorlds username",
            )
        )
        embeds.append(
            self.bot.base_embed(
                "Fashion Helper Rewards",
                "After you're done, use the close button with the names of your fashion helpers (each username on a separete line). They each gain points tallied to a leaderboard. ",
            )
        )

        await interaction.followup.send(embeds=embeds, view=FashionInitView(self.bot))

    @app_commands.command(name="sync", description="Syncs slash commands to server")
    async def sync(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(thinking=True)
        await self.bot.sync()
        await interaction.followup.send(
            embed=self.bot.base_embed(
                "Synced Commands", "Commands have been successfully synced!"
            )
        )

    @app_commands.command(name="suggest", description="Suggest an item")
    @app_commands.describe(item="The item you wish to suggest")
    async def suggest(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer(thinking=True)

        urls = await self.bot.search_item(item)

        if len(urls) == 1:
            images = await self.bot.get_image_url(urls[0])
            embeds = []

            for image in images:
                embeds.append((self.bot.base_embed(f"{self.bot.title_except(item)}", "", url=urls[0]).set_image(url=image)))
            if len(embeds) > 1:
                await interaction.followup.send(
                    embed=embeds[0],
                    view=ItemPaginator(embeds, interaction.user)
                )
            else:
                await interaction.followup.send(embed=embeds[0])
        elif len(urls) < 1:
            await interaction.followup.send(embed=self.bot.base_embed("Item not Found!", "Double check spelling and try again!"), ephemeral=True)
        else:
            pass


async def setup(bot: FashionThing):
    await bot.add_cog(Fashion(bot))
