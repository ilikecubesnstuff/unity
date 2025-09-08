import logging
import os

import discord
from discord.ext import commands, tasks
from discord.ext.pages import Page, Paginator

from ..util.merweb import ICON, MerWebWrapper, mw_dict_link, processed

logger = logging.getLogger(__name__)


# definition line
def def_ln(sn: str, dt: str) -> str:
    if not dt:
        return ""
    indent = ""
    if not sn:
        return f"{dt}"
    elif sn.split()[0] in "abcdefghijklmnopqrstuvwxyz":
        indent = "  "
    elif sn.split()[0].startswith("("):
        indent = "    "
    return f"**`{indent}{sn}`**{dt}"


def extract_page_from_entry(entry):
    # basic info
    word = entry["hwi"]["hw"].replace("*", "")
    fl = f" ({entry['fl']})" if "fl" in entry else ""

    # set up embed description with pronunciation if available
    description = f"-# {word}"
    if "prs" in entry["hwi"]:
        prs = entry["hwi"]["prs"]
        pr_strs = [pr["mw"] for pr in prs if "mw" in pr]
        if pr_strs:
            description = f"-# {word} /{', '.join(pr_strs)}/"
        else:
            description = f"-# {word}"

    # construct main text with definitions
    lines = [f"## {mw_dict_link(word)}{fl}"]
    for sseq in entry["def"]:
        if "vd" in sseq:
            lines.append(f"-# {sseq['vd']}")
        for sense in sseq["sseq"]:
            for subsense in sense:
                if subsense[0] == "sense" or subsense[0] == "sen":
                    info = subsense[1]
                    data = info.get("dt", []) or info.get("et", [])
                    for el in data:
                        if el[0] == "text":
                            lines.append(def_ln(info.get("sn", ""), el[1]))
                            break
                elif subsense[0] == "pseq":
                    ps_info = subsense[1]
                    for name, part in ps_info:
                        if name == "bs":
                            info = part["sense"]
                            data = info.get("dt", []) or info.get("et", [])
                            for el in data:
                                if el[0] == "text":
                                    lines.append(def_ln(info.get("sn", ""), el[1]))
                                    break
                        elif name == "sense" or name == "sen":
                            info = part
                            data = info.get("dt", []) or info.get("et", [])
                            for el in data:
                                if el[0] == "text":
                                    lines.append(def_ln(info.get("sn", ""), el[1]))
                                    break
        lines.append("")

    # construct embed
    embed = discord.Embed(
        color=discord.Color.blue(),
        description=description,
        timestamp=discord.utils.utcnow(),
        footer=discord.EmbedFooter(
            text="Data from Merriam-Webster",
            icon_url=ICON,
        ),
    )

    # add etymology field
    if "et" in entry:
        et_text = "\n".join(item[1] for item in entry["et"] if item[0] == "text")
        embed.add_field(
            name="Etymology",
            value=processed(et_text),
            inline=False,
        )

    # add first known use field
    if "date" in entry:
        embed.add_field(
            name="First Known Use",
            value=processed(entry["date"]),
            inline=False,
        )

    return Page(content=processed("\n".join(lines)), embeds=[embed])


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
            logger.warning(
                f"Daily request limit reached for collegiate dictionary. {self.mw_collegiate_counter = }"
            )
            await ctx.respond("Daily request limit reached for collegiate dictionary.")
            return
        self.mw_collegiate_counter += 1
        response = await self.mw_collegiate.fetch(query)
        await self.handle_response(ctx, query, response)

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
        await self.handle_response(ctx, query, response)

    async def handle_response(self, ctx, query, response):
        if not response:
            await ctx.respond(
                embed=discord.Embed(
                    description=f"No definitions found for {query}.",
                    color=discord.Color.red(),
                )
            )
            return

        if isinstance(response[0], str):
            suggestions = ", ".join(response)
            await ctx.respond(
                embed=discord.Embed(
                    description=f"No exact match found for {query}. *Did you mean: {suggestions}?*",
                    color=discord.Color.red(),
                )
            )
            return

        pages = [extract_page_from_entry(entry) for entry in response]
        paginator = Paginator(pages)
        await paginator.respond(ctx.interaction)

    @tasks.loop(hours=24)
    async def reset_counters(self):
        self.mw_collegiate_counter = 0
        self.mw_medical_counter = 0


def setup(bot):
    bot.add_cog(Words(bot))
