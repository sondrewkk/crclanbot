const EventEmitter = require('events');
const { logBattles } = require('./warlogSchedule.js');

const warlogEventHandler = new EventEmitter();
let clans = [];
const logInterval = 60000; // One minute
let client = null;

warlogEventHandler.on('uncaughtException', err => {
  console.error(err);
});

warlogEventHandler.on('add', (tag, interval, channelId) => {
  const clan = {
    tag: tag,
    interval: interval,
    previousRun: 0,
    channelId: channelId
  };

  clans.push(clan);
});

function log() {
  console.log(`There are ${clans.length} number of clans to log`);
  
  clans.map(clan => {
    const delta = Date.now() - clan.previousRun;

    if(delta >= clan.interval){
      client.channels.fetch(clan.channelId).then(channel => {
        logBattles(channel, clan.tag, clan.interval);
      });
    }
  });
}

function startWarlogScheduler(discordClient){
  
  client = discordClient;

  // Start warlog scheduler
  setInterval(log, logInterval);
}

module.exports = { 
  warlogEventHandler: warlogEventHandler,
  startWarlogScheduler: startWarlogScheduler
};
