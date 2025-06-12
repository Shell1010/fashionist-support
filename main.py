import os

import discord
from dotenv import load_dotenv

from src.bot import FashionThing

load_dotenv()


def main():
    bot = FashionThing(
        os.environ["TOKEN"],
        {"daylah": 1105202115850285116, "fish": 1143657502941122580},
        os.environ["DB_URI"],
        intents=discord.Intents.all(),
        command_prefix="!",
        help_command=None,
    )

    bot.go()

if __name__ == "__main__":
    main()
