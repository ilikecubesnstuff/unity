from pathlib import Path

import discord

bot = discord.Bot()

dir_cogs = Path("src/unity/cogs")
if not dir_cogs.exists():
    raise FileNotFoundError(f"The directory {dir_cogs} does not exist.")

for file in dir_cogs.glob("*.py"):
    extension = f"unity.cogs.{file.stem}"
    try:
        bot.load_extension(extension)
        print(f"Loaded extension '{extension}'")
    except Exception as e:
        print(f"Failed to load extension {extension}.", e)
