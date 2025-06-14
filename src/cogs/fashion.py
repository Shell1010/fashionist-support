from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from ..classes import ArmourPaginator, FashionInitView, ItemPaginator

if TYPE_CHECKING:
    from ..bot import FashionThing


class Fashion(commands.Cog):
    def __init__(self, bot: FashionThing) -> None:
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(1350262093190008945)

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
        await channel.purge(limit=10)

        await channel.send(embeds=embeds, view=FashionInitView(self.bot))

 


    # idk what to call it
    @app_commands.command(
        name="modals", description="Initialise embeds for support channel"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
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


    @app_commands.command(name="suggest", description="Suggest an item")
    @app_commands.describe(item="The item you wish to suggest")
    async def suggest(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer(thinking=True)

        item = item.lower()
        urls = await self.bot.search_item(item)

        if len(urls) == 1:
            resp = await self.bot.get_resp(urls[0])
            images = await self.bot.get_image_url(resp)
            embeds = []

            for image in images:
                embeds.append(
                    (
                        self.bot.base_embed(
                            f"{self.bot.title_except(item)}", "", url=urls[0]
                        ).set_image(url=image)
                    )
                )
            if len(embeds) > 1:
                if await self.bot.is_armour(resp):
                    await interaction.followup.send(
                        embed=embeds[0], view=ArmourPaginator(embeds, interaction.user)
                    )
                else:
                    await interaction.followup.send(
                        embed=embeds[0], view=ItemPaginator(embeds, interaction.user)
                    )

            else:
                await interaction.followup.send(embed=embeds[0])
        elif len(urls) < 1:
            await interaction.followup.send(
                embed=self.bot.base_embed(
                    "Item not Found!", "Double check spelling and try again!"
                ),
                ephemeral=True,
            )
        else:
            pass

    @app_commands.command(name="leaderboard", description="Get helper leaderboard")
    @app_commands.describe(limit="Number of entries to list")
    async def lb(self, interaction: discord.Interaction, limit: int = 20):
        await interaction.response.defer()
        leaderboard = await self.bot.db.get_leaderboard(limit)
        msg = f"Top {len(leaderboard)} Fashion Helpers for {datetime.now().strftime('%B')}\n\n"
        for idx, entry in enumerate(leaderboard, start=1):
            msg += f"{idx}. {entry['username'].capitalize()} ({entry['score']})\n"
        await interaction.followup.send(embed=self.bot.base_embed("Fashion Helper Leaderboard", msg).set_thumbnail(
                url="https://images-ext-1.discordapp.net/external/3UcfzmtXltk9GAN_08ZtTL7xa0lhlmi4yLeEGVm-h4I/https/cdn.discordapp.com/icons/872171573870735410/8b0f20b167ed00efbbe1046f955068ba.png"
            ))


    @app_commands.command(name="reset", description="Resets leaderboard")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.db.reset()
        await interaction.followup.send(embed=self.bot.base_embed("Leaderboard Reset!", "Leaderboard has successfully reset."))

    @reset.error
    async def reset_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(embed=self.bot.base_embed("Administrator Required", "Need to be Admin to run this command."))

async def setup(bot: FashionThing):
    await bot.add_cog(Fashion(bot))
