import discord
from discord.ext import commands
import configparser

CONFIG_DEFAULT = "DEFAULT"
CONFIG_ID = "ID"
CONFIG_GAMES_COMMANDS = "GamesCommands"
CONFIG_GAMES_NAMES = "GamesFullNames"
CONFIG_GAMES_ROLES = "GamesRoles"

def split_config_list(value):
    return [x.strip() for x in value.split(',')]

class matchmaking(commands.Cog):
        
    @commands.command(pass_context=True, brief="", name='lfg')
    async def lfgCMD(self, ctx, *desc):
        games = []
        gamesNames = []
        gamesRoles = []
        
        guildId = ctx.guild.id
        
        for guild in self.config.sections():
            found = (guildId == self.config.getint(guild, CONFIG_ID, fallback=None))
            if (found):
                break
        
        if (not(found)):
            guild = CONFIG_DEFAULT
        
        games = split_config_list(self.config.get(guild, CONFIG_GAMES_COMMANDS, fallback=None))
        gamesNames = split_config_list(self.config.get(guild, CONFIG_GAMES_NAMES, fallback=None))
        gamesRoles = split_config_list(self.config.get(guild, CONFIG_GAMES_ROLES, fallback=None))
                
        gameWanted = "game"
        if (desc[0] in games):
            index = games.index(desc[0])
            if (len(gamesNames[index]) >= 1):
                gameWanted = "**" + gamesNames[index] + "** " + gameWanted
            if (len(gamesRoles[index]) >= 1):
                gameWanted += " (" + gamesRoles[index] + ")"
            desc = desc[1:]
        
        embed = discord.Embed(description="Playing: "+ctx.message.author.mention)
        text = ctx.message.author.mention+" is looking for a "+gameWanted+" with: " +" ".join(desc)+"\n For discussion about this game, please use a thread."
        
        messageSent = await ctx.send(text,embed=embed)

        await messageSent.add_reaction("👍")
        await messageSent.add_reaction("🔔")
        await messageSent.add_reaction("❌")
        await ctx.message.delete()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        validEmojis = ["👍","🔔","❌"]
        
        if int(payload.user_id) == int(self.bot.user.id):
            return False
        
        if str(payload.emoji.name) in validEmojis:
            channel = self.bot.get_channel(int(payload.channel_id))
            message = await channel.fetch_message(int(payload.message_id))
            #print("Valid emoji")
            
            #print(" ".join((message.content.split(" ")[1:])))
            if " ".join((message.content.split(" ")[1:])).startswith("is looking for a "):
                #print("Matches msg")
                #messageEmbed = message.embeds[0]
                if str(payload.emoji.name) == "👍":
                    reactedMentions = []
                    for messageReaction in message.reactions:
                        if str(messageReaction) == "👍":
                            reactedUsers = await messageReaction.users().flatten()
                            for reactedUser in reactedUsers:
                                if not reactedUser.id == self.bot.user.id:
                                    reactedMentions.append(reactedUser.mention)
                                
                    embed = discord.Embed(description="Playing: "+message.content.split(" ")[0]+" "+" ".join(reactedMentions))
                    await message.edit(content=message.content,embed=embed)
                    for messageReaction in message.reactions:
                        if str(messageReaction) == "🔔":
                            reactedUsers = await messageReaction.users().flatten()
                            for userToDm in reactedUsers:
                                if not userToDm.id == self.bot.user.id:
                                    try:
                                        await userToDm.send("A new user has joined your Root game! Head to the LFG Channel to say hello.")
                                    except:
                                        print("Failed to DM "+str(userToDm))
                    
                if str(payload.emoji.name) == "❌":
                    if int(payload.user_id) == int(self.bot.user.id):
                        return False
                    currentReacter = channel.guild.get_member(int(payload.user_id))
                    if currentReacter.mention == message.content.split(" ")[0]:
                        await message.edit(content="Game closed/full. Sorry!")
                    else:
                        print("Not game creator, cannot close.")
                    
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        validEmojis = ["👍"]
        
        if int(payload.user_id) == int(self.bot.user.id):
            return False
        
        if str(payload.emoji.name) in validEmojis:
            channel = self.bot.get_channel(int(payload.channel_id))
            message = await channel.fetch_message(int(payload.message_id))
            #print("Valid emoji")
            
            #print(" ".join((message.content.split(" ")[1:])))
            if " ".join((message.content.split(" ")[1:])).startswith("is looking for a "):
                #print("Matches msg")
                #messageEmbed = message.embeds[0]
                if str(payload.emoji.name) == "👍":
                    reactedMentions = []
                    for messageReaction in message.reactions:
                        if str(messageReaction) == "👍":
                            reactedUsers = await messageReaction.users().flatten()
                            for reactedUser in reactedUsers:
                                if not reactedUser.id == self.bot.user.id:
                                    reactedMentions.append(reactedUser.mention)
                                
                    embed = discord.Embed(description="Playing: "+message.content.split(" ")[0]+" "+" ".join(reactedMentions))
                    await message.edit(content=message.content,embed=embed)
    
    def __init__(self, bot, config = None):
        print("Matchmaking plugin started.")
        self.bot = bot
        self.config = config
    
def setup(bot):
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot.add_cog(matchmaking(bot, config))