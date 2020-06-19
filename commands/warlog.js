const { warlogEventHandler } = require('../warlogEventHandler.js')

module.exports = {
	name: 'warlog',
	description: 'Start or stop warlog for a clan.',
	aliases: ['w'],
	usage: '[start/stop] [clanTag] [interval (minutes)]',
  cooldown: 5,
  guildOnly: true,
  args: true,
	async execute(message, args) {

    const action = args[0];
    const tag = args[1];
    const channelId = message.channel.id;
    let interval = args[2];

    if(args[2] >= 1) {
      interval = args[2] * 60 * 1000;
    }

    if(action === 'start') {
      warlogEventHandler.emit('add', tag, interval, channelId);
    }
  }
}
