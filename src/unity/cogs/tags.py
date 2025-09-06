import logging
import re

import discord
from discord.ext import commands
from discord.ext.pages import Page, Paginator

from ..db.models import Tag

logger = logging.getLogger(__name__)


DISCORD_EMBED_LIMIT = 6000  # Discord's embed description limit is 6000 characters


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tag = discord.SlashCommandGroup("tag", "Manage and use tags")

    @tag.command(name="create")
    async def create_tag(self, ctx, trigger: str, *, response: str):
        """Create a new tag."""
        await Tag.create(trigger=trigger, response=response)
        logger.debug(f"Tag '{trigger}' created with response: {response}")
        await ctx.respond(f"Tag created: `{trigger}` → `{response}`")

    @tag.command(name="delete")
    async def delete_tag(self, ctx, trigger: str):
        """Delete an existing tag."""
        tag = await Tag.get_or_none(trigger=trigger)
        if tag:
            await tag.delete()
            logger.debug(f"Tag '{trigger}' deleted.")
            await ctx.respond(f"Tag deleted: `{trigger}`")
        else:
            logger.debug(f"Attempted to delete non-existent tag '{trigger}'.")
            await ctx.respond(f"Tag not found: `{trigger}`")

    @tag.command(name="list")
    async def list_tags(self, ctx):
        """List all tags."""
        tags = await Tag.all()
        if not tags:
            await ctx.respond("No tags defined.")
            return

        pages = []
        buffer = discord.Embed(title="Tags", color=discord.Color.blue())
        for tag in tags:
            if (
                len(buffer) + len(tag.trigger) + len(tag.response) + 8
                > DISCORD_EMBED_LIMIT
            ):
                pages.append(Page(embeds=[buffer]))
                buffer = discord.Embed(title="Tags", color=discord.Color.blue())
            buffer.add_field(name=f"`{tag.trigger}`", value=tag.response, inline=False)
        pages.append(Page(embeds=[buffer]))

        paginator = Paginator(pages=pages, loop_pages=True)
        await paginator.respond(ctx.interaction)

    @tag.command(name="search")
    async def search_tags(self, ctx, query: str):
        """Search for tags by trigger or response."""
        tags = await Tag.all()
        tags = [
            tag
            for tag in tags
            if re.search(query, tag.trigger) or re.search(query, tag.response)
        ]
        if not tags:
            await ctx.respond(f"No tags found matching `{query}`.")
            return

        pages = []
        buffer = discord.Embed(
            title=f"Search results for '{query}'", color=discord.Color.green()
        )
        for tag in tags:
            if (
                len(buffer) + len(tag.trigger) + len(tag.response) + 8
                > DISCORD_EMBED_LIMIT
            ):
                pages.append(Page(embeds=[buffer]))
                buffer = discord.Embed(
                    title=f"Search results for '{query}'", color=discord.Color.green()
                )
            buffer.add_field(name=f"`{tag.trigger}`", value=tag.response, inline=False)
        pages.append(Page(embeds=[buffer]))

        paginator = Paginator(pages=pages, loop_pages=True)
        await paginator.respond(ctx.interaction)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Respond to messages that match a tag trigger."""
        if message.author.bot:
            return

        tags = await Tag.all()
        for tag in tags:
            if re.fullmatch(tag.trigger, message.content, re.DOTALL):
                await message.channel.send(tag.response)
                return


def setup(bot):
    bot.add_cog(Tags(bot))
