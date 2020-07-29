from os import listdir, getcwd
from os.path import dirname, basename

class CommandHandler:

  def __init__(self, bot, commandsDir):
    self.bot = bot
    self.commandsDir = f"{getcwd()}/{commandsDir}"
    self.extensions = [f"{commandsDir}.{basename(f)[:-3]}" for f in listdir(self.commandsDir) if f[-3:] == ".py" and not f.endswith("__init__.py")]
    print(self.extensions)
    print("Loading commands...")

    for extension in self.extensions:
      try:
        self.bot.load_extension(extension)
      except Exception as e:
        print(f"Failed to load extension {extension}. Exception: {e}")

    print("Done")
