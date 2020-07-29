import requests
from environment import Environment
import json
class ClashRoyaleApi:

  def __init__(self):
    self.env = Environment()
    self.isDevelopment = (self.env.PYTHON_ENV == "development" and not self.env.TEST_DATA)

  def get(self, url):
    headers = {
      "Authorization": "Bearer {}".format(self.env.CR_API_TOKEN),
      "Content-type": "Application/json"  
    }

    res = requests.get(url, headers = headers)

    if res.status_code == 200:
      return res.json()
    else:
      return None

  def loadTestData(self, fileName):
    with open(f"testdata/{fileName}.json", "r+") as json_file:
      data = json.load(json_file)
      return data

  def saveTestData(self, fileName, data):
    with open(f"testdata/{fileName}.json", "w+") as json_file:
        json_file.seek(0)
        json.dump(data, json_file)
        json_file.truncate()


  def getWarlog(self, clanTag):

    if self.isDevelopment:
      return self.loadTestData(f"warlog_{clanTag}")["items"]

    url = f"https://{self.env.CR_API_URL}/clans/%23{clanTag}/warlog"
    warlog = self.get(url)

    if warlog is not None:

      if self.env.TEST_DATA:
        self.saveTestData(f"warlog_{clanTag}", warlog)

      return warlog["items"]
    else:
      print(f"Failed to get warlog for clan({clanTag}")
      return None

  def getPlayerBattles(self, playerTag):

    if self.isDevelopment:
      return self.loadTestData(f"player_{playerTag}")

    url = f"https://{self.env.CR_API_URL}/players/%23{playerTag}/battlelog"
    playerBattles = self.get(url)

    if playerBattles is not None:
      if self.env.TEST_DATA:
        self.saveTestData(f"player_{playerTag}", playerBattles)

      return playerBattles
    else:
      print(f"Failed to get player battles for player {playerTag}")
      return None

  def getClanMemebers(self, clanTag):
    url = f"https://{self.env.CR_API_URL}/clans/%23{clanTag}/members"
    clanMembers = self.get(url)

    if clanMembers is not None:
      return clanMembers["items"]
    else:
      print(f"Failed to get clan memebers for clan: {clanTag}")
      return None

  def getClanWarDayBattles(self, clanTag):

    if self.isDevelopment:
      return self.loadTestData("warBattles")

    clanMembers = self.getClanMemebers(clanTag)

    if clanMembers is not None:
      warBattles = []

      for member in clanMembers:
        playerTag = member["tag"][1:]
        playerBattles = self.getPlayerBattles(playerTag)       
        playerWarBattles = [battle for battle in playerBattles if battle["type"] == "clanWarWarDay"]
        
        if len(playerWarBattles) > 0:
          warBattles.extend(playerWarBattles)

      if self.env.TEST_DATA:
        self.saveTestData("warBattles", warBattles)
          
      return warBattles

    else:
      print(f"Failed to get clan war day battles from clan: {clanTag}")
      return None
