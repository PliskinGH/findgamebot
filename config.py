import os
from dotenv import load_dotenv

load_dotenv()

discordtoken = os.getenv('DISCORD_TOKEN')
prefix = os.getenv('COMMAND_PREFIX')