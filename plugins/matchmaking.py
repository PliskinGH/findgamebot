import discord
from discord.ext import commands, tasks
import configparser
import re

from utils import common

LFG_COMMAND = "lfg"

CONFIG_GAMES_COMMANDS = "GamesCommands"
CONFIG_GAMES_NAMES = "GamesFullNames"
CONFIG_GAMES_ROLES = "GamesRoles"
CONFIG_GAMES_ICONS = "GamesIcons"
CONFIG_GAMES_COLORS = "GamesColors"
CONFIG_GAMES_FORUMS = "GamesForums"
CONFIG_GAMES_TAGS = "GamesTags"
CONFIG_GAMES_VISIBILITY = "GamesVisibility"

EMOJI_JOIN = "👍"
EMOJI_NOTIFY = "🔔"
EMOJI_CANCEL = "❌"
EMOJI_START = "✅"
EMOJIS_VALID = [EMOJI_JOIN, EMOJI_NOTIFY, EMOJI_CANCEL, EMOJI_START]
EMOJIS_CLOSE = [EMOJI_CANCEL, EMOJI_START]

DEFAULT_AVATAR_URL = "https://i.imgur.com/xClQZ1Q.png"

THREAD_TYPES = [discord.ChannelType.public_thread,
                discord.ChannelType.private_thread,
                discord.ChannelType.news_thread]

class matchmaking(commands.Cog):
    
    def __init__(self, bot, config = None):
        print("Match making plugin started.")
        self.bot = bot
        self.config = config
        
        activity_text = str(self.bot.command_prefix) + LFG_COMMAND
        activity = self.bot.activity
        if (activity is None):
            activity = discord.Game(name=activity_text)
        else:
            activity.name += " | " + activity_text
        self.bot.activity = activity
        
        self.custom_emoji_re = re.compile(r"<:[\w]+:[\d]+>")
        
        ## New feature to converge
        # self.threads = []
        # self.refresh_threads.start()
        
    async def cog_unload(self):
        # self.refresh_threads.cancel()
        await super().cog_unload()
    
    def get_configured_games(self, guild_id, *args):
        guild = common.get_guild_from_config(self.config, guild_id)
        
        result = []
        for arg in args:
            result.append(common.split_config_list(self.config.get(guild, arg, fallback=None)))
        
        return tuple(result)
    
    @tasks.loop(hours=23)
    async def refresh_threads(self):
        valid_threads = []
        for thread in self.threads:
            try:
                if (not(thread.archived)):
                    await thread.send(content="Daily refresh! Enjoy!\nIf this game is over, please let me know!")
                    valid_threads.append(thread)
            except Exception as error:
                print(error)
        self.threads = valid_threads
        print("Refreshed threads:\n", self.threads)
    
    async def lfg_help(self, ctx):
        text = "Syntax:\n"
        text += "`" + ctx.prefix + LFG_COMMAND
        text += " <game> <description>` where `<game>` is a game available on the server with a corresponding role to ping.\n"
        text += "or\n"
        text += "`" + ctx.prefix + LFG_COMMAND
        text += " <description>` for a custom game (no automatic ping).\n"
        
        games, gamesNames = self.get_configured_games(ctx.guild.id, CONFIG_GAMES_COMMANDS, CONFIG_GAMES_NAMES)
        
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
    
    @commands.command(name=LFG_COMMAND)
    async def lfg(self, ctx, *desc):
        if (not(len(desc)) or desc[0] == common.HELP_COMMAND):
            return await self.lfg_help(ctx)
        elif (ctx.channel.type in THREAD_TYPES):
            return await self.rename_thread(ctx, *desc)
        else:
            return await self.lfg_v2(ctx, *desc)
    
    @commands.command()
    async def lfg_v2(self, ctx, *desc):
        games, gamesNames, gamesRoles, gamesIcons, gamesColors = \
        self.get_configured_games(ctx.guild.id, CONFIG_GAMES_COMMANDS, \
                                  CONFIG_GAMES_NAMES, CONFIG_GAMES_ROLES, \
                                  CONFIG_GAMES_ICONS, CONFIG_GAMES_COLORS)
                
        gameWanted = "custom"
        gameRole = ""
        gameIcon = ""
        gameColor = ""
        if (len(desc) and desc[0] in games):
            index = games.index(desc[0])
            if (len(gamesNames) == len(games) and len(gamesNames[index])):
                gameWanted = gamesNames[index]
            if (len(gamesRoles) == len(games) and len(gamesRoles[index])):
                gameRole = gamesRoles[index]
            if (len(gamesIcons) == len(games) and len(gamesIcons[index])):
                gameIcon = gamesIcons[index]
            if (len(gamesColors) == len(games) and len(gamesColors[index])):
                gameColor = gamesColors[index]
            desc = desc[1:]
        
        text = ""
        if (len(desc)):
            text += " ".join(desc)
        embed = discord.Embed(description=text)
        embed.set_footer(text="For discussion about this game, please use a thread.\nIt will be created for you when you close the game.")
        
        if (len(gameRole)):
            embed.add_field(name="Target", value=gameRole, inline=True)
        
        # Member and User return different mentions for server nicknames...
        # So this :
        # field_text = ctx.message.author.mention
        # can give exclamation marks on the IDs
        # and can break comparisons of mentions when reacting
        # We need the User object
        user = self.bot.get_user(int(ctx.message.author.id))
        field_text = user.mention
        embed.add_field(name="Host", value=field_text, inline=True)
        
        author_avatar = common.DEFAULT_AVATAR_URL
        display_avatar = ctx.message.author.display_avatar
        if (display_avatar is not None):
            author_avatar = display_avatar.url
        embed.set_author(name=ctx.message.author.display_name,
                         icon_url=author_avatar)
        
        embed.title = "Looking for " 
        embed.title += common.indefinite_article(gameWanted)
        embed.title += " " + gameWanted + " game"
        
        if (not(len(gameIcon))):
            gameIcon = common.DEFAULT_AVATAR_URL
        embed.set_thumbnail(url=gameIcon)
        
        if (not(len(gameColor))):
            gameColor = ctx.message.author.colour
        embed.colour = gameColor
    
        try:
            await ctx.message.delete()
        except Exception as error:
            print(error)
        
        try:
            # Ghost pings are not reliable anymore...
            # if (len(gameRole)):
            #     bot_message = await ctx.send(content=gameRole)
            #     await bot_message.edit(content="", embed=embed)
            # else:
            #     bot_message = await ctx.send(content="", embed=embed)
            bot_message = await ctx.send(content=gameRole, embed=embed)
            for emoji in EMOJIS_VALID:
                await bot_message.add_reaction(emoji)
        except Exception as error:
            print(error)
    
    @commands.command()
    async def rename_thread(self, ctx, *desc):
        thread = ctx.channel
        if (not(thread.type in THREAD_TYPES)):
            return False
        
        if (int(thread.owner_id) != int(self.bot.user.id)):
            return False
        
        try:
            await thread.edit(name=common.clean_thread_title(" ".join(desc),
                                                        self.custom_emoji_re))
        except Exception as e:
            print(e)
    
    @commands.Cog.listener(name = "on_raw_reaction_add")
    @commands.Cog.listener(name = "on_raw_reaction_remove")
    async def refresh_message_embed(self, payload):
        if int(payload.user_id) == int(self.bot.user.id):
            return False
        
        emoji_name = str(payload.emoji.name)
        if emoji_name not in EMOJIS_VALID:
            return False
        
        user = self.bot.get_user(int(payload.user_id))
        channel = self.bot.get_channel(int(payload.channel_id))
        message = await channel.fetch_message(int(payload.message_id))
        if (message.author.id != self.bot.user.id):
            return False
        
        if (not(len(message.embeds))):
            return False
        
        embed = message.embeds[0]
        title = str(embed.title)
        if (not(title.startswith("Looking for a"))):
            return False
        footer = embed.footer.text
        if (footer.startswith("Game closed")):
            return False
        
        # Recover target role and host
        fields = embed.fields
        host = ""
        target = ""
        for field in fields:
            if (field.name == "Host"):
                host = field.value
            if (field.name == "Target"):
                target = field.value
        if (not(len(message.reactions)) # Game already closed, reactions cleaned
            or not(len(host))): # Should not happen...
            return False 
        
        # Recover players (and users to notify)
        players = []
        users_to_notify = []
        for reaction in message.reactions:
            reaction_users = {reaction_user async for reaction_user in reaction.users()}
            if ((self.bot.user not in reaction_users) \
                and (str(reaction) in EMOJIS_VALID)):
                return False # Game already closed, reactions cleaned
            reaction_users.remove(self.bot.user)
            if str(reaction) == EMOJI_JOIN:
                players = reaction_users
            if str(reaction) == EMOJI_NOTIFY:
                users_to_notify = reaction_users
                users_to_notify.discard(user)
        guests_mentions = ""
        guests_full = ""
        for player in players:
            if (player.mention == host):
                continue
            if (len(guests_mentions)):
                guests_mentions += ", "
            if (len(guests_full)):
                guests_full += ", "
            guests_mentions += player.mention
            guests_full += player.display_name + " (" + player.mention + ")"

        if (emoji_name == EMOJI_JOIN and user.mention != host):
            embed.clear_fields()
            if (len(target)):
                embed.add_field(name="Target", value=target, inline=True)
            embed.add_field(name="Host", value=host, inline=True)
            if (len(guests_full)):
                embed.add_field(name ="Guests", value=guests_full, inline=False)
            try:
                await message.edit(embed=embed)
            except Exception as error:
                print(error)
                
            if (user in players):
                await self.notify_players(channel, host, user, users_to_notify)
                
        if (str(payload.emoji.name) in EMOJIS_CLOSE and user.mention == host):
            emoji_url = payload.emoji.url
            if (not(len(emoji_url))):
                emoji_url = common.get_default_emoji_url(emoji_name)
            embed.set_footer(text="Game closed/full. Sorry!", icon_url=emoji_url)
            try:
                await message.edit(embed=embed)
                await message.clear_reactions()
            except Exception as error:
                print(error)
                
            if (str(payload.emoji.name) == EMOJI_START and \
                message.guild.get_channel_or_thread(message.id) is None):
                await self.create_game_thread(channel, message,
                                              target, host, guests_mentions, embed)
                    
    
    async def notify_players(self, channel, host, new_player, users_to_notify):
        for user_to_notify in users_to_notify:
            message_to_send = "A new player (" + new_player.display_name + ")"
            message_to_send += " has joined your game"
            message_to_send += " in the LFG channel "
            message_to_send += channel.mention + ".\n"
            if (user_to_notify.mention == host):
                message_to_send += "When the game is full,"
                message_to_send += " you can start the thread using "
                message_to_send += EMOJI_START + ", which will ping"
                message_to_send += " all the players. GLHF!"
            else:
                message_to_send += "When the game thread starts,"
                message_to_send += " you will be pinged there. GLHF!"
            try:
                await user_to_notify.send(message_to_send)
            except Exception as e:
                print(e)
                print("Failed to DM " + user_to_notify.display_name)

    async def create_game_thread(self, channel, message,
                                 target, host, guests, embed):
        # New feature: create thread
        # 3 cases: a) Do nothing if this message already has a thread
        #          b) Create thread in a (forum) channel if available
        #          c) Create thread under this message otherwise
    
        gamesRoles, gamesForums, gamesTags, gamesVisibility = \
        self.get_configured_games(message.guild.id, \
                                  CONFIG_GAMES_ROLES, \
                                  CONFIG_GAMES_FORUMS, \
                                  CONFIG_GAMES_TAGS,
                                  CONFIG_GAMES_VISIBILITY)
        nbGames = len(gamesRoles)
        index = -1
        if (nbGames and len(target) and target in gamesRoles):
            index = gamesRoles.index(target)
        
        thread_channel = channel
        parent_message = message
        thread_in_forum = False
        thread_pings = host
        if (len(guests)):
            thread_pings += ", " + guests
        thread_message = thread_pings + ", "
        thread_message += "your game can start! GLHF!"
        thread_embed = None
        
        # Thread title = embed description without custom emojis
        thread_title = embed.description
        if (thread_title is None or not(len(thread_title))):
            thread_title = embed.title
        thread_title = common.clean_thread_title(thread_title, self.custom_emoji_re)
        thread_visibility = True
        thread_tag = None
        
        keywords = {}
        keywords['name'] = thread_title
        
        forum_id = ""
        if (index >= 0 and nbGames == len(gamesForums)):
            forum_id = gamesForums[index]
        forum = None
        tag_name = ""
        if (index >= 0 and nbGames == len(gamesTags)):
            tag_name = gamesTags[index]
        if (len(forum_id)):
            forum = self.bot.get_channel(int(forum_id))
        if (forum is not None):
            thread_in_forum = True
            thread_channel = forum
            if (len(tag_name)):
                for forum_tag in forum.available_tags:
                    if (forum_tag.name == tag_name):
                        thread_tag = forum_tag
        if (index >= 0 and nbGames == len(gamesVisibility)):
            visibility = gamesVisibility[index]
            if (len(visibility) and int(visibility) == 0):
                thread_visibility = False
        
        thread_has_parent = not(thread_in_forum) and thread_visibility
        if (not(thread_has_parent)):
            thread_embed = embed.copy()
            thread_embed.remove_footer()
        if (thread_in_forum):
            if (thread_tag is not None):
                keywords['applied_tags'] = [thread_tag]
            keywords['content'] = thread_message
            keywords['embed'] = thread_embed
        if(thread_has_parent):
            keywords['message'] = parent_message
        if (not(thread_visibility)):
            keywords['type'] = discord.ChannelType.private_thread
        
        try:
            thread = await thread_channel.create_thread(**keywords)
            if (thread_in_forum):
                thread, _ = thread
            if (thread is not None):
                if (not(thread_in_forum)):
                    await thread.send(content=thread_message, embed=thread_embed)
                embed.url = thread.jump_url
                await message.edit(embed=embed)
        except Exception as e:
            print(e)
    
async def setup(bot):
    config = configparser.ConfigParser()
    config.read('config/games.ini')
    await bot.add_cog(matchmaking(bot, config))