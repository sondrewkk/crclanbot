from crApi import ClashRoyaleApi
from datetime import datetime, timedelta
from dateutil.parser import *
from io import BytesIO
from PIL import Image
from discord import File, Embed, Colour
from pytz import timezone
import pytz

api = ClashRoyaleApi()

async def logBattles(channel, clanTag, warStart, interval):
  riverraceBattles = api.getClanRiverraceBattles(clanTag)
  
  intervalTime = datetime.now(tz=pytz.utc) - timedelta(seconds=interval)
  riverraceBattlesFiltered = [battle for battle in riverraceBattles if parse(battle["battleTime"]) > intervalTime]

  for battle in riverraceBattlesFiltered:
    gameType = battle["type"]

    if gameType == "riverRaceDuel":
      embed = await _duelLog(battle, channel)
    else:
      embed = await _singelLog(battle, channel)


###########################################################
# Helper functions
# #########################################################
async def _duelLog(battle, channel):
  player = battle["team"][0]
  opponent = battle["opponent"][0]

  numOfBattles = int(len(player["cards"]) / 8)
  decks = []
  deckLinks = []

  for i in range(numOfBattles):
    start = i * 8
    end = start + 8
    decks.append(player["cards"][start:end])

  for deck in decks:
    link = _buildDeckLink(deck)
    deckLinks.append(link)

  deckImageBuffer = _createDeckImageBuffer(decks)
  deckAttachment = File(deckImageBuffer, filename="deck.png")

  playerTag = player["tag"]
  victory = player["crowns"] > opponent["crowns"]
  title = "Won the duel!" if victory else "Lost the duel"
  color = Colour.green() if victory else Colour.red()
  
  description = f"{player['name']} ({player['startingTrophies']}) vs {opponent['name']} ({opponent['startingTrophies']})"
  oslo = timezone("Europe/Oslo")
  battleTime = parse(battle["battleTime"]).replace(tzinfo=oslo)
  deckLinkInfo = "Clink on the deck you want to try:\n"

  for idx, deckLink in enumerate(deckLinks):
    deckLinkInfo += f"[Match {idx}]({deckLink} \"Deck\")\n"

  embed = Embed(title=title, color=color, description=description)

  embed.add_field(name='Player', value=f"[{player['name']}](https://royaleapi.com/player/{playerTag[1:]})")
  embed.add_field(name='Opponent', value=opponent["name"])
  embed.add_field(name='Battle time', value=battleTime, inline=False)
  embed.add_field(name='Duel summary', value = f"The fight needed {numOfBattles} rounds to get a winner.\n", inline=False)
  embed.add_field(name='Decks', value=deckLinkInfo, inline=False)
  embed.set_image(url="attachment://deck.png")
  
  await channel.send(file=deckAttachment, embed=embed)

async def _singelLog(battle, channel):
  player = battle["team"][0]
  opponent = battle["opponent"][0]

  warBattleDeck = []
  warBattleDeck.append(player["cards"])
  deckLink = _buildDeckLink(warBattleDeck[0])
  deckImageBuffer = _createDeckImageBuffer(warBattleDeck)
  deckAttachment = File(deckImageBuffer, filename="deck.png")

  playerTag = player["tag"]
  victory = player["crowns"] > opponent["crowns"]
  title = "Victory!" if victory else "Loss"
  color = Colour.green() if victory else Colour.red()
  description = f"{player['name']} ({player['startingTrophies']}) vs {opponent['name']} ({opponent['startingTrophies']})"
  oslo = timezone("Europe/Oslo")
  battleTime = parse(battle["battleTime"]).replace(tzinfo=oslo)

  embed = Embed(title=title, color=color, description=description)

  embed.add_field(name='Player', value=f"[{player['name']}](https://royaleapi.com/player/{playerTag[1:]})")
  embed.add_field(name='Opponent', value=opponent["name"])
  embed.add_field(name='Battle time', value=battleTime, inline=False)
  embed.add_field(name='Deck', value=f"[Click here to try the deck]({deckLink} \"Deck\")", inline=False)
  embed.set_image(url="attachment://deck.png")

  await channel.send(file=deckAttachment, embed=embed)

def _buildDeckLink(cards):
  deck = ";".join([str(card["id"]) for card in cards])
  return f"https://link.clashroyale.com/deck/en?deck={deck}"

def _createDeckImageBuffer(decks):
  cardImageWidth = 302
  cardImageHeight = 363
  xOffset = 0
  yOffset = 0
  xPos = 0
  yPos = 0
  deckImageWidht = cardImageWidth * len(decks[0])
  deckImageHeight = cardImageHeight * len(decks)
  
  deckImage = Image.new("RGBA", (deckImageWidht, deckImageHeight))

  for deck in decks:
    for card in deck:
      cardName = _getCardImageName(card["name"])
      cardImageSrc = f"./cards/{cardName}.png"
      cardImage = Image.open(cardImageSrc)
      
      xPos = cardImageWidth * xOffset
      deckImage.paste(cardImage, (xPos, yPos))
      xOffset += 1
    
    xOffset = 0
    yOffset += 1
    yPos = cardImageHeight * yOffset
  
  imageBuffer = BytesIO()
  deckImage.save(imageBuffer, format="png")
  imageBuffer.seek(0)

  return imageBuffer

def _getCardImageName(cardName):
  translateTable = {" ": "-", ".": ""}
  cardImageName = cardName.translate(str.maketrans(translateTable)).lower()

  return cardImageName
