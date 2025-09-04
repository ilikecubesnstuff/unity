import logging
import os
import sys

from dotenv import load_dotenv

from .bot import create_bot

dotenv_path = sys.argv[2] if len(sys.argv) > 2 else ".env"
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"The .env file at {dotenv_path} does not exist.")
load_dotenv(dotenv_path)


# set up logging
logger = logging.getLogger("unity")

ch = logging.StreamHandler()
ch.setLevel(os.getenv("LOGGING_LEVEL", "INFO").upper())
logger.addHandler(ch)

fmt = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
ch.setFormatter(fmt)


# create and run the bot
bot = create_bot(
    debug_guilds=(
        os.getenv("DEBUG_GUILDS").split(",") if os.getenv("DEBUG_GUILDS") else None
    )
)
bot.run(os.getenv("DISCORD_TOKEN"))
