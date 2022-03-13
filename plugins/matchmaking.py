import discord
from discord.ext import commands
import time
import config
import asyncio
import json
import random
import traceback

class matchmaking(commands.Cog):
	
	def is_allowedRole(ctx):
		'''
			Checks if members has admin permission, or is guild owner
		'''			
		groups = ctx.message.author.roles
		admin = False
		for group in groups:
			if group.permissions.administrator:
				admin = True
		if str(ctx.message.guild.owner_id) == str(ctx.message.author.id):
			admin = True
		if admin:
			return True
				
		return False
	
	@commands.command(pass_context=True, brief="", name='lfgdig')
	async def lfgdigCMD(self, ctx,*desc):
		gameWanted = "**Digital** (<@&746019278892957787>) game"
		
		embed = discord.Embed(description="Playing: "+ctx.message.author.mention)
		text = ctx.message.author.mention+" is looking for a "+str(gameWanted)+" with: " +" ".join(desc)+"\n For discussion about this game, please use a thread."
		
		messageSent = await ctx.send(text,embed=embed)

		await messageSent.add_reaction("👍")
		await messageSent.add_reaction("🔔")
		await messageSent.add_reaction("❌")
		await ctx.message.delete()
		
	@commands.command(pass_context=True, brief="", name='lfgtts')
	async def lfgttsCMD(self, ctx,*desc):
		gameWanted = "**Tabletop** (<@&536618324965195776>) game"
		
		embed = discord.Embed(description="Playing: "+ctx.message.author.mention)
		text = ctx.message.author.mention+" is looking for a "+str(gameWanted)+" with: " +" ".join(desc)+"\n For discussion about this game, please use a thread."
		
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
					await message.edit(message.content,embed=embed)
	
	def __init__(self, bot):
		
		print("Matchmaking plugin started")
		
		self.bot = bot
	
def setup(bot):
	bot.add_cog(matchmaking(bot))