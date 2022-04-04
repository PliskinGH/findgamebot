import discord
from discord.ext import commands

import os
from os.path import isfile, join
import traceback
import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX')
if (PREFIX is None):
    PREFIX = "!"

intents = discord.Intents.all()
intents.typing = False
    
cogs_dir = "plugins"

bot = commands.Bot(command_prefix=str(PREFIX), case_insensitive=True, \
                   heartbeat_timeout=300, intents=intents, \
                   help_command=None)

@bot.event
async def on_ready():
    print('\nLogged in as:')
    print(" Username",bot.user.name)
    print(" User ID",bot.user.id)
    print("To invite the bot in your server use this link:\n https://discordapp.com/oauth2/authorize?&client_id="+str(bot.user.id)+"&scope=bot&permissions=0")
    print("Time now",str(datetime.datetime.now()))

@bot.event
async def on_command_error(ctx, error):
    print(error, ctx)

def load_plugins():
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
        except Exception:
            print('Failed to load extension {extension}.')
            traceback.print_exc()
    
if __name__ == "__main__":
    print("Starting at time", str(datetime.datetime.now()))
    load_plugins()
    
    bot.run(TOKEN)