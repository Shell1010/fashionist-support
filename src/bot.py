import os
from typing import List, Optional

import aiohttp
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from .classes import EmbedHelper, DatabaseManager
import re

ALPHABET = {
    "a": "ᴀ",
    "b": "ʙ",
    "c": "ᴄ",
    "d": "ᴅ",
    "e": "ᴇ",
    "f": "ꜰ",
    "g": "ɢ",
    "h": "ʜ",
    "i": "ɪ",
    "j": "ᴊ",
    "k": "ᴋ",
    "l": "ʟ",
    "m": "ᴍ",
    "n": "ɴ",
    "o": "ᴏ",
    "p": "ᴘ",
    "q": "Q",
    "r": "ʀ",
    "s": "ꜱ",
    "t": "ᴛ",
    "u": "ᴜ",
    "v": "ᴠ",
    "w": "ᴡ",
    "x": "x",
    "y": "ʏ",
    "z": "ᴢ"
}

class FashionThing(commands.Bot):
    def __init__(self, token: str, admins: dict[str, int], db_uri: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.admins: dict[str, int] = admins
        self.db = DatabaseManager(self, db_uri) 
        self.token: str = token
        self.embed_helper: EmbedHelper = EmbedHelper()
        self.alphabet = ALPHABET
        self.fashion_helper = 1055311876382281830
        self.logs = 1357585230835224618
        # self.fashion_helper = 1382835286022684833
        # self.logs = 1341590622091345962
        self.session: Optional[aiohttp.ClientSession] = None

    def go(self):
        self.run(self.token)

    def base_embed(self, title: str, description: str, url: Optional[str] = None) -> discord.Embed:
        return self.embed_helper.base_embed(title, description, url)

    async def load_all_cogs(self):
        print("Loading cogs...")
        for file in os.listdir("./src/cogs"):
            if file.endswith(".py") and "__init__" not in file:
                try:
                    await self.load_extension(f"src.cogs.{file[:-3]}")
                except Exception as e:
                    print(f"Failed to load cog\n{e}")

        print("Cogs loaded.")

    def replace_word(self, text: str) -> str:
        new = ""
        for char in text.lower():
            new += self.alphabet[char]
        return new

    def title_except(self, text: str) -> str:
        articles = ['a', 'an', 'of', 'the', 'is']
        word_list = re.split(' ', text)       # re.split behaves as expected
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            final.append(word if word in articles else word.capitalize())
        return " ".join(final)

    async def get_resp(self, url: str) -> str:
        resp = await self.session.get(url)
        return await resp.text()

    async def is_armour(self, resp: str) -> bool:
        bs = BeautifulSoup(resp, "html.parser")
        div = bs.find(id="breadcrumbs")
        a = div.find("a", href="/armors") or div.find("a", href="/classes")
    
        return True if a else False


    async def get_image_url(self, resp: str) -> List[str]:
        images = []
        bs = BeautifulSoup(resp, "html.parser")
        try:
            div = bs.find(id="wiki-tab-0-0") # male
            if img := div.find("img"):
                if src := img.get("src"):
                    images.append(src)

            div = bs.find(id="wiki-tab-0-1") # female
            if img := div.find("img"):
                if src := img.get("src"):
                    images.append(src)
        except:
            # not armour - yes this is ass way of doing it
            div = bs.find(id="page-content")
            if gif := div.find(class_="gif-button"):
                if a := gif.find("a"):
                    if src := a.get("href"):
                        images.append(src)

            elif imgs := div.find_all("img"):
                if src := imgs[-1].get("src"):
                    images.append(src)

        return images

    async def search_item(self, item: str) -> List[str]:
        urls = []
        excluded_substrings = ["location", "monster"]
        resp = await self.session.get(f"http://aqwwiki.wikidot.com/search:main/fullname/{item}")
        bs = BeautifulSoup((await resp.text()), "html.parser")
        div = bs.find(class_="list-pages-item")
        try:
            if a_tags := div.find_all("a"):
                for a in a_tags:
                    if href := a.get("href"):
                        if not any(excluded_sub in href for excluded_sub in excluded_substrings):
                            urls.append(f"http://aqwwiki.wikidot.com{href}")
        except:
            pass

        return urls


    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_all_cogs()
        return await super().setup_hook()


    async def verify_username(self, username: str) -> bool:
        resp = await self.session.get(f"https://account.aq.com/CharPage?id={username}")
        if resp.ok:
            if not "Not Found" in (await resp.text()):
                return True
        return False


    async def sync(self):
        await self.tree.sync()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.user.name } is ONLINE!")
        # await self.sync()
