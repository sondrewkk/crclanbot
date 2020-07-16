import discord
from discord.ext import commands
from environment import Environment
from commandHandler import CommandHandler
from warlogEventHandler import WarlogEventHandler
from mongoengine import connect

# Get environment variables
env = Environment()
TOKEN = env.DISCORD_TOKEN

# Create bot
bot = commands.Bot(command_prefix = env.PREFIX, description = "Clash Royale clan bot")

# Connect to db
connect(env.DB_NAME)

# Create command handler
commandHandler = CommandHandler(bot, "commands")

# Run bot
bot.run(TOKEN, bot=True, reconnect=True)