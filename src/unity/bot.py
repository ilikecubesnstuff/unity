import logging
from pathlib import Path

import discord

logger = logging.getLogger(__name__)


class UnityBot(discord.Bot):

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}. (ID: {self.user.id})")
        if self.status:
            logger.info(f"Status set to {self.status.name}.")
        if self.activity:
            logger.info(
                f"Activity set to {self.activity.type.name + " " + self.activity.name if self.activity.type is not discord.ActivityType.custom else self.activity.name}."
            )
        logger.info(f"Connected to {len(self.guilds)} guild(s).")
        for guild in self.guilds:
            logger.debug(f"Connected to guild: {guild.name}. (ID: {guild.id})")


def create_bot(
    activity=None,
    status=None,
    debug_guilds=None,
    cogs_path=Path("src/unity/cogs"),
):
    bot = UnityBot(activity=activity, status=status, debug_guilds=debug_guilds)

    cogs_path = Path(cogs_path)
    if not cogs_path.exists():
        raise FileNotFoundError(f"The directory {cogs_path} does not exist.")

    for file in cogs_path.glob("*.py"):
        extension = f"unity.cogs.{file.stem}"
        try:
            bot.load_extension(extension)
            logger.info(f"Loaded extension '{extension}'.")
        except Exception as e:
            logger.error(f"Failed to load extension {extension}.", exc_info=e)

    return bot
