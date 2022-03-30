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

class matchrolls(commands.Cog):
    
    def __init__(self, bot, config = None, desc = None):
        print("Match rolls plugin started.")
        self.bot = bot
        self.config = config
        self.desc = desc
        
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
    
    @commands.command(brief="", name='random')
    async def random(self, ctx, *args):
        guild = common.get_guild_from_config(self.config, ctx.guild.id)
        
        choice = ""
        option, choices, left_args = self.parse_command(args, guild)
        
        if (len(choices)):
            choice = random.choice(choices)
            footer_text = "Randomly chosen among: "+ ", ".join(choices) + "."
        
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
                embed.set_footer(text=footer_text)
                await ctx.send(embed=embed)
        
        if (len(left_args)):
            await self.random(ctx, *left_args)
    
def setup(bot):
    config = configparser.ConfigParser()
    config.read('config/rolls.ini')
    
    json_file = open('config/rolls_descriptions.json', encoding="utf8")
    desc = json.load(json_file)
    json_file.close()
    
    bot.add_cog(matchrolls(bot, config, desc))