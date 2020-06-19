const EventEmitter = require('events');
const { logBattles } = require('./warlogSchedule.js');
const Clan = require('./schema/clanSchema.js');

const warlogEventHandler = new EventEmitter();
const logInterval = 60000; // One minute
let client = null;

warlogEventHandler.on('uncaughtException', err => {
  console.error(err);
});

warlogEventHandler.on('add', async (tag, interval, channelId) => {
  try {
    const clan = await Clan.findOne({tag: tag});
    const channel = await client.channels.fetch(channelId);
    
    if(clan) {
      channel.send(`The clan ${tag} is already added to the warlog schedule.`);
    } 
    else {
      const newClan = new Clan({tag, interval, channelId});
      await newClan.save();

      channel.send(`You have succsessfullt started logging of war battles.`);  
    }
  } catch(err) { console.error(err) };
});

async function log() {
  const clans = await Clan.find({});
  console.log(`There are ${clans.length} number of clans to log`);
  
  clans.filter(clan => {
    const delta = Date.now() - clan.previousRun;
    return delta >= clan.interval;
  })
  .map(async clan => {
    const channel = await client.channels.fetch(clan.channelId);
    logBattles(channel, clan.tag, clan.interval);
  });

  setTimeout(log, logInterval);
}

function startWarlogScheduler(discordClient){
  client = discordClient;

  // Start warlog scheduler
  log();
}

module.exports = { 
  warlogEventHandler: warlogEventHandler,
  startWarlogScheduler: startWarlogScheduler
};
