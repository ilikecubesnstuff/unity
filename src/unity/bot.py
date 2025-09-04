from pathlib import Path

import discord


def create_bot(debug_guilds=None, cogs_path=Path("src/unity/cogs")):
    bot = discord.Bot(debug_guilds=debug_guilds)

    cogs_path = Path(cogs_path)
    if not cogs_path.exists():
        raise FileNotFoundError(f"The directory {cogs_path} does not exist.")

    for file in cogs_path.glob("*.py"):
        extension = f"unity.cogs.{file.stem}"
        try:
            bot.load_extension(extension)
            print(f"Loaded extension '{extension}'")
        except Exception as e:
            print(f"Failed to load extension {extension}.", e)

    return bot
