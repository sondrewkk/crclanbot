const EventEmitter = require('events');
const { logBattles } = require('./warlogSchedule.js');
const Clan = require('./schema/clanSchema.js');
const moment = require('moment');
const clanApi = require('./api/clan.js');

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
  
  clans.filter(clan => {
    const delta = moment().subtract(clan.previousRun);
    return delta.valueOf() >= (clan.interval);
  })
  .map(async clan => {
    try {
      console.log(`${moment().format('hh:mm:ss')}: Running logging for ${clan.tag}`);

      // Default interval
      let interval = clan.interval;

      // The channel to send log to
      const channel = await client.channels.fetch(clan.channelId);
      
      // Need to have a bigger interval if the log has never been run before
      if(clan.previousRun === 0) {
        const warlog = await clanApi.warlog(clan.tag);
        const now = moment();
        const warCreated = moment(warlog[0].createdDate);
        const collectionEnding = moment(warCreated).add(24, 'hours');
        const warEnding = moment(warCreated).add(48, 'hours');
        const isWarday = now.isBetween(collectionEnding, warEnding);
  
        if(isWarday) {
          interval = now.subtract(collectionEnding).valueOf()
        }
      }
  
      logBattles(channel, clan.tag, interval);

      // Set previoustime to now and save
      clan.previousRun = moment().valueOf();
      clan.save();
    } catch(err) {console.error(err)};
    
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
