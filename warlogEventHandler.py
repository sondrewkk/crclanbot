import asyncio
import json
from pydispatch import Dispatcher
from models import Warlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
from crApi import ClashRoyaleApi
from dateutil.parser import *
from warlogSchedule import logBattles
from math import floor
from environment import Environment
class WarlogEmitter(Dispatcher):
  _events_ = ['on_start']


class WarlogEventHandler():

  def __init__(self, bot):
    self.bot = bot
    self.loop = asyncio.get_event_loop()
    self.warlogScheduler = AsyncIOScheduler()
    self.warlogScheduler.add_job(self.log, "interval", minutes = 5, next_run_time = datetime.now())
    self.warlogScheduler.start()
    self.api = ClashRoyaleApi()
    self.env = Environment()
    self.isDevelopment = (self.env.PYTHON_ENV == "development")

  async def onStartLog(self, channelId, clanTag):
    warlog = Warlog.objects(clanTag=clanTag)
    channel = self.bot.get_channel(channelId)

    if channel is None:
      print(f"Something wrong happend when fetching the channel: {channelId}")
      return
    
    if len(warlog) != 0:
      await channel.send(f"The clan {clanTag} has already started warlogging.")
    else:
      newWarlog = Warlog(clanTag = clanTag, interval = 15 * 60, channelId = channelId)
      newWarlog.save()

      await channel.send("You have succsessfullt started logging your clan war battles.")
 
  async def log(self):
    warlogs = Warlog.objects.all()

    for warlog in warlogs:
      now = datetime.now(timezone.utc)
      deltaTime = int(now.timestamp() - warlog.previousRun)
      interval = warlog.interval

      print(f"DeltaTime={deltaTime} interval={interval}")

      if deltaTime >= interval:
        channel = self.bot.get_channel(warlog.channelId)
        latestClanWarlog = self.api.getRiverracelog(warlog.clanTag)[0]
        warCreated = parse(latestClanWarlog["createdDate"])

        print(f"war created={warCreated} now={now}")

        if self.isDevelopment:
          interval = int((now - warCreated).total_seconds())
          print(f"interval={interval}")

        await logBattles(channel, warlog.clanTag, warCreated, interval)
        
        warlog.previousRun = int(now.timestamp())
        warlog.save()
    
    print("Logging finished")
