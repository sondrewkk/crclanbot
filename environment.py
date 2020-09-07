from environs import Env
from marshmallow.validate import OneOf
from get_docker_secret import get_docker_secret

class Environment:
  env = Env()
  env.read_env()

  PREFIX = env.str("PREFIX")
  PYTHON_ENV = env.str("PYTHON_ENV", validate=OneOf(["production", "development"], error="PYTHON_ENV must be one of: {choices}")) 
  TEST_DATA = env.bool("TEST_DATA", False)
  DISCORD_TOKEN = get_docker_secret("DISCORD_TOKEN", autocast_name=False)
  DB_NAME = env.str("DB_NAME")
  DB_HOST = env.str("DB_HOST")
  DB_PORT = env.int("DB_PORT")
  DB_USER = env.str("DB_USER")
  DB_USER_PASS = get_docker_secret("DB_USER_PASS", autocast_name=False)
  CR_API_TOKEN = get_docker_secret("CR_API_TOKEN", autocast_name=False)
  CR_API_URL = env.str("CR_API_URL")
  