from discord.ext import commands
from warlogEventHandler import WarlogEventHandler, WarlogEmitter

class Warlog(commands.Cog, name="Warlog Commands"):

  def __init__(self, bot):
    self.bot = bot
    
    self.warlogEventHandler = WarlogEventHandler(self.bot)  
    self.warlogEmitter = WarlogEmitter()
    self.warlogEmitter.bind_async(self.warlogEventHandler.startLogEventLoop, on_start = self.warlogEventHandler.onStartLog)

  @commands.group()
  async def warlog(self, ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid warlog command passed...')

  @warlog.command()
  async def start(self, ctx, clanTag: str, interval: int): 
    print(f"Channel ID = {ctx.message.channel.id}")
    self.warlogEmitter.emit("on_start", channelId = ctx.message.channel.id, clanTag = clanTag, interval = interval)
  
def setup(bot):
  bot.add_cog(Warlog(bot))


# module.exports = {
# 	name: 'warlog',
# 	description: 'Start or stop warlog for a clan.',
# 	aliases: ['w'],
# 	usage: '[start/stop] [clanTag] [interval (minutes)]',
#   cooldown: 5,
#   guildOnly: true,
#   admin: true,
#   args: true,
# 	async execute(message, args) {

#     const action = args[0];
#     const tag = args[1];
#     const channelId = message.channel.id;
#     let interval = args[2];

#     if(args[2] >= 1) {
#       interval = args[2] * 60 * 1000;
#     }

#     if(action === 'start') {
#       warlogEventHandler.emit('add', tag, interval, channelId);
#     }
#   }
# }