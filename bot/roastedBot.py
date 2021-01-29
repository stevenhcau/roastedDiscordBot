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
import sys

DESCRIPTION = "This is a discord bot for the roasted server."

# Sets up where the files will be
ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)
current_dir = os.getcwd()

# This sets up the sys.path to tell the system where to look for packages. It adds the current working directory (snowReportApp) to the highest level to sys.path
sys.path.append(current_dir)

# Then it opens the module from the snowApp directory
# Pylint is throwing an Unable to import 'snowApp' error because it does not know where to look for modules. Pylint does not execute the code so it does not recognize sys.path.append
# Running the code still works despite the error that pylint is throwing
from snowApp import snowReport # pylint: disable=import-error

if current_dir != D_NAME:
    os.chdir(D_NAME)
else:
    pass

# Sets up the logging that writes the logs to a file called discord.log instead of outputting it to the console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)

logger.debug(f'Adding to PATH... {current_dir}')
logger.debug(f'ABS_PATH: {ABS_PATH}')
logger.debug(f'D_NAME: {D_NAME}')
logger.debug(f'Current Directory: {current_dir} \n')

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

# Bot event logs in the bot into discord. Logger information displays the name and user id of the bot to discord.log
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

    logger.debug(f'Bot username: {bot.user.name}')
    logger.debug(f'Bot user ID: {bot.user.id}\n')

# This awaits the "Hello" message in any chat and then replies with "Hello World!"
# Logger prints the content 
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    logger.debug(f'Detected message: ----- {message.content} -----')
    logger.debug(f'Message author: {message.author}')

    # On message, if the message author is the same as the bot, do nothing, do not want the bot replying to it's own messages
    if message.author == bot.user:
        logger.debug(f'Message author {message.author} is same as bot user {bot.user} \n')
        return    

    # On message, if the message content contains Hello, reply with Hello World to the same channel. Logger sends the action to the log
    if message.content == "Hello":
        await message.channel.send("Hello World!")
        logger.debug(f'Replied to user {message.author} with message "Hello World" \n')

    # On message, if the message content contains Hello, reply with Hello World to the same channel. Logger sends the action to the log
    if message.content == "Bye":
        await message.channel.send("See you!")
        logger.debug(f'Replied to user {message.author} with message "Bye" \n')

    # This checks if the message is a DM and then replies to the author in the same channel
    # isinstance returns True if the object argument is an instance of the classinfo argument - isinstance(object,classinfo)
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        logger.debug(f'Message sent from channel: {message.channel}')
        logger.debug(f'Private channel: {isinstance(message.channel, discord.DMChannel)}')
        logger.debug(f'Message author: {message.author}')
        logger.debug(f'Bot username: {bot.user} \n' )

        # If the message is a DM and the user replies with !accept, th"en we will asign them their role to Member
        # The guild id and role ids are extracted from the Dicord server. This code block works because this bot is only being used on this server
        if message.content == '!accept':
            guild_id = bot.get_guild(int(748917163313725704))
            role = guild_id.get_role(int(800907308887572521))
            member = guild_id.get_member(message.author.id)
            await member.add_roles(role)

            logger.debug(f'Adding {message.author} to {role} role in {guild_id} guild')
            logger.debug(f'Sending message "Welcome to "roasted" server!" \n')
            await message.channel.send('Welcome to the "roasted" server!')

        # Else, any other message is ignored and the bot requests that the user reads the rules and replies with !accept
        else:
            logger.debug(f'Sending message "Please read the rules and reply with "!accept" \n')
            await message.channel.send('Please read the rules and reply with "!accept"')

    # This checks if the message !accept happens and is not sent by the bot
    if message.content == '!accept' and message.author != bot.user:
        logger.debug(f'Message sent from channel: {message.channel}')
        logger.debug(f'Message author: {message.author} \n')

        # This checks if the message content is !accept and is not a DM, so it happens in the main server and sends a message notifying the user that the !accept command is reserved only for DMs
        if message.content == '!accept' and not isinstance(message.channel, discord.DMChannel):
            await message.channel.send('Private command only - for DM use')

# This addresses the !accept command. This checks for the !accept command in the guild server, if it is called, nothing is actually done and then passes the action to the message async function to carry out the code in that block
# If the !accept command was issued in a DM, then the bot will reply and say it is adding to the member role.
# The code block then enters the message async function to actually assign the role
@bot.command(pass_context=True, name='accept')
async def assign_role(ctx):
    logger.debug(f'Command sent from channel {ctx.channel}')
    logger.debug(f'Command author: {ctx.author}')
    logger.debug(f'Command content: -----  {ctx.message.content} -----  \n')

    if not ctx.guild is not None:
        logger.debug(f'ctx.guild {ctx.guild}')
        logger.debug(f'Sending message..."Adding to "Member" role" \n')
        await ctx.send('Adding to "Member" role...')

# !server command displays the below information
@bot.command(name='server', help='fetches server information')
async def fetchServerInfo(ctx):
	guild = ctx.guild
	
	await ctx.send(f'Server Name: {guild.name}')
	await ctx.send(f'Server Size: {len(guild.members)}')
	await ctx.send(f'Administrator Name: {guild.owner.display_name}')

@bot.command(name='canadasnow', help='checks for snow in the forecast in Canadian ski resorts')
async def canada_snowReport(ctx):
    logger.debug(f'Command sent from channel {ctx.channel}')
    logger.debug(f'Command author: {ctx.author}')
    logger.debug(f'Command content: -----  {ctx.message.content} -----  \n')

    await ctx.send(f'Checking snow reports for Canadian resorts.... please note that 0mm total precipitation does not mean there is no snow, it just means that the snowfall is not significant.')
    await ctx.send(f'...')

    for resort_key in snowReport.CANADA_RESORTS:
        resort_object = snowReport.Resort(resort_key)
        resort_object.request_96hr()
        resort_temp = resort_object.get_temperature_96hr()
        resort_precipitation_type = resort_object.get_precipitation_type_96hr()
        resort_precipitation = resort_object.get_precipitation_96hr()

        total_precipitation = 0
        for preciptation_value in resort_precipitation.values():
            total_precipitation = int(preciptation_value) + int(total_precipitation)

        if 'snow' in resort_precipitation_type.values():
            await ctx.send(f'{resort_object.name} is expecting snow in the next 4 days')
            await ctx.send(f'Total snow expected: {total_precipitation} mm \n')
            await ctx.send(f'...')
        else:
            await ctx.send(f'{resort_object.name} is not expecting snow in the next 4 days')
            await ctx.send(f'...')
        

# Bot event that sends a DM to a user when the join the server
@bot.event
async def on_member_join(member): 
    logger.debug(f'{member.name} has joined the server...')
    logger.debug(f'{member.name} ID: {member.id}')    
    logger.debug(f'Sending DM to {member.name} \n')
    
    welcomeMessage = "Welcome to this server. Please reply with read the rules below and reply with '!accept' to join the server."
    await member.send(content=welcomeMessage)

bot.run(TOKEN)