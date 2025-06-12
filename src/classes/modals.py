from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

import discord

if TYPE_CHECKING:
    from ..bot import FashionThing


class CloseModal(discord.ui.Modal):
    def __init__(self, bot: FashionThing, user: discord.User | discord.Member) -> None:
        super().__init__(title="Closing Ticket", timeout=None, custom_id=str(uuid4()))
        self.bot = bot
        self.user = user

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
            await interaction.response.send_message(
                embed=self.bot.base_embed(
                    "Username not found!",
                    f"The following usernames weren't found, please double check spelling!\n{'\n'.join(not_found)}",
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
        await asyncio.sleep(2)
        await interaction.channel.delete(reason="Ticket complete") # type: ignore - stfu
        return


class TicketView(discord.ui.View):
    def __init__(self, bot: FashionThing, user: discord.User | discord.Member):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user

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
        modal = CloseModal(self.bot, self.user)
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
            f"fashion-support-{self.username.value.lower()}"
        )
        await channel.send(
            embed=self.bot.base_embed(
                f"Fashion Assistance - {self.task.value}",
                "Use this channel to discuss stuff yes (i forgot tell me what to add here)",
            ),
            view=TicketView(self.bot, self.user),
        )
        await interaction.response.send_message(
            embed=self.bot.base_embed("Ticket Created", f"Please move to {channel.mention} for your ticket."),
            ephemeral=True
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
