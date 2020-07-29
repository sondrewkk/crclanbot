from environs import Env
from marshmallow.validate import OneOf

class Environment:
  
  env = Env()
  env.read_env()

  PREFIX = env.str("PREFIX")
  PYTHON_ENV = env.str("PYTHON_ENV", validate=OneOf(["production", "development"], error="PYTHON_ENV must be one of: {choices}")) 
  TEST_DATA = env.bool("TEST_DATA", False)
  DISCORD_TOKEN = env.str("DISCORD_TOKEN")
  DB_NAME = env.str("DB_NAME")
  CR_API_TOKEN = env.str("CR_API_TOKEN")
  CR_API_URL = env.str("CR_API_URL")
