import subprocess

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

    extensions = discord.SlashCommandGroup("extensions", "Manage bot extensions")

    @extensions.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, name):
        """Load an extension."""
        extension = f"unity.cogs.{name}"
        try:
            ctx.bot.load_extension(extension)
            await ctx.respond(f"Loaded extension '{name}'.")
        except Exception as e:
            await ctx.respond(
                f"Failed to load extension '{name}'. See error message:\n```{e}```"
            )

    @extensions.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, name):
        """Unload an extension."""
        if name == "dev":
            await ctx.respond("You cannot unload the 'dev' extension.")
            return
        extension = f"unity.cogs.{name}"
        try:
            ctx.bot.unload_extension(extension)
            await ctx.respond(f"Unloaded extension '{name}'.")
        except Exception as e:
            await ctx.respond(
                f"Failed to unload extension '{name}'. See error message:\n```{e}```"
            )

    @extensions.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, name):
        """Reload an extension."""
        extension = f"unity.cogs.{name}"
        try:
            ctx.bot.reload_extension(extension)
            await ctx.respond(f"Reloaded extension '{name}'.")
        except Exception as e:
            await ctx.respond(
                f"Failed to reload extension '{name}'. See error message:\n```{e}```"
            )
    
    git = discord.SlashCommandGroup("git", "Git operations")

    @git.command(name="pull")
    @commands.is_owner()
    async def pull(self, ctx):
        """Pull the latest changes from the git repository."""
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True,
                check=True
            )
            output = (result.stdout + result.stderr).strip()
            message = "Git pull successful."
            if output:
                message += f"\n```{output}```"
            await ctx.respond(message)
        except subprocess.CalledProcessError as e:
            await ctx.respond(f"Git pull failed:\n```{e.stdout}\n{e.stderr}```")

    @git.command(name="checkout")
    @commands.is_owner()
    async def checkout(self, ctx, branch: str):
        """Checkout a specific branch in the git repository."""
        try:
            result = subprocess.run(
                ["git", "checkout", branch],
                capture_output=True,
                text=True,
                check=True
            )
            output = (result.stdout + result.stderr).strip()
            message = f"Checked out branch '{branch}'."
            if output:
                message += f"\n```{output}```"
            await ctx.respond(message)
        except subprocess.CalledProcessError as e:
            await ctx.respond(f"Git checkout failed:\n```{e.stdout}\n{e.stderr}```")


def setup(bot):
    bot.add_cog(Dev(bot))
