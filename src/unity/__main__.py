import os
import sys

from dotenv import load_dotenv

from .bot import bot

dotenv_path = sys.argv[2] if len(sys.argv) > 2 else ".env"
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"The .env file at {dotenv_path} does not exist.")

load_dotenv(dotenv_path)
bot.run(os.getenv("DISCORD_TOKEN"))
