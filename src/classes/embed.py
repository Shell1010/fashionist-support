from __future__ import annotations
import discord
from typing import Optional, Tuple, Union

class EmbedHelper:
    def __init__(self, color: str ="#cbbb9c") -> None:
        self.color: discord.Color = discord.Color.from_str(color)

    def base_embed(self, title: str, description: str, url: Optional[str] = None) -> discord.Embed:
        return (
            discord.Embed(title=title, description=description, color=self.color, url=url)
        )
