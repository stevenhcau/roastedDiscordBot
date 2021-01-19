#!/usr/bin/env python3

'''
discord.py
DISCORD_TOKEN environment variable is required to run this program

This is a discord bot for the roasted server.
'''

import discord
from discord.ext.commands import Bot
from dotenv import load_dotenv
import logging
import os

DESCRIPTION = "This is a discord bot for the roasted server."

# Sets up where the files will be
ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)
currentDir = os.getcwd()

if currentDir != D_NAME:
    os.chdir(D_NAME)
else:
    pass

# Sets up the logging that writes the logs to a file called discord.log instead of outputting it to the console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)

logger.debug(f'ABS_PATH: {ABS_PATH}')
logger.debug(f'D_NAME: {D_NAME}')
logger.debug(f'Current Directory: {currentDir}')

# Grabs discord token from .env
load_dotenv(".env")
TOKEN = os.getenv('DISCORD_TOKEN')
logger.debug(f'Token: {TOKEN}')

# Define intents. Intents use flags to determine what part of discord.py must be run
intents = discord.Intents.default()
intents.typing = True
intents.presences = False
intents.members = True
intents.guilds = True
intents.reactions = True
intents.guild_messages = True

# Create a bot instance - bot instances are technically Client instances, this serves as the connection from Discord to discord.py
bot = Bot(command_prefix='!', description=DESCRIPTION, intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(
                          type = discord.ActivityType.listening, 
                          name = 'Pretty Savage'))
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

# This awaits the "Hello" message in any chat and then replies with "Hello World!"
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return    
    if message.content == "Hello":
        await message.channel.send("Hello World!")
    if message.content == "Bye":
        await message.channel.send("See you!")

    # This checks if the message is a DM and then replies to the author in the same channel
    # isinstance returns True if the object argument is an instance of the classinfo argument - isinstance(object,classinfo)
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        if message.content == "!yes":
            await message.channel.send('Welcome to the "roasted" server!')
        else:
            await message.channel.send('Please read the rules and reply with "!yes"')

# !server command displays the below information
@bot.command(name='server', help='fetches server information')
async def fetchServerInfo(context):
	guild = context.guild
	
	await context.send(f'Server Name: {guild.name}')
	await context.send(f'Server Size: {len(guild.members)}')
	await context.send(f'Administrator Name: {guild.owner.display_name}')

# Bot event that sends a DM to a user when the join the server
@bot.event
async def on_member_join(member): 
    print(f'{member.name} has joined the server...')
    print(f'{member.name} ID: {member.id}')    
    print(f'Sending DM to {member.name}')

    welcomeMessage = "Welcome to this server. Please reply with read the rules below and reply with '!yes' to join the server."
    await member.send(content=welcomeMessage)

bot.run(TOKEN)