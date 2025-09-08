import re

import aiohttp

ICON = "https://dictionaryapi.com/images/info/branding-guidelines/MWLogo_DarkBG_120x120_2x.png"


class MerWebWrapper:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key

    async def fetch(self, word: str):
        url = f"{self.base_url}/{word.replace(' ', '%20')}"
        if self.api_key:
            url += f"?key={self.api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error fetching data: {response.status}")
                return await response.json()


def mw_dict_link(hw: str) -> str:
    return (
        f"[{hw}](https://www.merriam-webster.com/dictionary/{hw.replace(' ', '%20')})"
    )


# following https://dictionaryapi.com/products/json
processing_map = {
    # formatting and punctuation
    r"\{b\}(.*?)\{/b\}": lambda m: "**" + m.group(1) + "**",  # bold
    r"\{bc\}": lambda m: ": ",  # bold colon
    r"\{inf\}(.*?)\{/inf\}": lambda m: m.group(1),  # inflection
    r"\{it\}(.*?)\{/it\}": lambda m: "*" + m.group(1) + "*",  # italics
    r"\{ldquo\}": lambda m: "“",  # left double quote
    r"\{rdquo\}": lambda m: "”",  # right double quote
    r"\{sc\}(.*?)\{/sc\}": lambda m: m.group(1).upper(),  # small caps
    r"\{sup\}(.*?)\{/sup\}": lambda m: m.group(1),  # superscript
    # word-marking and gloss
    r"\{gloss\}(.*?)\{/gloss\}": lambda m: "[" + m.group(1) + "]",  # gloss
    r"\{parahw\}(.*?)\{/parahw\}": lambda m: "**" + m.group(1).upper() + "**",  # headword instance in paragraph
    r"\{phrase\}(.*?)\{/phrase\}": lambda m: "***" + m.group(1) + "***",  # phrase
    r"\{qword\}(.*?)\{/qword\}": lambda m: "*" + m.group(1) + "*",  # headword instance in quote
    r"\{wi\}(.*?)\{/wi\}": lambda m: "*" + m.group(1) + "*",  # headword instance in running text
    # cross-reference grouping
    r"\{dx\}(.*?)\{/dx\}": lambda m: "—" + m.group(1),  # introductory text
    r"\{dx_def\}(.*?)\{/dx_def\}": lambda m: "—" + m.group(1),  # parenthetical xref with introductory text
    r"\{dx_ety\}(.*?)\{/dx_ety\}": lambda m: "—" + m.group(1),  # directional xref within etymology
    r"\{ma\}(.*?)\{/ma\}": lambda m: "—more at " + m.group(1),  # more at
    # cross-reference links
    r"\{a_link\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # auto link
    r"\{d_link\|(.*?)\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # direct link
    r"\{i_link\|(.*?)\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # italicized link
    r"\{et_link\|(.*?)\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # etymology link
    r"\{mat\|(.*?)\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # more at target
    r"\{sx\|(.*?)\|(.*?)\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # synonymous xref
    r"\{dxt\|(.*?):(.*?)\|(.*?)\|(.*?)\}": lambda m: mw_dict_link(m.group(1)),  # directional xref target
    # date sense
    r"\{ds\|(.*?)\|(.*?)\|(.*?)\}": lambda m: "",  # date sense
}


def processed(text: str) -> str:
    if not text:
        return text

    # Apply all regex substitutions in the processing_map
    for pattern, repl in processing_map.items():
        text = re.sub(pattern, repl, text)

    return text
