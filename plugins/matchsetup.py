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

def split_config_list(value):
    return [x.strip() for x in value.split(',')]

class matchsetup(commands.Cog):
    
    def __init__(self, bot, config = None, desc = None):
        print("Match setup plugin started.")
        self.bot = bot
        self.config = config
        self.desc = desc
        
    def parse_command(self, args):
        option = ""
        value_index = 0
        for arg in args:
            value_index += 1
            if (len(arg) > 1 and arg[0] == '-'):
                option = arg[1:]
                break
        
        value = ""
        next_args = []
        if (value_index < len(args)):
            next_arg = args[value_index]
            if (len(next_arg) and next_arg[0] != '-'):
                value = next_arg
                next_args = args[value_index+1:]
            else:
                next_args = args[value_index:]
        
        return option, value, next_args
    
    @commands.command(brief="", name='setup')
    async def setup(self, ctx, *args):
        option, value, left_args = self.parse_command(args)
        
        choice = ""
        choices = split_config_list(self.config.get("DEFAULT", option, fallback=None))
        cardinal = len(choices)
        
        if (len(value)):
            value = int(value)
        else:
            value = 0
        if (value <= 0 or value > cardinal):
            value = cardinal
        if (value > 0):
            choice = choices[random.randint(0, value-1)]
        
        dicts = [ _dict for _dict in self.desc
                 if ("title" in _dict and _dict["title"] == choice) ]
        nb_desc = len(dicts)
        desc = {}
        if (nb_desc >= 1):
            desc = dicts[random.randint(0, nb_desc-1)]
        
        embed = discord.Embed.from_dict(desc)
        if ("title" in desc and "category" in desc):
            embed.title = "Random " + desc["category"] + ": " + desc["title"]
        
        embed.colour = discord.Colour.random()
        
        await ctx.send(embed=embed)
        
        if (len(left_args)):
            await self.setup(ctx, *left_args)
    
def setup(bot):
    config = configparser.ConfigParser()
    config.read('config/setup.ini')
    
    json_file = open('config/setup_descriptions.json', encoding="utf8")
    desc = json.load(json_file)
    json_file.close()
    
    bot.add_cog(matchsetup(bot, config, desc))