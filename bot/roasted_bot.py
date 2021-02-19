#!/usr/bin/env python3

'''
discord.py
DISCORD_TOKEN environment variable is required to run this program

This is a discord bot for the roasted server. It uses the discord library and integrates the snow_report.py script in order for users to gather information about ski resorts through commands.
'''

# ------------------------------------------------------------imports------------------------------------------------------------

import boto3
import csv
import discord
import datetime
from discord.ext.commands import Bot
from dotenv import load_dotenv
import logging
from multiprocessing import Process
import os
import sys
from timeloop import Timeloop

# Sets up where the files will be
ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)
current_dir = os.getcwd()

# This sets up the sys.path to tell the system where to look for packages. It adds the current working directory (snow_reportApp) to the highest level to sys.path
sys.path.append(current_dir)

# Then it opens the module from the snowApp directory
# Pylint is throwing an Unable to import 'snowApp' error because it does not know where to look for modules. Pylint does not execute the code so it does not recognize sys.path.append
# Running the code still works despite the error that pylint is throwing
from snowapp import snow_report# pylint: disable=import-error

os.chdir(D_NAME)

DESCRIPTION = "This is a discord bot for the roasted server."

# ------------------------------------------------------------logger------------------------------------------------------------

# Sets up the logging that writes the logs to a file called discord.log instead of outputting it to the console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)

logger.debug(f'Adding to PATH... {current_dir}')
logger.debug(f'ABS_PATH: {ABS_PATH}')
logger.debug(f'D_NAME: {D_NAME}')
logger.debug(f'Current Directory: {current_dir}')

# ------------------------------------------------------------env variables------------------------------------------------------------


# Grabs discord token from .env
load_dotenv(".env")
logger.debug(f'Successfully retrieved DISCORD_TOKEN, AWS_ACCESS_KEY, AWS_SECRET_KEY')
TOKEN = os.getenv('DISCORD_TOKEN')
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')

# ------------------------------------------------------------discord------------------------------------------------------------

# Define intents. Intents use flags to determine what part of discord.py must be run
logger.debug(f'Setting up discord bot intents...')
intents = discord.Intents.default()
intents.typing = True
intents.presences = False
intents.members = True
intents.guilds = True
intents.reactions = True
intents.guild_messages = True

help_command = discord.ext.commands.DefaultHelpCommand(
    no_category = 'Commands'
)

# Create a bot instance - bot instances are technically Client instances, this serves as the connection from Discord to discord.py
bot = Bot(command_prefix='!', description=DESCRIPTION, intents=intents, help_command=help_command)

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

    logger.debug(f'async def on_ready: Bot username: {bot.user.name} logged in successfully')
    logger.debug(f'async def on_ready: Bot user ID: {bot.user.id}')

# This bot event monitors all messages incoming from all channels
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    logger.debug(f'async def on_message: Detected message sent by {message.author}: Message Content: "{message.content}"')

    # On message, if the message author is the same as the bot, do nothing, do not want the bot replying to it's own messages
    if message.author == bot.user:
        pass

    # On message, if the message content contains Hello, reply with Hello World to the same channel. Logger sends the action to the log
    elif message.content == "Hello":
        await message.channel.send("Hello World!")
        logger.debug(f'async def on_message: Message Content "Hello"')
        logger.debug(f'async def on_message: Replied to user {message.author} with message "Hello World"')


    # On message, if the message content contains Hello, reply with Hello World to the same channel. Logger sends the action to the log
    elif message.content == "Bye":
        await message.channel.send("See you!")
        logger.debug(f'async def on_message: Message Content "Bye"')
        logger.debug(f'async def on_message: Replied to user {message.author} with message "Bye"')



# This addresses the !accept command. This checks for the !accept command in the guild server, if it is from a guild channel, it notifies the messenger that this is a command reserved for DM channels
# It then checks to see if the user is a member, if they are not a member, it then adds them to the 
# If the !accept command was issued in a DM, then the bot will reply and say it is adding to the member role
# If they are already a member, nothing is done and it says that member is already assigned the role in the log.
# The code block then enters the message async function to actually assign the role
@bot.command(pass_context=True, name='accept', help='Accept command for new users after reading the rules')
async def assign_role(ctx):
    logger.debug(f'async def assign_role: Command ("!accept"): Author ({ctx.author}): Channel: ({ctx.channel})')

    if ctx.guild is None:
        guild_id = bot.get_guild(int(748917163313725704))
        role = guild_id.get_role(int(800907308887572521))
        member = guild_id.get_member(ctx.author.id)

        if role not in member.roles:

            await ctx.send('async def assign_role: Adding to "Member" role...')
            await member.add_roles(role)
            logger.debug(f'async def assign_role: Adding {ctx.author} to {role} role in {guild_id} guild')
            logger.debug(f'async def assign_role: Sending message \'Welcome to "roasted\' server!"')
            await ctx.channel.send('Welcome to the \'roasted\' server!')

        else:
            logger.debug(f'async def assign_role: Member {ctx.author} is already assigned role')
            
    else:
        logger.debug(f'async def assign_role: Message was sent from guild channel {ctx.channel}... sending message to let command author know that this command is "DM only"')
        await ctx.send('Private command only - for DM use')
            

# !server command displays the below information
@bot.command(name='server', help='Fetches server information')
async def fetch_server_info(ctx):
    guild = ctx.guild
    logger.debug(f'async def fetch_server_info: Command ("!server"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    if role in member.roles:   

        logger.debug(f'async def fetch_server_info: {ctx.author} role authorization successful') 
        logger.debug(f'async def fetch_server_info: Sending server information...')
        await ctx.send(f'Server Name: {guild.name}')
        await ctx.send(f'Server Size: {len(guild.members)}')
        await ctx.send(f'Administrator Name: {guild.owner.display_name}')

    else:
        logger.debug(f'async def fetch_server_info: Sending message: Command author is not in "Member" roles. Invalid command, please !accept the rules.')
        await ctx.send('Invalid command, please !accept the rules.')
    

# !canadasnow command checks the ski resorts in Canada for snow in the next 4 days
@bot.command(name='canadasnow', help='Checks for snow in the forecast in Canadian ski resorts')
async def canada_snow_report(ctx):
    logger.debug(f'async def canada_snow_report: Command ("!canadasnow"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    if role in member.roles:    
        
        logger.debug(f'async def canada_snow_report: {ctx.author} role authorization successful')
        logger.debug(f'async def canada_snow_report: Checking snow reports for Canadian resorts... sending to {ctx.author} DM')
        await ctx.send(f'Checking snow reports for Canadian resorts.... please note that 0mm total precipitation does not mean there is no snow, it just means that the snowfall is not significant.')
        await ctx.send(f'Please check your DM')

        dmchannel = await ctx.author.create_dm()

        for resort_key in snow_report.CANADA_RESORTS:
            logger.debug(f'async def canada_snow_report: Sending data for resort {resort_key}')
            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            # resort_temp = resort_object.get_temperature_96hr()
            resort_precipitation_type = resort_object.get_precipitation_type_96hr()
            resort_precipitation = resort_object.get_precipitation_96hr()

            total_precipitation = 0
            for preciptation_value in resort_precipitation.values():
                total_precipitation = int(preciptation_value) + int(total_precipitation)

            if 'snow' in resort_precipitation_type.values():
                await dmchannel.send(f'{resort_object.name} is expecting snow in the next 4 days ({total_precipitation} mm)')
            else:
                await dmchannel.send(f'{resort_object.name} is not expecting snow in the next 4 days')

        logger.debug(f'async def canada_snow_report: Completed command loop')
        await dmchannel.send(f'Complete')

    else:
        logger.debug(f'async def canada_snow_report: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !USAsnow command checks for the snow in the forecast in American resorts for the next 4 days
@bot.command(name='USAsnow', help='Checks for snow in the forecast in American ski resorts')
async def USA_snow_report(ctx):
    logger.debug(f'async def USA_snow_report: Command ("!USAsnow"): Author ({ctx.author}): Channel: ({ctx.channel})')


    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:

        logger.debug(f'async def USA_snow_report: {ctx.author} role authorization successful')
        logger.debug(f'async def USA_snow_report: Checking snow reports for USA resorts... sending to {ctx.author} DM')
        await ctx.send(f'Checking snow reports for American resorts.... please note that 0mm total precipitation does not mean there is no snow, it just means that the snowfall is not significant.')
        await ctx.send(f'Please check your DM')
        
        dmchannel = await ctx.author.create_dm()

        for resort_key in snow_report.USA_RESORTS:
            logger.debug(f'async def USA_snow_report: Sending data for resort {resort_key}')
            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            # resort_temp = resort_object.get_temperature_96hr()
            resort_precipitation_type = resort_object.get_precipitation_type_96hr()
            resort_precipitation = resort_object.get_precipitation_96hr()

            total_precipitation = 0
            for preciptation_value in resort_precipitation.values():
                total_precipitation = int(preciptation_value) + int(total_precipitation)

            if 'snow' in resort_precipitation_type.values():
                await dmchannel.send(f'{resort_object.name} is expecting snow in the next 4 days ({total_precipitation} mm)')
            else:
                await dmchannel.send(f'{resort_object.name} is not expecting snow in the next 4 days')

        logger.debug(f'async def USA_snow_report: Completed command loop')
        await dmchannel.send(f'Complete')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !resorts command lists the resorts that the user can request with the snow report module within discord
@bot.command(name='resorts', help='Lists the resorts that the user can request snow report forecasts')
async def list_resorts(ctx):
    logger.debug(f'async def list_resorts: Command ("!resorts"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:

        logger.debug(f'async def list_resorts: {ctx.author} role authorization successful')
        logger.debug(f'async def list_resorts: Checking Resort: Resort Key pairs... sending to {ctx.author} DM')
        await ctx.send(f'Sending list of searchable resorts to your DM...')

        dmchannel = await ctx.author.create_dm()

        resort_name_key_dict = {snow_report.RESORT_NAMES[i]: snow_report.RESORT_KEYS[i] for i in range(len(snow_report.RESORT_NAMES))}

        await dmchannel.send(f'To check for snow, put a ! at the beginning of the searchable keyword and snow at the end. For example, to search for 4 day forecast of whistler, type !checksnow <insert key here>')
        await dmchannel.send(f'Please wait a few seconds for me to work....')
        logger.debug(f'async def list_resorts: Sending resorts key value pair to {ctx.author} DM')

        for resort in resort_name_key_dict:
            logger.debug(f'async def canada_snow_report: Sending data for resort {resort}')
            await dmchannel.send(f'<Resort Name>: {resort} | <keyword>: {resort_name_key_dict[resort]}')
        
        logger.debug(f'async def list_resorts: Completed command loop')
        await dmchannel.send(f'Complete')
        

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def list_resorts: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !checksnow command checks for snow in the forecast for the resort that is passed as an argument
@bot.command(name='checksnow', help='Checks for snow in the forecast for the resort passed as an argument')
async def check_4day_snow(ctx, resort_key):
    logger.debug(f'async check_4day_snow: Command ("!checksnow {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def check_4day_snow: {ctx.author} role authorization successful')

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_4day_snow: Checking if snow is in the forecast for requested resort')
            await ctx.send(f'Checking forecast... please check your DM')
            await dmchannel.send(f'Checking for snow for resort key {resort_key}, please wait a few seconds for me to work....')

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            # resort_temp = resort_object.get_temperature_96hr()
            resort_precipitation_type = resort_object.get_precipitation_type_96hr()
            resort_precipitation = resort_object.get_precipitation_96hr()

            total_precipitation = 0
            for preciptation_value in resort_precipitation.values():
                total_precipitation = int(preciptation_value) + int(total_precipitation)

            logger.debug(f'async def check_4day_snow: Sending requested information')
            if 'snow' in resort_precipitation_type.values():
                await dmchannel.send(f'{resort_object.name} is expecting snow in the next 4 days ({total_precipitation} mm)')
            else:
                await dmchannel.send(f'{resort_object.name} is not expecting snow in the next 4 days')

        else: 
            await ctx.send(f'Checking forecast... please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again')
            logger.debug(f'async def check_4day_snow: Error, cannot find {resort_key}')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_4day_snow: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# Checks the current temperature of the requested resort
@bot.command(name='checktemp', help='Checks for temperature for the resort passed as an argument')
async def check_temp_now(ctx, resort_key):
    logger.debug(f'async def check_temp_now: Command ("!checktemp {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def check_temp_now: {ctx.author} role authorization successful')  

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_temp_now: Sending requested information')
            await ctx.send(f'Checking temperature... please check your DM')

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_now()
            resort_temp = resort_object.now_temperature

            await dmchannel.send(f'The current temperature of {resort_object.name} is {resort_temp} degrees C')

        else: 
            logger.debug(f'async def check_temp_now: Error, cannot find {resort_key}')
            await ctx.send(f'Checking temperature... please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again.')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_temp_now: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !checkfeelslike command checks feels like temperature for the resort that is passed as an argument
@bot.command(name='checkfeelslike', help='Checks for feels like temperature for the resort passed as an argument')
async def check_feelslike_now(ctx, resort_key):
    logger.debug(f'async def feelslike_now: Command ("!checkfeelslike {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def feelslike_now: {ctx.author} role authorization successful') 

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_feelslike_now: Sending requested information')
            await ctx.send(f'Checking "feels like" temperature... please check your DM')

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_now()
            resort_feelslike = resort_object.now_feelslike

            await dmchannel.send(f'It currently feels like {resort_feelslike} degrees C at {resort_object.name}')

        else: 
            logger.debug(f'async def feelslike_now: Error, cannot find {resort_key}')
            await ctx.send(f'Checking "feels like" temperature... please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again.')


# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_feelslike_now: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !checktomorrowtemp checks the temperature for tomorrow for the requested resort
@bot.command(name='checktomorrowtemp', help='Checks the temperature tomorrow for the requested resort')
async def check_temp_tomorrow(ctx, resort_key):
    logger.debug(f'async def check_temp_tomorrow: Command ("!checktomorrowtemp {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def check_temp_tomorrow: {ctx.author} role authorization successful') 

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_temp_tomorrow: Sending requested information')
            

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            resort_temp_tomorrow = resort_object.get_tomorrow_temp()

            await ctx.send(f'Checking the temperature for tomorrow at {resort_object.name}... please check your DM')
            await dmchannel.send(f'<{resort_object.name}> Temperature: {resort_temp_tomorrow} degrees C')

        else: 
            logger.debug(f'async def check_temp_tomorrow: Error, cannot find {resort_key}')
            await ctx.send(f'Checking "feels like" temperature... please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again.')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_temp_tomorrow: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')


# !checktomorrowfeelslike checks the temperature for tomorrow for the requested resort
@bot.command(name='checktomorrowfeelslike', help='Checks the feels like temperature tomorrow for the requested resort')
async def check_feelslike_tomorrow(ctx, resort_key):
    logger.debug(f'async def check_feelslike_tomorrow: Command ("!checktomorrowfeelslike {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def check_feelslike_tomorrow: {ctx.author} role authorization successful') 

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_feelslike_tomorrow: Sending requested information')

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            resort_feelslike_tomorrow = resort_object.get_tomorrow_feelslike()

            await ctx.send(f'Checking the feels like temperature for tomorrow at {resort_object.name}... please check your DM')
            await dmchannel.send(f'<{resort_object.name}> Feels like: {resort_feelslike_tomorrow} degrees C')

        else: 
            logger.debug(f'async def check_feelslike_tomorrow: Error, cannot find {resort_key}')
            await ctx.send(f'Checking "feels like" temperature... please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again.')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_feelslike_tomorrow: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !checktomorrowfeelslike checks the temperature for tomorrow for the requested resort
@bot.command(name='checktomorrowprecipitation', help='Checks the total amount of precipitation tomorrow for the requested resort')
async def check_precipitation_tomorrow(ctx, resort_key):
    logger.debug(f'async def check_precipitation_tomorrow: Command ("!checktomorrowprecipitation {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def check_precipitation_tomorrow: {ctx.author} role authorization successful') 

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_precipitation_tomorrow: Sending requested information')

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            resort_precipitation_tomorrow = resort_object.get_tomorrow_precipitation()
            resort_precipitation_type_tomorrow = resort_object.get_tomorrow_precipitation_type()

            await ctx.send(f'Checking the precipitation for tomorrow at {resort_object.name}... please check your DM')
            await dmchannel.send(f'<{resort_object.name}> Total precipitation tomorrow: {resort_precipitation_tomorrow} mm')
            await dmchannel.send(f'<{resort_object.name}> Precipitation types: {resort_precipitation_type_tomorrow}')

        else: 
            logger.debug(f'async def check_precipitation_tomorrow: Error, cannot find {resort_key}')
            await ctx.send(f'Checking precipitation.. please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again.')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_precipitation_tomorrow: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# !checktomorrow checks the weather for the requested resort
@bot.command(name='checktomorrow', help='Checks the weather tomorrow for the requested resort')
async def check_tomorrow(ctx, resort_key):
    logger.debug(f'async def check_tomorrow: Command ("!checktomorrow {resort_key}"): Author ({ctx.author}): Channel: ({ctx.channel})')

    guild_id = bot.get_guild(int(748917163313725704))
    role = guild_id.get_role(int(800907308887572521))
    member = guild_id.get_member(ctx.author.id)

    dmchannel = await ctx.author.create_dm()

# Checks if the user is a member, if they are, it executes it.
    if role in member.roles:
        logger.debug(f'async def check_tomorrow: {ctx.author} role authorization successful') 

        if resort_key in snow_report.RESORT_KEYS:
            logger.debug(f'async def check_tomorrow: Sending requested information')

            resort_object = snow_report.Resort(resort_key)
            resort_object.request_96hr()
            resort_temp_tomorrow = resort_object.get_tomorrow_temp()
            resort_feelslike_tomorrow = resort_object.get_tomorrow_feelslike()
            resort_precipitation_tomorrow = resort_object.get_tomorrow_precipitation()
            resort_precipitation_type_tomorrow = resort_object.get_tomorrow_precipitation_type()

            await ctx.send(f'Checking the weather for tomorrow at {resort_object.name}... please check your DM')
            await dmchannel.send(f'<{resort_object.name}> Temperature: {resort_temp_tomorrow} degrees C')           
            await dmchannel.send(f'<{resort_object.name}> Feels like: {resort_feelslike_tomorrow} degrees C')         
            await dmchannel.send(f'<{resort_object.name}> Total precipitation tomorrow: {resort_precipitation_tomorrow} mm')
            await dmchannel.send(f'<{resort_object.name}> Precipitation types: {resort_precipitation_type_tomorrow}')

        else: 
            logger.debug(f'async def check_tomorrow: Error, cannot find {resort_key}')
            await ctx.send(f'Checking weather.. please check your DM')
            await dmchannel.send(f'Error, I cannot find the key "{resort_key}" in my database, please check the key and try again.')

# Checks if the user is a member, if not, it asks the users to !accept the rules
    else:
        logger.debug(f'async def check_tomorrow: Author {ctx.author} not part of Member role.')
        await ctx.send('Invalid command, please !accept the rules.')

# Bot even tthat sends a DM to the new member when they join the server
@bot.event
async def on_member_join(member): 
    logger.debug(f'async def on_member_join')
    logger.debug(f'{member.name} has joined the server...')
    logger.debug(f'{member.name} ID: {member.id}')    
    logger.debug(f'Sending DM to {member.name}')
    
    welcomeMessage = "Welcome to this server. Please reply with read the rules below and reply with '!accept' to join the server."
    await member.send(content=welcomeMessage)

#TODO: Create functions to check tomorrow's weather, precipitation, feels like... etc. 

# ------------------------------------------------------------AWS S3------------------------------------------------------------

# Set up AWS S3 Client with central Canada region
# S3 allows us to store files in the cloud
# This function runs the AWS S3 client
s3 = boto3.client('s3', region_name='ca-central-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
bucket_name = 'roasteddiscordbot-log-bucket'
location = {'LocationConstraint': 'ca-central-1'}

def run_s3():
    logger.debug(f'Accessing AWS S3 service')
    print('------')
    print('Accessing AWS S3')

    try:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        logger.debug(f'Created s3 bucket')
    except:
        logger.debug(f's3 bucket exists')
        print('Successfully logged into AWS S3 bucket')
            
# ------------------------------------------------------------Timeloop------------------------------------------------------------

# This function periodically sends logs to AWS (every 300 seconds)
tl = Timeloop()
@tl.job(interval=datetime.timedelta(seconds=300))
def send_log_60s():

    # Creating the string for the log file name, this is unique to the time
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dt_string_f = now.strftime("%d/%m/%Y %H:%M:%S").replace('/','-').replace(' ', '-').replace(':','.')
    log_name = dt_string_f + '_' + 'discord.log'
    
    logger.debug(f'-----------Sending log {log_name} to AWS S3-----------')
    print(f'-----------Sending log {log_name} to AWS S3-----------')
    s3.upload_file('discord.log', bucket_name, log_name)

    os.chdir(D_NAME)

    # Adds the name of the uploaded discord log to a local csv file and the corresponding date and time
    with open("s3_logs.csv", "a+", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([dt_string, log_name])
    

# This function runs the timeloop necessary to periodically load logs onto AWS S3
def timeloop():
    logger.debug(f'Starting up timeloop to send logs to AWS S3')
    tl.start(block=True)
    print(f'Starting up timeloop to periodically send logs to AWS S3 \n')

 #  This function starts the discord client
def run_bot():
    logger.debug(f'Starting discord bot client')
    bot.run(TOKEN)

# Main function
if __name__ == "__main__":
    p1 = Process(target=run_bot)
    p2 = Process(target=run_s3)
    p3 = Process(target=timeloop)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

