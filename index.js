const fs = require('fs');
const Discord = require('discord.js');
const { startWarlogScheduler } = require('./warlogEventHandler');
const { prefix, token } = require('./config.json');

const client = new Discord.Client();
const cooldowns = new Discord.Collection();



// Create a commands collection
client.commands = new Discord.Collection();

// Find all javascript files in the commands folder
const commandFiles = fs.readdirSync('./commands').filter(file => file.endsWith('.js'));

// Loop throgh all files found, require them and add them to the commands collection
for (const file of commandFiles) {
  const command = require(`./commands/${file}`)
  client.commands.set(command.name, command);
}

// When the bot has connected to Discord, log a ready message
client.once('ready', () => {
	console.log('Ready! Starting schedulers');
	
	// start warlog scheduler
	startWarlogScheduler(client);
});

// Message event handler
client.on('message', message => {
  if (!message.content.startsWith(prefix) || message.author.bot) return;

	const args = message.content.slice(prefix.length).split(/ +/);
	const commandName = args.shift().toLowerCase();

	const command = client.commands.get(commandName) || client.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName));

	if (!command) return;

	if (command.guildOnly && message.channel.type !== 'text') {
		return message.reply('I can\'t execute that command inside DMs!');
	}

	if (command.args && !args.length) {
		let reply = `You didn't provide any arguments, ${message.author}!`;

		if (command.usage) {
			reply += `\nThe proper usage would be: \`${prefix}${command.name} ${command.usage}\``;
		}

		return message.channel.send(reply);
	}

	if (!cooldowns.has(command.name)) {
		cooldowns.set(command.name, new Discord.Collection());
	}

	const now = Date.now();
	const timestamps = cooldowns.get(command.name);
	const cooldownAmount = (command.cooldown || 3) * 1000;

	if (timestamps.has(message.author.id)) {
		const expirationTime = timestamps.get(message.author.id) + cooldownAmount;

		if (now < expirationTime) {
			const timeLeft = (expirationTime - now) / 1000;
			return message.reply(`please wait ${timeLeft.toFixed(1)} more second(s) before reusing the \`${command.name}\` command.`);
		}
	}

	timestamps.set(message.author.id, now);
	setTimeout(() => timestamps.delete(message.author.id), cooldownAmount);

	try {
		command.execute(message, args);
	} catch (error) {
		console.error(error);
		message.reply('there was an error trying to execute that command!');
	}

});

process.on('unhandledRejection', error => {
	console.error('Unhandled promise rejection:', error);
});

// log bot into discord
client.login(token);
