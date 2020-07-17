import asyncio
from pydispatch import Dispatcher
from models import WarlogModel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
class WarlogEmitter(Dispatcher):
  _events_ = ['on_start']


class WarlogEventHandler():

  def __init__(self, bot):
    self.bot = bot
    self.loop = asyncio.get_event_loop()
    self.warlogScheduler = AsyncIOScheduler()
    self.warlogScheduler.add_job(self.log, "interval", minutes = 1, next_run_time = datetime.now())
    self.warlogScheduler.start()

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
 
  async def log(self):
    print("Log function")

# async function log() {
#   const clans = await Clan.find({});
  
#   clans.filter(clan => {
#     const delta = moment().subtract(clan.previousRun);
#     return delta.valueOf() >= (clan.interval);
#   })
#   .map(async clan => {
#     try {
#       console.log(`${moment().format('hh:mm:ss')}: Running logging for ${clan.tag}`);

#       // Default interval
#       let interval = clan.interval;

#       // The channel to send log to
#       const channel = await client.channels.fetch(clan.channelId);
      
#       // Need to have a bigger interval if the log has never been run before
#       if(clan.previousRun === 0) {
#         const warlog = await clanApi.warlog(clan.tag);
#         const now = moment();
#         const warCreated = moment(warlog[0].createdDate);
#         const collectionEnding = moment(warCreated).add(24, 'hours');
#         const warEnding = moment(warCreated).add(48, 'hours');
#         const isWarday = now.isBetween(collectionEnding, warEnding);
  
#         if(isWarday) {
#           interval = now.subtract(collectionEnding).valueOf()
#         }
#       }
  
#       logBattles(channel, clan.tag, interval);

#       // Set previoustime to now and save
#       clan.previousRun = moment().valueOf();
#       clan.save();
#     } catch(err) {console.error(err)};
    
#   });

#   setTimeout(log, logInterval);
# }

# function startWarlogScheduler(discordClient){
#   client = discordClient;

#   // Start warlog scheduler
#   log();
# }