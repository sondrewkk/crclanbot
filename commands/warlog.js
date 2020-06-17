const { warlogEventHandler } = require('../warlogEventHandler.js')


module.exports = {
	name: 'warlog',
	description: 'Start or stop warlog for a clan.',
	aliases: ['w'],
	usage: '[start/stop] [clanTag] [interval (seconds)]',
  cooldown: 5,
  guildOnly: true,
  args: true,
	async execute(message, args) {

    const action = args[0];
    const tag = args[1];
    const channelId = message.channel.id;
    let interval = 60000;
  

    if(args[2] >= 60) {
      interval = args[2] * 1000;
    }

    if(action === 'start'){
      
      warlogEventHandler.emit('add', tag, interval, channelId);
      message.channel.send(`You have succsessfullt started logging of war battles`);
    }
  }
}
