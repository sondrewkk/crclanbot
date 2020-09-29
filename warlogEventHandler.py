import asyncio
import json
from pydispatch import Dispatcher
from models import Warlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, timezone
from crApi import ClashRoyaleApi
from dateutil.parser import *
from warlog import logBattles, logFinishLineReached, logSummary
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
      finishLineReached = warlog.finishLineReached
      channel = self.bot.get_channel(warlog.channelId)

      print(f"now={now} | deltaTime={deltaTime} | interval={interval} | finishLineReached={finishLineReached}")

      latestClanWarlog = self.api.getRiverracelog(warlog.clanTag)[0]
      currentWar = self.api.getCurrentRiverrace(warlog.clanTag)
      clan = currentWar["clan"]
      warCreated = parse(latestClanWarlog["createdDate"])

      if deltaTime >= interval and not finishLineReached:
        # Recalculate interval for development
        if self.isDevelopment:
          interval = int((now - warCreated).total_seconds())
          print(f"Interval changed to: {interval}")

        # Check if clan has reach finish line
        if 'finishTime' in clan:
          finishLineReached = True
          warlog.finishLineReached = finishLineReached
          finishTime = parse(clan["finishTime"])
          warlog.currentRaceFinishTime = finishTime
      
        #await logBattles(channel, warlog.clanTag, warCreated, interval)
        print(f"Logging battles")
        
        #warlog.previousRun = int(now.timestamp())
        warlog.save()

        if finishLineReached:
          standing = 1
          clans = currentWar["clans"]

          for clan in clans:
            if 'finishTime' in clan:
              clanFinish = parse(clan["finishTime"])
              finishedBefore = clanFinish > finishTime

              if finishedBefore:
                standing += 1

          await logFinishLineReached(channel, warCreated, finishTime, standing)

      else:
        riverraceFinished = warCreated + timedelta(days=7)
        isWeekFinished = now >= riverraceFinished

        # DEV
        isWeekFinished = True
        print(f"riverraceFinished={riverraceFinished} | isWeekFinished={isWeekFinished}")

        if isWeekFinished:
          await logSummary(channel, warlog.clanTag)

          warlog.finishLineReached = False
          warlog.currentRaceFinishTime = 0
          warlog.previousRun = int(now.timestamp())
          warlog.save()

    print("Logging finished")
