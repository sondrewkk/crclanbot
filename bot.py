import sys
import discord
from discord.ext import commands
from environment import Environment
from commandHandler import CommandHandler
from warlogEventHandler import WarlogEventHandler
from mongoengine import connect
import json
this = sys.modules[__name__]
this.running = False

# Get environment variables
env = Environment()


######################################################################################

def main():
  
  #Initialize
  print(f"Starting up discord bot v.{discord.__version__}")
  
  bot = commands.Bot(command_prefix = env.PREFIX, description = "Clash Royale clan bot")

  # Connect to db
  connect(
    db=env.DB_NAME,
    username=env.DB_USER,
    password=env.DB_USER_PASS,
    host=env.DB_HOST,
    port=env.DB_PORT,
    authentication_source=env.DB_NAME)

  @bot.event
  async def on_ready():
    
    if this.running:
      return
    
    this.running = True

    # Create command handler
    commandHandler = CommandHandler(bot, "commands")

  # Run bot
  bot.run(env.DISCORD_TOKEN, bot=True, reconnect=True)

######################################################################################  

if __name__ == "__main__":
    main()
