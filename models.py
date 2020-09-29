from mongoengine import Document, StringField, IntField, FloatField, BooleanField, DateTimeField

class Warlog(Document):
  clanTag = StringField(required = True)
  interval = IntField(default = 15) # mins
  previousRun = FloatField(default = 0.0)
  channelId = IntField(required = True)
  finishLineReached = BooleanField(default = False)
  meta = {"collection": "warlogs"}