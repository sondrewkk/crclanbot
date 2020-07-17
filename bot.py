import sys
import discord
from discord.ext import commands
from environment import Environment
from commandHandler import CommandHandler
from warlogEventHandler import WarlogEventHandler
from mongoengine import connect

this = sys.modules[__name__]
this.running = False

# Get environment variables
env = Environment()


######################################################################################

def main():
  
  #Initialize
  print("Starting up...")
  
  bot = commands.Bot(command_prefix = env.PREFIX, description = "Clash Royale clan bot")

  # Connect to db
  connect(env.DB_NAME)

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
