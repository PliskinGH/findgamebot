# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 15:08:26 2022

@author: Pliskin
"""

import random
from discord.ext import commands
import configparser

def split_config_list(value):
    return [x.strip() for x in value.split(',')]

class matchsetup(commands.Cog):
    
    def __init__(self, bot, config = None):
        print("Match setup plugin started.")
        self.bot = bot
        self.config = config
        
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
        await ctx.send(choice)
        
        if (len(left_args)):
            await self.setup(ctx, *left_args)
    
def setup(bot):
    config = configparser.ConfigParser()
    config.read('config/setup.ini')
    bot.add_cog(matchsetup(bot, config))