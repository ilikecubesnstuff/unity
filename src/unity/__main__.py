import logging
import os
import sys

from dotenv import load_dotenv
import discord

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
status = os.getenv("BOT_STATUS", "online").lower()
activity_type = os.getenv("BOT_ACTIVITY_TYPE", "playing").lower()
activity_name = os.getenv("BOT_ACTIVITY_NAME", None)

bot = create_bot(
    debug_guilds=(
        os.getenv("DEBUG_GUILDS").split(",") if os.getenv("DEBUG_GUILDS") else None
    ),
    status=getattr(discord.Status, status, discord.Status.online),
    activity=discord.Activity(
        type=getattr(discord.ActivityType, activity_type, discord.ActivityType.playing),
        name=activity_name,
    ) if activity_name else None,
)
bot.run(os.getenv("DISCORD_TOKEN"))
