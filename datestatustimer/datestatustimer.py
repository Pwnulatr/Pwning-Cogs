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
__version__ = "1.1.3"

monthname = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"}


bot = None
file_path = "data/pwning-cogs/datestatustimer/settings.json"
settings = dataIO.load_json(file_path)
last_check = None


def owner_command(hidden=False):
    def decorator(func):
        return datestatus.command(name=func.__name__[1:-11], pass_context=False, hidden=hidden)(checks.is_owner()(func))
    return decorator


def change_settings(d: Dict[str, any]):
    for k, v in d.items():
        settings[k] = v
    dataIO.save_json(file_path)


class Datestatustimer:
    def __init__(self, _bot):
        global bot
        bot = _bot


@commands.group(pass_context=True)
async def datestatus(ctx):
    if ctx.invoked_subcommand is None:
        await send_cmd_help(ctx)


@owner_command()
async def _date_datestatus(self, month: int, day: int):
    try:
        datetime.datetime.strptime(f"{month}-{day}", "%m-%d")
        change_settings({"MONTH_NUMBER": month, "DAY_NUMBER": day})
        msg = f"Date set to {day} of {monthname[month]}"
    except ValueError:
        msg = "You have not entered a valid date.\nBe sure it's formatted as `month day`"
    await self.bot.say(msg)


@owner_command()
async def _printdate_datestatus(self):
    await self.bot.say(f"Counting down towards {monthname[settings['MONTH_NUMBER']]} {settings['DAY_NUMBER']}")


@owner_command()
async def _name_datestatus(self, *, name=None):
    change_settings({"DATE_NAME": name})
    await self.bot.say(f"Date name successfully set to `{name}`" if name else "Date name cleared.")


@owner_command()
async def _force_update_datestatus():
    status_verify = status_creator()

    await bot.change_presence(game=discord.Game(name=status_verify))
    global last_check
    last_check = int(time.perf_counter())
    await bot.say("Done.")


@owner_command(hidden=True)
async def _debug_datestatus():
    await bot.say(
        f"Status: {self.status_creator()}\n"
        f"Days Remaining: {self.datecheck()}\n"
        f"Datatype for days: {type(self.datecheck())}\n"
        f"Name of Date: {settings['DATE_NAME']}"
    )


def datecheck():
    today = date.today()
    monthnumber = settings["MONTH_NUMBER"]
    daysnumber = settings["DAY_NUMBER"]
    targetdate = date(today.year, monthnumber, daysnumber)

    if targetdate < today:
        targetdate = targetdate.replace(year=today.year + 1)
        daysremain = abs(targetdate - today)
        return daysremain.days
    else:
        daysremain = abs(targetdate - today)
        return daysremain.days


def status_creator():
    days_remaining = datecheck()
    datename = settings["DATE_NAME"]
    if datename is None:
        if days_remaining == 1:
            return "1 Day Remaining!"
        else:
            return f"{days_remaining} Days Remaining!"
    else:
        if days_remaining == 1:
            return f"1 Day until {datename}!"
        else:
            return f"{days_remaining} Days until {datename}!"


async def check_date_looper(self, message):
    if not message.channel.is_private:
        status_verify = self.status_creator()
        current_game = str(message.server.me.game)

        if self.last_check is None:  # first run
            self.last_check = int(time.perf_counter())
            await self.bot.change_presence(game=discord.Game(name=status_verify))

        if abs(self.last_check - int(time.perf_counter())) >= 3600:
            self.last_check = int(time.perf_counter())
            if status_verify != current_game:
                await self.bot.change_presence(game=discord.Game(name=status_verify))


def check_folders():
    folder = "data/pwning-cogs/datestatustimer"
    if not os.path.exists(folder):
        print("Creating datestatustimer folder...")
        os.makedirs(folder)


def check_files():
    f = "data/pwning-cogs/datestatustimer/settings.json"
    settings = {"DATE_NAME": "New Year's", "MONTH_NUMBER": 1, "DAY_NUMBER": 1}

    if not dataIO.is_valid_json(f):
        print("Creating example settings.json for datestatustimer...")
        dataIO.save_json(f, settings)


def setup(bot):
    check_folders()
    check_files()
    n = Datestatustimer(bot)
    bot.add_listener(n.check_date_looper, "on_message")
    bot.add_cog(n)
