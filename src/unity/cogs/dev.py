import discord
from discord.ext import commands


class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command()
    async def ping(self, ctx):
        """Check the bot's latency."""
        latency = self.bot.latency * 1000  # Convert to milliseconds
        await ctx.respond(f"Pong! Latency: {latency:.2f} ms")


def setup(bot):
    bot.add_cog(Dev(bot))
