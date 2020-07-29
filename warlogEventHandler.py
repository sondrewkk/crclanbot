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

  async def onStartLog(self, channelId, clanTag, interval):
    warlog = Warlog.objects(clanTag=clanTag)
    channel = self.bot.get_channel(channelId)

    if channel is None:
      print(f"Something wrong happend when fetching the channel: {channelId}")
      return
    
    if len(warlog) != 0:
      await channel.send(f"The clan {clanTag} has already started warlogging.")
    else:
      newWarlog = Warlog(clanTag = clanTag, interval = interval, channelId = channelId)
      newWarlog.save()

      await channel.send("You have succsessfullt started logging your clan war battles.")
 
  async def log(self):
    warlogs = Warlog.objects.all()

    for warlog in warlogs:
      now = datetime.now(timezone.utc)
      deltaTime = now.timestamp() - warlog.previousRun

      # print(f"time now = {now.timestamp()} delta = {deltaTime} previousRun = {warlog.previousRun}")

      if deltaTime >= warlog.interval:
        interval = warlog.interval
        channel = self.bot.get_channel(warlog.channelId)
        latestClanWarlog = self.api.getWarlog(warlog.clanTag)[0]
        warCreated = parse(latestClanWarlog["createdDate"])

        if warlog.previousRun == 0:
          collectionEnding = warCreated + timedelta(hours = 24)
          warEnding = warCreated + timedelta(hours = 48)
          isWarDay = (collectionEnding < now < warEnding)

          # print(f"War created: {warCreated}")
          # print(f"now:       : {now}")
          # print(f"war ending : {warEnding}")
          # print(f"isWarDay   : {isWarDay}")

          if isWarDay or self.isDevelopment:
            calculatedInterval = now - collectionEnding
            interval = floor(calculatedInterval.total_seconds() / 60) # result in minutes

        #logBattles(channel, warlog.clanTag, interval)
        logBattles(channel, warlog.clanTag, warCreated, interval)
        
        # warlog.previousRun = now.timestamp()
        # warlog.save()
