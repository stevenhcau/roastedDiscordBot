#!/usr/bin/env python3

import boto3
import csv
import logging
import os
import re
import sys

# Sets up where the files will be
ABS_PATH = os.path.abspath(__file__)
D_NAME = os.path.dirname(ABS_PATH)
current_dir = os.getcwd()

if current_dir != D_NAME:
    os.chdir(D_NAME)
else:
    pass

# ------------------------------------------------------------logger------------------------------------------------------------

# Sets up the logging that writes the logs to a file called log_parser.log instead of outputting it to the console
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(filename='log_parser.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)

logger.debug(f'Adding to PATH... {current_dir}')
logger.debug(f'ABS_PATH: {ABS_PATH}')
logger.debug(f'D_NAME: {D_NAME}')
logger.debug(f'Current Directory: {current_dir}')

# ------------------------------------------------------------regex functions------------------------------------------------------------
# argument for variable log_file is a string of the log file

# Returns the total number of messages sent
def message_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def on_message')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def message_count: return value: {number_matches}')
    return number_matches

# Returns the total number of messages sent from a specific user (message.author)
def user_message_count(log_file, message_author):
    regex_author = re.compile(r'[a-zA-Z0-9]{2,32}#\d\d\d\d')
    author_match = regex_author.fullmatch(str(message_author))

    if author_match is True:
        regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def on_message: Detected message sent by ' + re.escape(message_author))
        matches = regex.findall(log_file)
        number_matches = len(matches)
        logger.debug(f'def user_message_count: message_author: {message_author} return value: {number_matches}')
        return number_matches

    else:
        logger.debug(f'Invalid message_author name')
        logger.debug(f'def user_message_count: message_author: {message_author} return value: 0')
        return 0
    

# Returns the total number of times !USAsnow command is passed
def USA_snow_report_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def USA_snow_report: Command \(\"!USAsnow\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def USA_snow_report_count: return value: {number_matches}')
    return number_matches

# Returns the total number of times !canadasnow command is passed
def canada_snow_report_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def USA_snow_report: Command \(\"!canadasnow\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def canada_snow_report_count: return value: {number_matches}')
    return number_matches

# Returns the total number of times !checkfeelslike command is passed
# Resort that is queuried is determined by passing resort_key arg
def feelslike_now_count(log_file, resort_key):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def feelslike_now: Command \(\"!checkfeelslike [a-zA-Z0-9\D]{2,32}\d\d\d\d\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def feelslike_now_count: resort_key: {str(resort_key)}: return value: {number_matches}')
    return number_matches

# Returns the total number of times !checksnow command is passed
# Resort that is queuried is determined by passing resort_key arg
def checksnow_count(log_file, resort_key):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def check_4day_snow: Command \(\"!checksnow [a-zA-Z0-9\D]{2,32}\d\d\d\d\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def checksnow_count: resort_key: {str(resort_key)}: return value: {number_matches}')    
    return number_matches

# Returns the total number of times !checktemp command is passed
# Resort that is queuried is determined by passing resort_key arg
def checktemp_count(log_file, resort_key):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def check_temp_now: Command \(\"!checktemp [a-zA-Z0-9\D]{2,32}\d\d\d\d\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def checktemp_count: resort_key: {str(resort_key)}: return value: {number_matches}')        
    return number_matches

# Returns the total number of times !resort command is passed
def list_resorts_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def list_resorts: Command \(\"!resorts\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def listresorts_count: return value: {number_matches}')   
    return number_matches

# Returns the total number of time !accept command is passed
def assign_role_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def assign_role: Command \(\"!accept\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def assign_role_count: return value: {number_matches}')       
    return number_matches

# Returns the total number of times !server command is passed
def fetch_server_info_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def fetch_server_info: Command \(\"!server\"\):')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def fetch_server_info_count: return value: {number_matches}')         
    return number_matches

# Returns the total number of times "Hello" message is sent
def on_message_Hello_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def on_message: Message Content \"Hello\"')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def on_message_Hello_count: return value: {number_matches}')       
    return number_matches

# Returns the total number of times "Bye" message is sent
def on_message_Bye_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def on_message: Message Content \"Bye\"')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def on_message_Bye_count: return value: {number_matches}')       
    return number_matches

# Returns the total amount of times a query to determine if there is snow for a specific resort over the next 4 days
# Resort that is queuried is determined by passing resort_key arg
def resort_has_snow_count(log_file, resort_key):

    regex_canadasnow = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def canada_snow_report: Sending data for resort ' + re.escape(resort_key))
    regex_checksnow = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def check_4day_snow: Command \(\"!checksnow ' + re.escape(resort_key))
    regex_USAsnow = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def USA_snow_report: Sending data for resort ' + re.escape(resort_key))

    matches_canadasnow = regex_canadasnow.findall(log_file)
    matches_checksnow = regex_checksnow.findall(log_file)
    matches_USAsnow = regex_USAsnow.findall(log_file)

    number_matches_canadasnow = len(matches_canadasnow)
    number_matches_checksnow = len(matches_checksnow)
    number_matches_USAsnow = len(matches_USAsnow)

    number_matches = number_matches_canadasnow + number_matches_checksnow + number_matches_USAsnow
    
    logger.debug(f'def resort_has_snow_count: resort_key: {str(resort_key)}: return value: {number_matches}')   
    return number_matches
   

# Returns the total amount of new members that have joined the server
def on_member_join_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async on_member_join')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def on_member_join_count: return value: {number_matches}')     
    return number_matches

# Returns the total amount of times a message is sent by the bot
def bot_messages_sent_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def on_message: Detected message sent by RoastedBot#1314:')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def bot_messages_sent_count: return value: {number_matches}')     
    return number_matches

# Returns the total amount of times !accept is used without the message.author belonging to the "Member" role:
def accept_fail_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def on_message: Detected message sent by RoastedBot#1314: Message Content: \"Invalid command, please !accept the rules\.\"')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def accept_fail_count: return value: {number_matches}')     
    return number_matches

# Returns the total amount of times !accept is used and works successfully from a DM channel
def accept_success_count(log_file):
    regex = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def assign_role: Command \(\"!accept\"\): Author \([a-zA-Z0-9\D]{2,32}\d\d\d\d\): Channel: \(Direct Message with [a-zA-Z0-9\D]{2,32}\d\d\d\d\)')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def accept_success_count: return value: {number_matches}')     
    return number_matches

# Returns the total amount of times !accept is used not from a DM channel
def accept_public_channel_count(log_file):
    regex_accept_total = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def assign_role: Command \(\"!accept\"\): Author \([a-zA-Z0-9\D]{2,32}\d\d\d\d\)')
    regex_success = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d:DEBUG:__mp_main__: async def assign_role: Command \(\"!accept\"\): Author \([a-zA-Z0-9\D]{2,32}\d\d\d\d\): Channel: \(Direct Message with [a-zA-Z0-9\D]{2,32}\d\d\d\d\)')

    matches_accept_total = regex_accept_total.findall(log_file)
    matches_success = regex_success.findall(log_file)

    number_accept_total = len(matches_accept_total)
    number_matches_success = len(matches_success)
    
    # times !accept is used from a non-DM channel - regex_accept_total - regex_success
    number_matches = number_accept_total - number_matches_success
    logger.debug(f'def accept_public_channel_count: return value: {number_matches}')      
    return number_matches

# Returns the total amount of times that !help is used successfully
def help_command_count(log_file):
    regex = re.compile(r'Type !help command for more info on a command\.')
    matches = regex.findall(log_file)
    number_matches = len(matches)
    logger.debug(f'def help_command_count: return value: {number_matches}')     
    return number_matches

# Returns the number of users that were active (had some activity)
def active_users(log_file):
    regex_user = re.compile(r'[a-zA-Z0-9]{2,32}#\d\d\d\d')
    matches = regex_user.findall(log_file)
    unique_matches = list(set(matches))
    logger.debug(f'def active_users: unique users: {len(unique_matches)}')  
    return unique_matches

# ------------------------------------------------------------logic------------------------------------------------------------

with open('discord.log', 'r', encoding='utf-8') as f:
     log_string = f.read()

print(active_users(log_string))
