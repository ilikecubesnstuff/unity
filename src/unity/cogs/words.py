import logging
import os

import discord
from discord.ext import commands, tasks
from discord.ext.pages import Page, Paginator

from ..util.merweb import MerWebWrapper, mw_dict_link, processed

logger = logging.getLogger(__name__)


def definition_line(sn: str, dt: str) -> str:
    if not dt:
        return ""
    indent = ""
    if not sn:
        return f"{dt}\n"
    elif sn.split()[0] in "abcdefghijklmnopqrstuvwxyz":
        indent = "  "
    elif sn.split()[0].startswith("("):
        indent = "    "
    return f"**`{indent}{sn}`**{dt}\n"


def extract_pages_from_response(query, response):
    embed = discord.Embed(
        footer=discord.EmbedFooter(
            text="Data from Merriam-Webster",
            icon_url="https://dictionaryapi.com/images/info/branding-guidelines/MWLogo_DarkBG_120x120_2x.png",
        ),
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow(),
    )

    if not response:
        embed.description = f"No definitions found for **{query}**."
        embed.color = discord.Color.red()
        return [embed]

    if isinstance(response[0], str):
        suggestions = ", ".join(response)
        embed.description = (
            f"No exact match found for **{query}**. *Did you mean: {suggestions}?*"
        )
        embed.color = discord.Color.red()
        return [embed]

    pages = []
    for data in response:
        page_embed = embed.copy()
        word = data["hwi"]["hw"].replace("*", "")
        text = f"## [{word}]({mw_dict_link(word)}) ({data['fl']})\n"

        for sseq in data["def"]:
            for sense in sseq["sseq"]:
                for subsense in sense:
                    dt = ""
                    sn = ""
                    if subsense[0] == "sense":
                        sense_data = subsense[1]
                        sn = sense_data.get("sn", sn)
                        for el in sense_data["dt"]:
                            if el[0] == "text":
                                dt = el[1]
                                break
                        text += definition_line(sn, dt)
                    elif subsense[0] == "pseq":
                        sense_data = subsense[1]
                        for name, part in sense_data:
                            if name == "bs":
                                sn = part["sense"].get("sn", sn)
                                for el in part["sense"]["dt"]:
                                    if el[0] == "text":
                                        dt = el[1]
                                        break
                            elif name == "sense":
                                sn = part.get("sn", sn)
                                for el in part["dt"]:
                                    if el[0] == "text":
                                        dt = el[1]
                                        break
                            text += definition_line(sn, dt)
        if "pr" in data["hwi"]:
            page_embed.description = f"-# {data['hwi']['hw']} /{data['hwi']['pr']}/"
        if "et" in data:
            body = [item[1] for item in data["et"] if item[0] == "text"][
                0
            ]  # usually only one
            page_embed.add_field(name="Etymology", value=processed(body), inline=False)
        if "date" in data:
            page_embed.add_field(
                name="First Known Use", value=processed(data["date"]), inline=False
            )
        pages.append(Page(content=processed(text), embeds=[page_embed]))
    return pages


class Words(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mw_collegiate = MerWebWrapper(
            "https://dictionaryapi.com/api/v3/references/collegiate/json",
            os.getenv("MWD_COLLEGIATE_API_KEY"),
        )
        self.mw_medical = MerWebWrapper(
            "https://dictionaryapi.com/api/v3/references/medical/json",
            os.getenv("MWD_MEDICAL_API_KEY"),
        )

        # limit to 500 requests per day
        self.mw_collegiate_counter = 0
        self.mw_medical_counter = 0

    @discord.slash_command(name="define", description="Get the definition of a word")
    async def define_word(self, ctx, query: str):
        """Fetch and display the definition of a word from Merriam-Webster."""
        if self.mw_collegiate_counter >= 500:
            await ctx.respond("Daily request limit reached for collegiate dictionary.")
            return
        self.mw_collegiate_counter += 1
        response = await self.mw_collegiate.fetch(query)
        pages = extract_pages_from_response(query, response)
        paginator = Paginator(pages)
        await paginator.respond(ctx.interaction)

    @discord.slash_command(
        name="meddefine", description="Get the medical definition of a word"
    )
    async def meddefine_word(self, ctx, query: str):
        """Fetch and display the medical definition of a word from Merriam-Webster."""
        if self.mw_medical_counter >= 500:
            await ctx.respond("Daily request limit reached for medical dictionary.")
            return
        self.mw_medical_counter += 1
        response = await self.mw_medical.fetch(query)
        pages = extract_pages_from_response(query, response)
        paginator = Paginator(pages)
        await paginator.respond(ctx.interaction)

    @tasks.loop(hours=24)
    async def reset_counters(self):
        self.mw_collegiate_counter = 0
        self.mw_medical_counter = 0


def setup(bot):
    bot.add_cog(Words(bot))
