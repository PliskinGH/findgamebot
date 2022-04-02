import discord
from discord.ext import commands
import configparser

from utils import common
CONFIG_GAMES_COMMANDS = "GamesCommands"
CONFIG_GAMES_NAMES = "GamesFullNames"
CONFIG_GAMES_ROLES = "GamesRoles"

EMOJI_JOIN = "👍"
EMOJI_NOTIFY = "🔔"
EMOJI_CLOSE = "❌"

class matchmaking(commands.Cog):
    
    def __init__(self, bot, config = None):
        print("Match making plugin started.")
        self.bot = bot
        self.config = config
    
    def get_configured_games(self, guild_id):
        games = []
        gamesNames = []
        gamesRoles = []
        
        guild = common.get_guild_from_config(self.config, guild_id)
        
        games = common.split_config_list(self.config.get(guild, CONFIG_GAMES_COMMANDS, fallback=None))
        gamesNames = common.split_config_list(self.config.get(guild, CONFIG_GAMES_NAMES, fallback=None))
        gamesRoles = common.split_config_list(self.config.get(guild, CONFIG_GAMES_ROLES, fallback=None))
        
        return (games, gamesNames, gamesRoles)
    
    async def lfg_help(self, ctx):
        text = "Syntax:\n"
        text += "`" + ctx.prefix
        text += "lfg <game> <description>` where `<game>` is a game available on the server with a corresponding role to ping.\n"
        text += "or\n"
        text += "`" + ctx.prefix
        text += "lfg <description>` for a custom game (no automatic ping).\n"
        
        games, gamesNames, _ = self.get_configured_games(ctx.guild.id)
        
        commands_list = []
        align = len(max(games, key=len))
        for game in games:
            index = games.index(game)
            command_text = "• `"
            command_text += game
            command_text += " " * (align-len(game)) + "`"
            if (len(gamesNames) == len(games) and len(gamesNames[index])):
                command_text += " : Looking for "
                command_text += common.indefinite_article(gamesNames[index]) + " "
                command_text += "**" + gamesNames[index] + "** game."
            command_text += "\n"
            commands_list.append(command_text)
        
        embed = discord.Embed(description="".join(commands_list))
        text += "\nGames available on your server:\n"
        
        await ctx.send(text,embed=embed)
        
    async def lfg_match(self, ctx, *desc):
        games, gamesNames, gamesRoles = self.get_configured_games(ctx.guild.id)
                
        gameWanted = "game"
        article = "a"
        if (desc[0] in games):
            index = games.index(desc[0])
            if (len(gamesNames) == len(games) and len(gamesNames[index])):
                gameWanted = "**" + gamesNames[index] + "** " + gameWanted
            if (len(gamesRoles) == len(games) and len(gamesRoles[index])):
                gameWanted += " (" + gamesRoles[index] + ")"
            desc = desc[1:]
            article = common.indefinite_article(gamesNames[index])
        
        embed = discord.Embed(description="Playing: "+ctx.message.author.mention)
        text = ctx.message.author.mention + " is looking for "
        text += article + " "
        text += gameWanted + " with: " + " ".join(desc)
        text += "\n For discussion about this game, please use a thread."
        
        messageSent = await ctx.send(text,embed=embed)

        await messageSent.add_reaction("👍")
        await messageSent.add_reaction("🔔")
        await messageSent.add_reaction("❌")
        await ctx.message.delete()
    
    @commands.command()
    async def lfg(self, ctx, *desc):
        if (desc[0] == common.HELP_COMMAND):
            return await self.lfg_help(ctx)
        else:
            return await self.lfg_match(ctx, *desc)
    
    @commands.command()
    async def lfg_v2(self, ctx, *desc):
        games, gamesNames, gamesRoles = self.get_configured_games(ctx.guild.id)
                
        gameWanted = "custom"
        gameRole = ""
        if (desc[0] in games):
            index = games.index(desc[0])
            if (len(gamesNames) == len(games) and len(gamesNames[index]) >= 1):
                gameWanted = gamesNames[index]
            if (len(gamesRoles) == len(games) and len(gamesRoles[index]) >= 1):
                gameRole = gamesRoles[index]
            desc = desc[1:]
        
        text = ""
        if (len(desc)):
            text += " ".join(desc) + "\n"
        text += "For discussion about this game, please use a thread." 
        embed = discord.Embed(description=text)
        
        if (len(gameRole)):
            embed.add_field(name="Target", value=gameRole, inline=True)
        
        field_text = ctx.message.author.mention
        embed.add_field(name="Player 1", value=field_text, inline=True)
        
        embed.set_author(name=ctx.message.author.name,
                         icon_url=str(ctx.message.author.avatar.url))
        embed.title = "Looking for " 
        embed.title += common.indefinite_article(gameWanted)
        embed.title += " " + gameWanted + " game"
        embed.set_thumbnail(url=str(ctx.message.author.avatar.url))
        embed.colour = ctx.message.author.colour
        
        messageSent = await ctx.send(embed=embed)

        await messageSent.add_reaction("👍")
        await messageSent.add_reaction("🔔")
        await messageSent.add_reaction("❌")
        await ctx.message.delete()
        
    async def refresh_message_embed(self, message, user, emoji):
        embeds = message.embeds
        if (not(len(embeds))):
            return
        embed = embeds[0]
        
        if (str(emoji.name) == EMOJI_JOIN):
            players = []
            users_to_notify = []
            for reaction in message.reactions:
                reaction_users = await reaction.users().flatten()
                reaction_users.remove(self.bot.user)
                if str(reaction) == EMOJI_JOIN:
                    players = reaction_users
                if str(reaction) == EMOJI_NOTIFY:
                    users_to_notify = reaction_users
            
            fields = embed.fields
            embed.clear_fields()
            number = 1
            for field in fields:
                if (field.name == "Target"):
                    embed.add_field(name = field.name, value=field.value, inline=True)
                elif (field.name[:6] == "Player"):
                    if (not(field.name[7:].isdigit())):
                        continue
                    if (field.value != user.mention):
                        embed.add_field(name = "Player " + str(number), value=field.value, inline=True)
                        number += 1
            if (user in players):
                embed.add_field(name="Player " + str(number), value=user.mention, inline=True)
                for user_to_notify in users_to_notify:
                    try:
                        await user_to_notify.send("A new user has joined your game! Head to the LFG Channel to say hello.")
                    except:
                        print("Failed to DM " + str(user_to_notify))
            await message.edit(embed=embed)
                
        if str(emoji.name) == EMOJI_CLOSE:
            embed.description = "Game closed/full. Sorry!"
            await message.edit(embed=embed)
        
    async def refresh_message(self, message, user, emoji, notify=True):
        if str(emoji.name) == "👍":
            reactedMentions = []
            for messageReaction in message.reactions:
                if str(messageReaction) == "👍":
                    reactedUsers = await messageReaction.users().flatten()
                    for reactedUser in reactedUsers:
                        if not reactedUser.id == self.bot.user.id:
                            reactedMentions.append(reactedUser.mention)
                        
            embed = discord.Embed(description="Playing: "+message.content.split(" ")[0]+" "+" ".join(reactedMentions))
            await message.edit(content=message.content,embed=embed)
            
            if (notify):
                for messageReaction in message.reactions:
                    if str(messageReaction) == "🔔":
                        reactedUsers = await messageReaction.users().flatten()
                        for userToDm in reactedUsers:
                            if not userToDm.id == self.bot.user.id:
                                try:
                                    await userToDm.send("A new user has joined your Root game! Head to the LFG Channel to say hello.")
                                except:
                                    print("Failed to DM "+str(userToDm))
            
        if str(emoji.name) == "❌":
            if user.mention == message.content.split(" ")[0]:
                await message.edit(content="Game closed/full. Sorry!")
            else:
                print("Not game creator, cannot close.")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): # Todo: refactor
        validEmojis = ["👍","❌"]
        
        if int(payload.user_id) == int(self.bot.user.id):
            return False
        
        if str(payload.emoji.name) in validEmojis:
            user = self.bot.get_user(int(payload.user_id))
            channel = self.bot.get_channel(int(payload.channel_id))
            message = await channel.fetch_message(int(payload.message_id))
            if (message.author.id != self.bot.user.id):
                return False
            
            title = ""
            if (len(message.embeds)):
                title = str(message.embeds[0].title)
            if (title.startswith("Looking for a")):
                return await self.refresh_message_embed(message, user, payload.emoji)
            elif (" ".join((message.content.split(" ")[1:])).startswith("is looking for a ")):
                return await self.refresh_message(message, user, payload.emoji)
                    
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload): # Todo: refactor
        validEmojis = ["👍"]
        
        if int(payload.user_id) == int(self.bot.user.id):
            return False
        
        if str(payload.emoji.name) in validEmojis:
            user = self.bot.get_user(int(payload.user_id))
            channel = self.bot.get_channel(int(payload.channel_id))
            message = await channel.fetch_message(int(payload.message_id))
            if (message.author.id != self.bot.user.id):
                return False
            
            title = ""
            if (len(message.embeds)):
                title = str(message.embeds[0].title)
            if (title.startswith("Looking for a")):
                return await self.refresh_message_embed(message, user, payload.emoji)
            elif " ".join((message.content.split(" ")[1:])).startswith("is looking for a "):
                return await self.refresh_message(message, user, payload.emoji, notify=False)
    
def setup(bot):
    config = configparser.ConfigParser()
    config.read('config/games.ini')
    bot.add_cog(matchmaking(bot, config))
    print(bot.cogs["matchmaking"].get_commands())