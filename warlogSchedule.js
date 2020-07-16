const player = require('./api/player.js');
const clan = require('./api/clan.js');
const moment = require('moment-timezone');
const table = require('text-table');
const mergeImages = require('merge-images');
const { Canvas, Image } = require('canvas');
const { MessageAttachment, MessageEmbed } = require('discord.js');

/**
 * 
 * @param {The discord channel to send log embeds} channel 
 * @param {Clan tag} tag 
 * @param {Battles the last x milliseconds} interval 
 */
async function logBattles(channel, tag, interval) {
  try {

    const clanWarBattles = await getWarBattles(tag);
    
    const logBattles = clanWarBattles
      .filter(battle => moment(battle.battleTime).isAfter(moment().subtract(interval)))
      .map( async battle => {
        try {
         
          // Get player tag and the 25 resent battles played
          const playerTag = battle.team[0].tag;
          const playerBattles = await player.battles(playerTag.substr(1));

          // Get the deck played in the war battle and create a decklink to open in-game
          const warBattleDeck = battle.team[0].cards;
          const deckLink = buildDeckLink(warBattleDeck);

          // Player battles error handling
          if(!playerBattles || !Array.isArray(playerBattles))
          {
            console.log(`Player battles is not an array. Stopping`);
            return;
          }

          // Go through battles played and find matches where the war deck has been played.
          // ? Warday battle er strengt tatt ikke en trenings kamp, filtere ut den ?
          const trainingBattles = playerBattles
          .filter(playerBattle => 
             (isDeckEqual(warBattleDeck, playerBattle.team[0].cards) && playerTag === playerBattle.team[0].tag) 
             || (isDeckEqual(warBattleDeck, playerBattle.opponent[0].cards) && playerTag === playerBattle.opponent[0].tag)
          );

          // Group battles using type as key
          const groupedBattles = groupBy(trainingBattles, 'type');

          // Count total number of battles played with the war deck
          const totalTrainingCount =
              (groupedBattles['clanMate'] ? groupedBattles['clanMate'].length : 0) +
              (groupedBattles['challenge'] ? groupedBattles['challenge'].length : 0) +
              (groupedBattles['PvP'] ? groupedBattles['PvP'].length : 0) +
              (groupedBattles['tournament'] ? groupedBattles['tournament'].length : 0);

          // Count decks that is equal or is simular to the war deck. Then
          // create a table to show information
          const deckMatches = deckMatchCounts(warBattleDeck, playerTag, playerBattles);
          const countTable = createCountTable(deckMatches);

          // All friendly battles last 25 battles
          const allFriendlies = playerBattles.filter(battle => battle.type === 'clanMate').length;
          
          // Is the player victorious or not
          const victory = battle.team[0].crowns > battle.opponent[0].crowns;

          // A PNG image of the deck
          const deckImage = await createDeckImageBuffer(warBattleDeck);

          // The embed that is going to be returned to discord
          const embed = new MessageEmbed()
              .setColor(victory ? '#33cc33' : '#cc3300')
              .setTitle(victory ? 'Victory!' : 'Loss')
              .setDescription(`${battle.team[0].name} (${battle.team[0].startingTrophies}) vs ${battle.opponent[0].name} (${battle.opponent[0].startingTrophies})`)
              .addFields(
                { name: 'Player', value: `[${battle.team[0].name}](https://royaleapi.com/player/${playerTag.substr(1)})`, inline: true},
                { name: 'Opponent', value: `${battle.opponent[0].name}`, inline: true},
                { name: 'Battle time', value: `${moment
                      .utc(battle.battleTime)
                      .locale(process.env.MOMENT_LOCALE)
                      .tz(process.env.TIME_ZONE)
                      .format(process.env.MOMENT_DATETIME_FORMAT)}`},
                { name: 'Training', value: `${totalTrainingCount} practice battles with the war deck \n A total of ${allFriendlies} friendlies during the last 25 battles.\n The table is showing games played with the wardeck (WD) and games that is 1, 2, 3 or 4 cards diffrent from WD. ${countTable}`},
                { name: 'Deck', value: `[Click here to try the deck](${deckLink} "Deck") `}
              )
              .attachFiles(new MessageAttachment(deckImage, 'deck.png'))
              .setImage('attachment://deck.png')

          return embed;

        } catch(err) {console.log(err)}
      });

      // Loop throug all battles and send the embed to discord
      Promise.all(logBattles)
        .then((battles) => {
          battles.map(embedMessage => {
            channel.send(embedMessage) // .catch(err => {console.error(err.message)})       
          })
        })
        .catch(err => {console.error(err)});

  } catch(err) {console.log(err)}
}

/*
* Build an url that can be open in-game to copy in a deck
*/
function buildDeckLink(cards) {
  const deck = cards.map(card => card.id).join(';');

  return `https://link.clashroyale.com/deck/en?deck=${deck}&war=1`;
}

/*
* Get all war battles a clan has played
*/
async function getWarBattles(tag) {
  let warBattles = [];
  const clanMembers = await clan.members(tag);

  for(member in clanMembers) {
    const memberTag = clanMembers[member].tag.substr(1);
    const playerBattles = await player.battles(memberTag);
    
    const playerWarBattles = playerBattles
      .filter(battle => {
        return battle.type === 'clanWarWarDay';
      });

    if(playerWarBattles.length > 0)
    {
      warBattles = warBattles.concat(playerWarBattles);
    }
  }

  return warBattles;
};

/*
* Check if two decks is equal. Returns true if it is.
*/
function isDeckEqual(deck, otherDeck) {
  const deckString = deck
    .map(card => card.id)
    .sort()
    .join();
  const otherDeckString = otherDeck
    .map(card => card.id)
    .sort()
    .join();
  
  return deckString === otherDeckString;
};

/* 
* Group a set of key value pairs
*/
const groupBy = (xs, key) => {
  return xs.reduce(function(rv, x) {
      (rv[x[key]] = rv[x[key]] || []).push(x);
      return rv;
  }, {});
};

/* 
* Find the number of equal cards in wardeck and the otherdeck
*/
const numEqual = (warDeck, otherDeck) => {
  const warSet = new Set(warDeck.map(card => card.id));
  const otherSet = new Set(otherDeck.map(card => card.id));
  const intersection = new Set([...warSet].filter(id => otherSet.has(id)));
  return intersection.size;
};

/* 
* Counting number of cards that is equal to the war deck for a spesific game mode
*/
const deckMatchCounts = (warDeck, warBattleTag, playerBattles) =>
  playerBattles.map(playerBattle => {
    const playerBattleDeck =
      playerBattle.team
        .concat(playerBattle.opponent)
        .find(p => p.tag === warBattleTag)
        .cards;
    return {
      type: playerBattle.type,
      equalCards: numEqual(warDeck, playerBattleDeck)
    };
  });

  /**
   * Creating an array to store the number of equal cards in one type of game mode
   * @param {*} countGroup 
   */
const countArr = countGroup => countGroup.reduce((arr, {equalCards}) => {
    const countIdx = 8 - equalCards;
    
    if(countIdx < 5) {
      arr[countIdx] = arr[countIdx] + 1;
    }

    return arr;
  },[0, 0, 0, 0, 0]
);

/**
 * Creating a string from @matchCounts in a table format
 * @param {*} matchCounts 
 */
const createCountTable = matchCounts => {
  const grouped = groupBy(matchCounts, 'type');

  const tableRows = [
    ["", "WD", "-1", "-2", "-3", "-4"],
    []
  ];

  const totalCounts = ["Total", 0, 0, 0, 0, 0];

  Object.entries(grouped).forEach(
    ([type, counts]) => {
      const typeCounts = countArr(counts);
      tableRows.push([type, ...typeCounts]);
      for (let i = 0; i < 5; i++) {
        totalCounts[i + 1] += typeCounts[i];
      }
    }
  );

  tableRows.push([]);
  tableRows.push(totalCounts);

  return "```\n" + table(tableRows, {align: ['l', 'r', 'r', 'r', 'r', 'r']}) + "\n```";
};

/**
 * Normelizes the name of the card to fit the names of card images
 * @param {Name of a card from game data} cardName 
 */
const cardImageName = cardName => {
  return cardName.replace(/\./g, '').replace(' ', '-').toLowerCase();
};

/**
 * Creating a .PNG image of the deck returned as a Buffer
 * @param {An array containg eight cards} deck 
 */
const createDeckImageBuffer = async deck => {
  const cardImages = deck.map((card, i) => {
    const cardImageWidth = 302;
    const cardSrc = `./cards/${cardImageName(card.name)}.png`;

    const cardImage = {
      src: cardSrc,
      x: i * cardImageWidth,
      y: 0
    };

    return cardImage;
  });

  const deckImage = await mergeImages(cardImages, {
    width: 302*8,
    height: 363,
    Canvas: Canvas,
    Image: Image
  });

  const buffer = Buffer.from(deckImage.substring(deckImage.indexOf(',') + 1), 'base64');

  return buffer;
};

module.exports = { logBattles: logBattles };
