import asyncio
import os
import re
from datetime import date, datetime
from typing import List, Optional

import aiohttp
import discord
from bs4 import BeautifulSoup
from discord.ext import commands

from .classes import DatabaseManager, EmbedHelper

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
    "z": "ᴢ",
}


class FashionThing(commands.Bot):
    def __init__(
        self, token: str, admins: dict[str, int], db_uri: str, *args, **kwargs
    ) -> None:
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

    def base_embed(
        self, title: str, description: str, url: Optional[str] = None
    ) -> discord.Embed:
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
        articles = ["a", "an", "of", "the", "is"]
        word_list = re.split(" ", text)  # re.split behaves as expected
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
            div = bs.find(id="wiki-tab-0-0")  # male
            if img := div.find("img"):
                if src := img.get("src"):
                    images.append(src)

            div = bs.find(id="wiki-tab-0-1")  # female
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
        resp = await self.session.get(
            f"http://aqwwiki.wikidot.com/search:main/fullname/{item}"
        )
        bs = BeautifulSoup((await resp.text()), "html.parser")
        div = bs.find(class_="list-pages-item")
        try:
            if a_tags := div.find_all("a"):
                for a in a_tags:
                    if href := a.get("href"):
                        if not any(
                            excluded_sub in href for excluded_sub in excluded_substrings
                        ):
                            urls.append(f"http://aqwwiki.wikidot.com{href}")
        except:
            pass

        return urls

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_all_cogs()
        return await super().setup_hook()

    async def verify_username(self, username: str) -> bool:
        text = await self.get_char_page(username) 
        if not "Not Found" in text:
            return True
        return False


    async def get_char_page(self, username: str) -> str:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB",
            "artixmode": "launcher",
            "cache-control": "max-age=0",
            "cookie": "__cflb=04dTocX5CGvapQX63C16eHjNv6zbskMmRgUzsXQsRX; _gid=GA1.2.566334845.1749907274;_ gat_gtag_UA_43443388_4=1; _ga_1FTKJ82KTX=GS2.1.s1749907274$o35$g0$t1749907274$j60$l0$h0; _ga=GA1.1.1787332714.1739564226",
            "referer": "https://account.aq.com/CharPage?id={username}",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
        }
        resp = await self.session.get(f"https://account.aq.com/CharPage?id={username}", headers=headers)
        return await resp.text()

    async def monthly_check(self) -> None:
        while True:
            await asyncio.sleep(3600)
            month = datetime.now().strftime("%B")
            db_month = (await self.db.get_month())[0]
            print(db_month['value'], month)
            if db_month['value'] != month:
                channel = self.get_channel(self.logs)
                top_3 = await self.db.get_leaderboard(3)
                msg = ""
                for idx, mem in enumerate(top_3, 1):
                    msg += f"{idx}. {mem['username']} ({mem['score']})\n"
                await channel.send(
                    content=f"<@&{self.fashion_helper}>",
                    embed=self.base_embed(
                        "Monthly Winners",
                        f"Here are the Top 3 helpers for this month\n\n{msg}",
                    )
                )

                await self.db.reset()
                await self.db.update_month(month)

    async def sync(self):
        await self.tree.sync()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.user.name } is ONLINE!")
        # await self.sync()
        # await self.db.submit_score("archfishy", 100)
        # await self.db.update_month("January")
        asyncio.create_task(self.monthly_check())
