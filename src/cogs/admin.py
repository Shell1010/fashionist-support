from __future__ import annotations
import os
import discord
from discord.ext import commands
from discord import app_commands
import subprocess


from typing import TYPE_CHECKING 
if TYPE_CHECKING:
    from src.bot import FashionThing

class Admin(commands.Cog):
    def __init__(self, bot: FashionThing):
        self.bot = bot

    admin = app_commands.Group(name="admin", description="Commands for admin related commands.")




    @admin.command(name="sync", description="Syncs command tree, bot admin only")
    @app_commands.describe(here="Syncs commands to this guild.")
    async def sync(self, ctx: discord.Interaction, here: bool = False):
        
        if not ctx.user.id in self.bot.admins.values():
            await ctx.response.send_message(embed=self.bot.base_embed("Permission Denied", "Only server admins can do this."))
            return
        
        await ctx.response.defer()
        try:
            for name, cog in self.bot.cogs.items():
                for cmd in cog.walk_commands():
                    self.bot.tree.add_command(cmd)
        except Exception as e:
            print(e)

        if here:
            await self.bot.tree.sync(guild=ctx.guild)
            await ctx.followup.send(embed=self.bot.base_embed("Synced Commands", description="Successfully synced commands locally"))
        else:
            await self.bot.tree.sync()
            await ctx.followup.send(embed=self.bot.base_embed("Synced Commands", description="Successfully synced commands globally"))
    


    @admin.command(name="reload", description="Reloads all cogs, bot admin only")
    async def reload(self, ctx: discord.Interaction):
        if ctx.user.id in self.bot.admins.values():
            await ctx.response.defer()
            for file in os.listdir("./src/cogs"):
                if file.endswith(".py") and "__init__" not in file:
                    try:
                        await self.bot.reload_extension(f"src.cogs.{file[:-3]}")
                    except Exception as e:
                        await ctx.followup.send(embed=self.bot.base_embed("Failed to Reload Cog", f"Could not reload cog {file}.\n{e}"))
            await ctx.followup.send(embed=self.bot.base_embed("Reload Complete", "All cogs reloaded successfully."))
        else:
            await ctx.response.send_message(embed=self.bot.base_embed("Unauthorized", "You do not have permission to use this command"), ephemeral=True)

    @admin.command(name="update", description="Pulls the latest updates from GitHub and reloads the bot, bot admin only")
    async def update(self, ctx: discord.Interaction):
        await ctx.response.defer()
        
        if ctx.user.id in self.bot.admins.values():
            # Step 1: Pull latest changes from GitHub
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            
            if "Already up to date" in result.stdout:
                await ctx.followup.send(embed=self.bot.base_embed("Update Check", "The bot is already up to date."))
                return
            
            elif result.returncode == 0:
                await ctx.followup.send(embed=self.bot.base_embed("Updating Bot", "Pulled latest changes successfully. Reloading cogs..."))

                # Step 2: Reload all cogs
                for file in os.listdir("./src/cogs"):
                    if file.endswith(".py") and "__init__" not in file:
                        try:
                            await self.bot.reload_extension(f"src.cogs.{file[:-3]}")
                        except Exception as e:
                            await ctx.followup.send(embed=self.bot.base_embed("Failed to Reload Cog", f"Could not reload cog {file}.\n{e}"))

                await ctx.followup.send(embed=self.bot.base_embed("Update Complete", "All cogs reloaded successfully."))
            else:
                # If there was an error pulling from GitHub
                await ctx.followup.send(embed=self.bot.base_embed("Update Failed", f"Could not pull updates from GitHub.\n{result.stderr}"))
        else:
            await ctx.followup.send(embed=self.bot.base_embed("Unauthorized", "You do not have permission to use this command."), ephemeral=True)

async def setup(bot: FashionThing):
    await bot.add_cog(Admin(bot))
