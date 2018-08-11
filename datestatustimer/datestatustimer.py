from discord.ext import commands
from __main__ import send_cmd_help
from .utils.dataIO import dataIO
from datetime import date
from cogs.utils import checks
import discord
import os
import time
import datetime
from typing import Dict


__author__ = "Pwnulatr and Tyler"
__version__ = "1.1.4"


async def test_decorator(arg):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.bot.say(arg)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def owner_command(hidden=False, context=False):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            decorator1 = self.datestatus.command(name=func.__name__[1:-11], pass_context=context, hidden=hidden)
            self.bot.say("The next 3 lines are things")
            self.bot.say(decorator1)
            decorator2 = checks.is_owner()
            self.bot.say(decorator2)
            q = decorator1(decorator2(func(self, *args, **kwargs)))
            self.bot.say(q)
            return q
        return wrapper
    return decorator


class Datestatustimer:
    """Calculates the time between dates and makes it the bot \"playing\" status"""
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/pwning-cogs/datestatustimer/settings.json"
        self.settings = dataIO.load_json(self.file_path)
        self.last_check = None

    def change_settings(self, d: Dict[str, any]):
        for k, v in d.items():
            self.settings[k] = v
        dataIO.save_json(self.file_path, self.settings)

    @commands.group(pass_context=True)
    async def datestatus(self, ctx):
        """These are the settings for the date status cog"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @datestatus.command()
    @checks.is_owner()
    async def date(self, month: int, day: int):
        """Set the date for countdown"""
        try:
            datetime.datetime.strptime(f"{month}-{day}", "%m-%d")
            self.change_settings({"MONTH_NUMBER": month, "DAY_NUMBER": day})
            msg = f"Date set to {day} of {month_name(month)}"
        except ValueError:
            msg = "You have not entered a valid date.\nBe sure it's formatted as `month day`"
        await self.bot.say(msg)

    @datestatus.command()
    @checks.is_owner()
    async def printdate(self):
        """Prints date that the cog is counting towards"""
        await self.bot.say(f"Counting down towards "
                           f"{month_name(self.settings['MONTH_NUMBER'])} {self.settings['DAY_NUMBER']}")

    @owner_command()
    async def _name_datestatus(self, *, name=None):
        """Name for the day that you are counting down for. Leave blank to clear."""
        self.change_settings({"DATE_NAME": name})
        await self.bot.say(f"Date name successfully set to `{name}`" if name else "Date name cleared.")

    @owner_command()
    async def _force_update_datestatus(self):
        """Forces an update of the status on command"""
        status_verify = self.create_status()
        await self.bot.change_presence(game=discord.Game(name=status_verify))
        self.last_check = int(time.perf_counter())
        await self.bot.say("Done.")

    def check_date(self):
        today = date.today()
        target_date = date(today.year, self.settings["MONTH_NUMBER"], self.settings["DAY_NUMBER"])

        if target_date < today:
            target_date = target_date.replace(year=today.year + 1)
        days_remain = abs(target_date - today)
        return days_remain.days

    def create_status(self):
        days_left = self.check_date()
        date_name = f" until {self.settings['DATE_NAME']}" if self.settings["DATE_NAME"] is not None else "Remaining"
        day_pluralized = "Day" if days_left == 1 else "Days"
        return f"{days_left} {day_pluralized} {date_name}!"


def month_name(month: int):
    return datetime.date(1900, month, 1).strftime('%B')


def setup(bot):
    folder = "data/pwning-cogs/datestatustimer"
    file = folder + "/settings.json"

    if not os.path.exists(folder):  # NOTE: Beware of race condition here.
        os.makedirs(folder)

    if not dataIO.is_valid_json(file):
        dataIO.save_json(file, {"DATE_NAME": "New Year's", "MONTH_NUMBER": 1, "DAY_NUMBER": 1})

    bot.add_cog(Datestatustimer(bot))
