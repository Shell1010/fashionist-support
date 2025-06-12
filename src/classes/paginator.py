from __future__ import annotations

from typing import List
from uuid import uuid4

import discord


class QuerySelect(discord.ui.Select):
    def __init__(self, urls: List[str], author: discord.User | discord.Member):
        self.urls = urls


class QueryView(discord.ui.View):
    def __init__(self, urls: List[str], author: discord.User):
        super().__init__(timeout=None)
        self.urls = urls
        self.author = author
        self.page_select = QuerySelect(urls, author)
        self.add_item(self.page_select)
        self.current_choice = urls[0]




class ItemPaginator(discord.ui.View):
    def __init__(self, pages: List[discord.Embed], author: discord.User) -> None:
        super().__init__(timeout=None)
        self.pages = pages
        self.author = author
        self.current_page = 0

    @discord.ui.button(label="Female")
    async def show_female(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(embed=self.pages[-1], view=self)

    @discord.ui.button(label="Male")
    async def show_male(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(embed=self.pages[0], view=self)
