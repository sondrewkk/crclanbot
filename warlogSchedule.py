from crApi import ClashRoyaleApi
from datetime import datetime, timezone, timedelta
from dateutil.parser import *
from itertools import groupby
from tabulate import tabulate
import json
import re
import base64
from io import BytesIO
from PIL import Image
import string

api = ClashRoyaleApi()

#def logBattles(channel, clanTag, interval):
def logBattles(channel, clanTag, warStart, interval):
  print("Log Battles...")
  
  warDayBattles = api.getClanWarDayBattles(clanTag)
  
  intervalTime = datetime.now(tz = timezone.utc) - timedelta(minutes = interval)
  #intervalTime = datetime.now(tz = timezone.utc) - timedelta(hours = 48)
  warDayBattlesFiltered = [battle for battle in warDayBattles if parse(battle["battleTime"]) > intervalTime]

  print(f"Warday filter battles \n{len(warDayBattlesFiltered)}")

  for battle in warDayBattlesFiltered:

    # Get player tag and the last 25 battles played
    playerTag = battle["team"][0]["tag"][1:]
    print(f"Player: {playerTag}")
    playerBattles = api.getPlayerBattles(playerTag)
    
    if playerBattles is None or type(playerBattles) is not list:
      print("Player battles is not an array. Stopping")
      continue

    playerBattlesFiltered = [battle for battle in playerBattles if parse(battle["battleTime"]) > warStart]
    playerBattlesGrouped = groupBattles(playerBattlesFiltered, "type")

    # Get the deck that was played in the war battle and create decklink to open in-game
    warBattleDeck = battle["team"][0]["cards"]
    deckLink = buildDeckLink(warBattleDeck)


    groupedDeckMatches = deckMatches(warBattleDeck, playerTag, playerBattlesGrouped)
    createDeckMatchesTable(groupedDeckMatches)

    numOfTraningBattles = countTraningBattles(groupedDeckMatches)
    numOfFriendlyBattles = len([battle for battle in playerBattles if battle["type"] == "clanMate"])

    victory = battle["team"][0]["crowns"] > battle["opponent"][0]["crowns"]

    deckImageBuffer = createDeckImageBuffer(warBattleDeck)
    #print(deckImageBuffer)

    print("\n")
    
    


 

def buildDeckLink(cards):
  deck = ";".join([str(card["id"]) for card in cards])
  return f"https://link.clashroyale.com/deck/en?deck={deck}&war=1"
  
# def trainingBattleFilter(playerTag, warBattleDeck, playerBattle):
#   deckEqualTeam = isDeckEqual(warBattleDeck, playerBattle["team"][0]["cards"]) and playerTag == playerBattle["team"][0]["tag"][1:]
#   #deckEqualOpponent = isDeckEqual(warBattleDeck, playerBattle["opponent"][0]["cards"]) and playerTag == playerBattle["opponent"][0]["tag"][1:]

#   return deckEqualTeam #or deckEqualOpponent

# def isDeckEqual(deck, otherDeck):
#   cardIds = sorted([card["id"] for card in deck])
#   otherCardIds = sorted([card["id"] for card in otherDeck])

#   return cardIds == otherCardIds

def groupBattles(battles, key):
  groups = {}
  battles.sort(key = lambda battle: battle[key])

  for k, g in groupby(battles, lambda battle: battle[key]):
    groups.update({k: list(g)})
  
  return groups

# def countBattles(groups):
#   total = 0
#   battlesCounted = {}

#   for group in groups:
#     count = len(groups[group])
#     total += count
#     battlesCounted.update({group: count})
  
#   battlesCounted.update({"total": total})

#   return battlesCounted

def countTraningBattles(deckMatchesGroups):
  traningBattles = 0

  for group in deckMatchesGroups:
    if group != "clanWarWarDay":
      traningBattles += deckMatchesGroups[group][8]
  
  return traningBattles


def numberOfEqualCards(warDeck, otherDeck):
  warSet = set(([card["id"] for card in warDeck]))
  otherSet = set(([card["id"] for card in otherDeck]))
  matches = warSet.intersection(otherSet)
  
  return len(matches)

def deckMatches(warDeck, playerTag, battleGroups):
  groupMatches = {}

  for group in battleGroups:
    battles = battleGroups[group]
    cardMatches = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for battle in battles:
      deck = battle["team"][0]["cards"]
      matches = numberOfEqualCards(warDeck, deck)
      cardMatches[matches] += 1
    
    groupMatches.update({group: cardMatches})

  return groupMatches

def createDeckMatchesTable(matchesGrouped):
  headers = ["Battle type", "WD", "-1", "-2", "-3", "-4"]
  table = []

  for group in matchesGrouped:
    row = []
    hasMatch = False
    row.append(group)

    for i in range(8, 3, -1):
      numOfMatches = matchesGrouped[group][i]
      row.append(numOfMatches)

      if numOfMatches > 0:
        hasMatch = True
    
    if hasMatch:
      table.append(row)
  
  return table

def createDeckImageBuffer(deck):
  print("create deck image buffer")
  cardImageWidth = 302
  cardImageHeight = 363
  deckImageWidht = cardImageWidth * len(deck)
  xOffset = 0
  
  deckImage = Image.new("RGB", (deckImageWidht, cardImageHeight))

  for card in deck:
    cardName = getCardImageName(card["name"])
    cardImageSrc = f"./cards/{cardName}.png"
    cardImage = Image.open(cardImageSrc)
    
    xPos = cardImageWidth * xOffset
    deckImage.paste(cardImage, (xPos, 0))
    xOffset += 1
  
  imageBuffer = BytesIO()
  deckImage.save(imageBuffer, format="PNG")
  imageStr = base64.b64encode(imageBuffer.getvalue())

  return imageStr  

  

  

# /**
#  * Creating a .PNG image of the deck returned as a Buffer
#  * @param {An array containg eight cards} deck 
#  */
# const createDeckImageBuffer = async deck => {
#   const cardImages = deck.map((card, i) => {
#     const cardImageWidth = 302;
#     const cardSrc = `./cards/${cardImageName(card.name)}.png`;

#     const cardImage = {
#       src: cardSrc,
#       x: i * cardImageWidth,
#       y: 0
#     };

#     return cardImage;

#   const deckImage = await mergeImages(cardImages, {
#     width: 302*8,
#     height: 363,
#     Canvas: Canvas,
#     Image: Image
#   });

#   const buffer = Buffer.from(deckImage.substring(deckImage.indexOf(',') + 1), 'base64');

#   return buffer;
#   });
def getCardImageName(cardName):
  cardImageName = cardName.replace(" ", "-").lower()
  print(cardImageName)
  cardImageName = cardImageName.translate(str.maketrans("","", string.punctuation))
  print(f"{cardName} \t\t {cardImageName}")
  return cardImageName

#           // The embed that is going to be returned to discord
#           const embed = new MessageEmbed()
#               .setColor(victory ? '#33cc33' : '#cc3300')
#               .setTitle(victory ? 'Victory!' : 'Loss')
#               .setDescription(`${battle.team[0].name} (${battle.team[0].startingTrophies}) vs ${battle.opponent[0].name} (${battle.opponent[0].startingTrophies})`)
#               .addFields(
#                 { name: 'Player', value: `[${battle.team[0].name}](https://royaleapi.com/player/${playerTag.substr(1)})`, inline: true},
#                 { name: 'Opponent', value: `${battle.opponent[0].name}`, inline: true},
#                 { name: 'Battle time', value: `${moment
#                       .utc(battle.battleTime)
#                       .locale(process.env.MOMENT_LOCALE)
#                       .tz(process.env.TIME_ZONE)
#                       .format(process.env.MOMENT_DATETIME_FORMAT)}`},
#                 { name: 'Training', value: `${totalTrainingCount} practice battles with the war deck \n A total of ${allFriendlies} friendlies during the last 25 battles.\n The table is showing games played with the wardeck (WD) and games that is 1, 2, 3 or 4 cards diffrent from WD. ${countTable}`},
#                 { name: 'Deck', value: `[Click here to try the deck](${deckLink} "Deck") `}
#               )
#               .attachFiles(new MessageAttachment(deckImage, 'deck.png'))
#               .setImage('attachment://deck.png')

#           return embed;

#         } catch(err) {console.log(err)}
#       });

#       // Loop throug all battles and send the embed to discord
#       Promise.all(logBattles)
#         .then((battles) => {
#           battles.map(embedMessage => {
#             channel.send(embedMessage) // .catch(err => {console.error(err.message)})       
#           })
#         })
#         .catch(err => {console.error(err)});

#   } catch(err) {console.log(err)}
# }





# };

# module.exports = { logBattles: logBattles };

