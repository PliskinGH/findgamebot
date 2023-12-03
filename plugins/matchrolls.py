# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 15:08:26 2022

@author: Pliskin
"""

import random
import discord
from discord.ext import commands
import configparser
import json

from utils import common

RANDOM_COMMAND = "random"
RANDOM_ALIASES = ["rand"]

class matchrolls(commands.Cog):
    
    def __init__(self, bot, config = None, desc = None):
        print("Match rolls plugin started.")
        self.bot = bot
        self.config = config
        self.desc = desc
        activity_text = str(self.bot.command_prefix) + RANDOM_COMMAND
        activity = self.bot.activity
        if (activity is None):
            activity = discord.Game(name=activity_text)
        else:
            activity.name += " | " + activity_text
        self.bot.activity = activity
    
    async def random_help(self, ctx):
        text = "Syntax:\n"
        text += "`" + ctx.prefix + RANDOM_COMMAND
        text += " <category> [<number> / <subset>]` where `<category>` is a type of set to roll from.\n"
        text += "Example of subsets:\n"
        text += "`" + ctx.prefix
        text += "random <category> 6` to roll from the first 6 items in the set.\n"
        text += "`" + ctx.prefix
        text += "random <category> 2,5-9` to roll from the second and 5th to 9th items.\n"
        
        guild = common.get_guild_from_config(self.config, ctx.guild.id)
        
        sets = self.config.items(guild)
        rolls_list = []
        cat_list = []
        rollset_list = []
        for cat, rollset in sets:
            if (not(len(cat)) or not(len(rollset))):
                continue
            if (rollset in rollset_list):
                if (cat in cat_list):
                    continue
                index = rollset_list.index(rollset)
                rollset = "alias for `"
                rollset += str(cat_list[index]) + "`"
            cat_list.append(cat)
            rollset_list.append(rollset)
        display_sets = list(zip(cat_list, rollset_list))
        align = len(max([cat for cat, rollset in display_sets], key=len))
        for cat, rollset in display_sets:
            roll_text = "• `"
            roll_text += str(cat)
            roll_text += " " * (align-len(str(cat))) + "`"
            if (len(rollset)):
                roll_text += " : " + str(rollset) + "."
            roll_text += "\n"
            rolls_list.append(roll_text)
        
        embed = discord.Embed(description="".join(rolls_list))
        text += "\nSets available on your server:\n"
        
        await ctx.send(text,embed=embed)
        
    def parse_command(self, args, guild):
        option = ""
        value_index = 0
        for arg in args:
            value_index += 1
            if (arg.isalpha() and arg.islower()):
                option = arg
                break
        
        choices = common.split_config_list(self.config.get(guild, option, fallback=None))
        cardinal = len(choices)
        
        value_list = []
        next_args = []
        subset_choices = []
        if (value_index < len(args)):
            next_arg = args[value_index]
            value_list = common.parse_intervals(next_arg, cardinal)
        
        if (len(value_list)):
            next_args = args[value_index+1:]
            subset_choices = [choices[i-1] for i in value_list]
        else:
            next_args = args[value_index:]
            subset_choices = choices
        
        return option, subset_choices, next_args
    
    @commands.command(brief="", name=RANDOM_COMMAND, aliases=RANDOM_ALIASES)
    async def random(self, ctx, *args):
        if (not(len(args)) or args[0] == common.HELP_COMMAND):
            return await self.random_help(ctx)
        
        guild = common.get_guild_from_config(self.config, ctx.guild.id)
        
        choice = ""
        option, choices, left_args = self.parse_command(args, guild)
        
        if (len(choices)):
            choice = random.choice(choices)
            footer_text = "Randomly chosen among: " + ", ".join(choices) + "."
        
        nb_desc = 0
        if (len(choice)):
            dicts = [ _dict for _dict in self.desc
                      if ("title" in _dict and _dict["title"] == choice) ]
            nb_desc = len(dicts)
        desc = {}
        if (nb_desc >= 1):
            desc = dicts[random.randrange(0, nb_desc)]
        
        if (len(desc)):
            embed = discord.Embed.from_dict(desc)
        
            if ("color" not in desc):
                embed.colour = discord.Colour.random()
            
            if ("title" in desc):
                if ("category" in desc):
                    embed.title = "Random " + desc["category"] + ": " + desc["title"]
                author_avatar = common.DEFAULT_AVATAR_URL
                display_avatar = ctx.message.author.display_avatar
                if (display_avatar is not None):
                    author_avatar = display_avatar.url
                embed.set_author(name=ctx.message.author.display_name,
                                 icon_url=author_avatar)
                embed.set_footer(text=footer_text)
                await ctx.send(embed=embed)
        
        if (len(left_args)):
            await self.random(ctx, *left_args)
    
async def setup(bot):
    config = configparser.ConfigParser()
    config.read('config/rolls.ini')
    
    json_file = open('config/rolls_descriptions.json', encoding="utf8")
    desc = json.load(json_file)
    json_file.close()
    
    await bot.add_cog(matchrolls(bot, config, desc))
