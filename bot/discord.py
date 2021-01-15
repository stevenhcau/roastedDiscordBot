#!/usr/bin/env python3

'''
discord.py
DISCORD_TOKEN environment variable is required to run this program

This is a discord bot for the roasted server.
'''

import discord
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

