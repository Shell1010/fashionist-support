from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

import discord

if TYPE_CHECKING:
    from ..bot import FashionThing


class CloseModal(discord.ui.Modal):
    def __init__(
        self,
        bot: FashionThing,
        user: discord.User | discord.Member,
        username: str,
        reason: str,
    ) -> None:
        super().__init__(title="Closing Ticket", timeout=None, custom_id=str(uuid4()))
        self.bot = bot
        self.user = user
        self.username = username
        self.reason = reason

        self.helpers = discord.ui.TextInput(
            label="Helpers",
            style=discord.TextStyle.long,
            placeholder="Type your helper usernames here, each on a separate line.",
            required=True,
        )
        self.add_item(self.helpers)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        usernames = self.helpers.value.split("\n")
        not_found = []
        for user in usernames:
            if not await self.bot.verify_username(user):
                not_found.append(user)

        if len(not_found) > 0:
            names = "\n".join(not_found)
            await interaction.response.send_message(
                embed=self.bot.base_embed(
                    "Username not found!",
                    f"The following usernames weren't found, please double check spelling!\n{names}",
                ),
                ephemeral=True,
            )
            return

        if self.username in usernames:
            await interaction.response.send_message(
                embed=self.bot.base_embed(
                    "You can't credit yourself!",
                    f"I see you...",
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()
        await interaction.followup.send(
            embed=self.bot.base_embed(
                "Thank you for helping!",
                f"This ticket is now closed, thank you for the following helpers:\n{self.helpers.value}",
            )
        )
        for username in usernames:
            await self.bot.db.submit_score(username, 1)

        channel = self.bot.get_channel(self.bot.logs)  # 1357585230835224618

        await channel.send(
            embed=(
                self.bot.base_embed("Ticket Completed", "")
                .add_field(name="Ticket Creator", value=f"{self.user.name}")
                .add_field(name="AQW Username", value=f"{self.username}")
                .add_field(name="Reason", value=f"{self.reason}")
                .add_field(name="helpers", value=f"{self.helpers.value}", inline=False)
            )
        )
        await asyncio.sleep(2)
        await interaction.channel.delete(reason="Ticket complete")  # type: ignore - stfu
        return


class TicketView(discord.ui.View):
    def __init__(
        self,
        bot: FashionThing,
        user: discord.User | discord.Member,
        username: str,
        reason: str,
    ):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.username = username
        self.reason = reason

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user != self.user:
            return await interaction.response.send_message(
                embed=self.bot.base_embed(
                    "You are not the ticket owner",
                    "Only the ticket owner/admins can close the ticket",
                ),
                ephemeral=True,
            )
        modal = CloseModal(self.bot, self.user, self.username, self.reason)
        await interaction.response.send_modal(modal)


class FashionTicketModal(discord.ui.Modal):
    def __init__(self, bot: FashionThing, user: discord.User | discord.Member) -> None:
        self.ticket_id = uuid4()
        super().__init__(
            title="Fashion Assistance", timeout=None, custom_id=str(self.ticket_id)
        )
        self.bot = bot
        self.user = user

        self.task = discord.ui.TextInput(
            label="Task",
            min_length=3,
            max_length=30,
            placeholder="Item Hunting, IODA Suggestions, Etc...",
            required=True,
        )
        self.character_url = discord.ui.TextInput(
            label="Character URL (Optional)",
            min_length=10,
            placeholder="Your character set URL",
            required=False,
        )
        self.username = discord.ui.TextInput(
            label="AQW Username", placeholder="Your AQW Username here", required=True
        )
        self.add_item(self.task)
        self.add_item(self.character_url)
        self.add_item(self.username)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        aqw_username = self.username.value

        username_exists = await self.bot.verify_username(aqw_username)

        if not username_exists:
            await interaction.response.send_message(
                embed=self.bot.base_embed(
                    "Username not found!",
                    f"The AQWorlds username `{aqw_username}` does not appear to exist. Please double-check spelling and try again.",
                ),
                ephemeral=True,
            )
            return

        category = interaction.channel.category  # type: ignore - stupid ass python
        channel = await category.create_text_channel(
            f"ꜰᴀꜱʜɪᴏɴ-ꜱᴜᴘᴘᴏʀᴛ-{self.bot.replace_word(self.username.value)}"
        )
        await channel.send(
            content=f"<@&{self.bot.fashion_helper}> {self.user.mention}",
            embed=(
                self.bot.base_embed(
                    f"Fashion Assistance - {self.task.value}",
                    "Fashion Helpers were pinged, help will arrive shortly. After you're done please remember to credit your helpers when closing the ticket. They gain points for a monthly leaderboard.",
                )
                .add_field(name="Username", value=f"{aqw_username}")
                .add_field(name="Reason", value=f"{self.task.value}")
                .set_image(url=self.character_url.value)
            ),
            view=TicketView(self.bot, self.user, aqw_username, self.task.value),
        )
        await interaction.response.send_message(
            embed=self.bot.base_embed(
                "Ticket Created", f"Please move to {channel.mention} for your ticket."
            ),
            ephemeral=True,
        )
        return


class FashionInitView(discord.ui.View):
    def __init__(self, bot: FashionThing):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Get Fashion Assistance")
    async def ticket_create_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        modal = FashionTicketModal(self.bot, interaction.user)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Become a Fashion Helper!")
    async def become_helper(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        await interaction.user.add_roles(discord.Object(id=self.bot.fashion_helper))
        await interaction.response.send_message(
            embed=self.bot.base_embed(
                "Successfully added Role", "You are now a Fashion Helper!"
            ),
            ephemeral=True,
        )
