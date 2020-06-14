module.exports = {
  name: 'ping',
  description:'Ping!',
  cooldown: 5,
  guildOnly: true,
  args: false,
  // usage: '', dont need usage when command has no arguments
  execute(message) {
    message.channel.send('Pong.')
  }
}