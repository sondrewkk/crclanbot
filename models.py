from mongoengine import Document, StringField, IntField

class WarlogModel(Document):
  clanTag = StringField(required = True)
  interval = IntField(default = 15) # mins
  previousRun = IntField(default = 0)
  channelId = IntField(required = True)
  meta = {"collection": "warlogs"}