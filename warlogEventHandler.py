from pydispatch import Dispatcher
# from mongoengine import *
from models import WarlogModel
import asyncio

class WarlogEmitter(Dispatcher):
  _events_ = ['on_start']


class WarlogEventHandler():

  def __init__(self, bot):
    self.bot = bot
    self.startLogEventLoop = asyncio.get_event_loop()
    
    # Register events
    # self.startLogEmitter = WarlogEmitter()
    # self.startLogEmitter.bind_async(self.startLogEvent, on_start = self.onStartLog)

  async def onStartLog(self, channelId, clanTag, interval):
    warlog = WarlogModel.objects(clanTag=clanTag)
    channel = self.bot.get_channel(channelId)

    if channel is None:
      print(f"Something wrong happend when fetching the channel: {channelId}")
      return
    
    if len(warlog) != 0:
      await channel.send(f"The clan {clanTag} has already started warlogging.")
    else:
      newWarlog = WarlogModel(clanTag = clanTag, interval = interval, channelId = channelId)
      newWarlog.save()

      await channel.send("You have succsessfullt started logging your clan war battles.")
 