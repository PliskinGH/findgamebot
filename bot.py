import discord
from discord.ext import commands

import os
from os.path import isfile, join
import traceback
import time
import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX')
if (PREFIX is None):
    PREFIX = "!"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=str(PREFIX), case_insensitive=True, \
                   heartbeat_timeout=300, intents=intents, \
                   help_command=None)
    
cogs_dir = "plugins"

@bot.event
async def on_ready():
    print('\nLogged in as:')
    print(" Username",bot.user.name)
    print(" User ID",bot.user.id)
    print("To invite the bot in your server use this link:\n https://discordapp.com/oauth2/authorize?&client_id="+str(bot.user.id)+"&scope=bot&permissions=0")
    print("Time now",str(datetime.datetime.now()))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid syntax")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid syntax")
    else:
        print(error, ctx)

def run_client(token):
    global bot
    
    while True:
        print("Starting at time",str(datetime.datetime.now()))
        loadPlugins()
        
        bot.run(token)
            
        for plugin in bot.extensions:
            plugin.unload()
            
        print("Restarting in 60 seconds")
        time.sleep(60)
        bot = commands.Bot(command_prefix=str(PREFIX), \
                           case_insensitive=True, heartbeat_timeout=300, \
                           intents=intents, help_command=None)

def loadPlugins():
    activadedPlugins = []
    with open(cogs_dir+"/activated.conf") as f:
        activadedPlugins = f.readlines()
        
    activadedPlugins = [x.strip() for x in activadedPlugins]

    for extension in [f for f in os.listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            if (str(extension)[-3:] == ".py") and (not str(extension) == "__init__.py"):
                if extension[:-3] in activadedPlugins:
                    bot.load_extension(cogs_dir + "." + extension[:-3])
                else:
                    print(str(extension[:-3])," disabled")
        except Exception as e:
            print('Failed to load extension {extension}.')
            traceback.print_exc()
    
if __name__ == "__main__":
    run_client(TOKEN)