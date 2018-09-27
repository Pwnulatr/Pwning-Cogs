import os
import discord
from datetime import date
from discord.ext import commands
from .utils.dataIO import dataIO

__author__ = "Pwnulatr"
__version__ = "2.1.2"

PATH = "data/pwning-cogs/outagecounter/"
JSON = PATH + "tally.json"


class Outagetally:
    """A joke tally counter for the amount of times my internet goes out"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json(JSON)

    @commands.command(no_pm=False, pass_context=True)
    async def internetwentout(self, ctx):
        """Just adds one to the tally"""

        await self.bot.type()
        if ctx.message.author.id not in self.settings:
            self.settings[ctx.message.author.id] = {"Tally": 1, "Last Outage": date.today()}
            dataIO.save_json(JSON, self.settings)
            await self.bot.reply("This appears to be your first outage on record.")
        elif ctx.message.author.id in self.settings:
            auth_id = self.settings[ctx.message.author.id]
            auth_id["Tally"] = auth_id['Tally'] + 1
            auth_id["Last Outage"] = date.today()
            dataIO.save_json(JSON, self.settings)
            await self.bot.reply(f"Logged! You're currently at {auth_id['Tally'] + 1} outages!")

    @commands.command(no_pm=False, pass_context=True)
    async def howmanytimes(self, ctx, *, user: discord.Member = None):
        """Says what the current tally is"""

        if not user:
            user = ctx.message.author

        if user.id in self.settings:
            auth_id = self.settings[user.id]
            info = discord.Embed(colour=user.colour)
            info.add_field(name="Total Disconnects", value=auth_id["Tally"])
            info.add_field(name="Last Outage", value=auth_id["Last Outage"])

            name = " | ".join((str(user), user.nick)) if user.nick else str(user)
            if user.avatar_url:
                info.set_author(name=name, url=user.avatar_url)
                info.set_thumbnail(url=user.avatar_url)
            else:
                info.set_author(name=name)
            try:
                await self.bot.say(embed=info)
            except discord.HTTPException:
                await self.bot.say("Uh oh! I need the `Embed Links` permission to send fancy embedded messages!")
        elif user.id not in self.settings:
            if user.id == ctx.message.author.id:
                msg = ("You are not currently in the database. You need to log your first outage before I can tell you "
                       "what your outage statistics are.")
            else:
                msg = ("That user is currently not in the database. They would need to log their first outage before I "
                       "can display their statistics.")
            await self.bot.reply(msg)


def setup(bot):
    if not os.path.exists(PATH):
        print("Creating outage counter folder...")
        os.makedirs(PATH)

    if not dataIO.is_valid_json(JSON):
        print("Creating empty tally.json...")
        dataIO.save_json(JSON, {})

    bot.add_cog(Outagetally(bot))
