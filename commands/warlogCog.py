from discord.ext import commands
from warlogEventHandler import WarlogEventHandler, WarlogEmitter

class WarlogCog(commands.Cog, name="Warlog Commands"):

  def __init__(self, bot):
    self.bot = bot
    
    self.warlogEventHandler = WarlogEventHandler(self.bot)  
    self.warlogEmitter = WarlogEmitter()
    self.warlogEmitter.bind_async(self.warlogEventHandler.loop, on_start = self.warlogEventHandler.onStartLog)

  @commands.group()
  async def warlog(self, ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid warlog command passed...')

  @warlog.command()
  async def start(self, ctx, clanTag: str): 
    self.warlogEmitter.emit("on_start", channelId = ctx.message.channel.id, clanTag = clanTag)
  
def setup(bot):
  bot.add_cog(WarlogCog(bot))
