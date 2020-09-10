from crApi import ClashRoyaleApi
from datetime import datetime, timedelta
from dateutil.parser import *
from itertools import groupby
from tabulate import tabulate
from io import BytesIO
from PIL import Image
# import string
from discord import File, Embed, Colour
from pytz import timezone
import pytz

api = ClashRoyaleApi()

async def logBattles(channel, clanTag, warStart, interval):
  print("Log Battles...")
  riverraceBattles = api.getClanRiverraceBattles(clanTag)
  print(riverraceBattles)
  # intervalTime = datetime.now(tz=pytz.utc) - timedelta(minutes=interval)
  # riverraceBattlesFiltered = [battle for battle in riverraceBattles if parse(battle["battleTime"]) > intervalTime]

  # for battle in riverraceBattlesFiltered:

  #   player = battle["team"][0]
  #   opponent = battle["opponent"][0]

    # Ikke intressant å sjekke opp treningskamper. Må heller sjekke lvl på kort, link til side med tips til endringer og synergier
    # # Get player tag and the last 25 battles played
    # playerTag = player["tag"][1:]
    # playerBattles = api.getPlayerBattles(playerTag)
    
    # if playerBattles is None or type(playerBattles) is not list:
    #   print("Player battles is not an array. Stopping")
    #   continue

    # playerBattlesFiltered = [battle for battle in playerBattles if parse(battle["battleTime"]) > warStart]
    # playerBattlesGrouped = _groupBattles(playerBattlesFiltered, "type")

    # Get the deck that was played in the war battle and create decklink to open in-game
    # warBattleDeck = player["cards"]
    # deckLink = _buildDeckLink(warBattleDeck)

    #groupedDeckMatches = _deckMatches(warBattleDeck, playerTag, playerBattlesGrouped)
    #deckMatchTable = _createDeckMatchesTable(groupedDeckMatches) 

    #numOfTraningBattles = _countTraningBattles(groupedDeckMatches)
    #numOfFriendlyBattles = len([battle for battle in playerBattles if battle["type"] == "clanMate"])

    # deckImageBuffer = _createDeckImageBuffer(warBattleDeck)
    # deckAttachment = File(deckImageBuffer, filename="deck.png")

    #victory = player["crowns"] > opponent["crowns"]
    #title = "Victory!" if victory else "Loss"
    #color = Colour.green() if victory else Colour.red()
    #description = f"{player['name']} ({player['startingTrophies']}) vs {opponent['name']} ({opponent['startingTrophies']})"
    #oslo = timezone("Europe/Oslo")
    #battleTime = parse(battle["battleTime"]).replace(tzinfo=oslo)

    #embed = Embed(title=title, color=color, description=description)

    # embed.add_field(name='Player', value=f"[{player['name']}](https://royaleapi.com/player/{playerTag[1:]})")
    # embed.add_field(name='Opponent', value=opponent["name"])
    # embed.add_field(name='Battle time', value=battleTime, inline=False)
    # embed.add_field(name='Training', value=f"{numOfTraningBattles} practice battles with the war deck \n A total of {numOfFriendlyBattles} friendlies during the last 25 battles.\n```{deckMatchTable}```\n *NOTE: The table is showing games played with the wardeck (WD) and games that is 1, 2, 3 or 4 cards diffrent from WD.*", inline=False)
    # embed.add_field(name='Deck', value=f"[Click here to try the deck]({deckLink} \"Deck\")", inline=False)
    # embed.set_image(url="attachment://deck.png")

    #await channel.send(file=deckAttachment, embed=embed)


###########################################################
# Helper functions
# #########################################################
def _buildDeckLink(cards):
  deck = ";".join([str(card["id"]) for card in cards])
  return f"https://link.clashroyale.com/deck/en?deck={deck}&war=1"

def _groupBattles(battles, key):
  groups = {}
  battles.sort(key=lambda battle: battle[key])

  for k, g in groupby(battles, lambda battle: battle[key]):
    groups.update({k: list(g)})
  
  return groups

def _countTraningBattles(deckMatchesGroups):
  traningBattles = 0

  for group in deckMatchesGroups:
    if group != "clanWarWarDay":
      traningBattles += deckMatchesGroups[group][8]
  
  return traningBattles

def _numberOfEqualCards(warDeck, otherDeck):
  warSet = set(([card["id"] for card in warDeck]))
  otherSet = set(([card["id"] for card in otherDeck]))
  matches = warSet.intersection(otherSet)
  
  return len(matches)

def _deckMatches(warDeck, playerTag, battleGroups):
  groupMatches = {}

  for group in battleGroups:
    battles = battleGroups[group]
    cardMatches = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    for battle in battles:
      deck = battle["team"][0]["cards"]
      matches = _numberOfEqualCards(warDeck, deck)
      cardMatches[matches] += 1
    
    groupMatches.update({group: cardMatches})

  return groupMatches

def _createDeckMatchesTable(matchesGrouped):
  headers = ["Battle type", "WD", "-1", "-2", "-3", "-4"]
  table = []

  for group in matchesGrouped:
    if group != "clanWarWarDay":
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
  
  tableStr = tabulate(table, headers=headers, tablefmt="presto")
  
  return tableStr

def _createDeckImageBuffer(deck):
  cardImageWidth = 302
  cardImageHeight = 363
  deckImageWidht = cardImageWidth * len(deck)
  xOffset = 0
  
  deckImage = Image.new("RGBA", (deckImageWidht, cardImageHeight))

  for card in deck:
    cardName = _getCardImageName(card["name"])
    cardImageSrc = f"./cards/{cardName}.png"
    cardImage = Image.open(cardImageSrc)
    
    xPos = cardImageWidth * xOffset
    deckImage.paste(cardImage, (xPos, 0))
    xOffset += 1
  
  imageBuffer = BytesIO()
  deckImage.save(imageBuffer, format="png")
  imageBuffer.seek(0)

  return imageBuffer

def _getCardImageName(cardName):
  translateTable = {" ": "-", ".": ""}
  cardImageName = cardName.translate(str.maketrans(translateTable)).lower()

  return cardImageName
