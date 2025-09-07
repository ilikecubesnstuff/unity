import re

import aiohttp


class MerWebWrapper:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key

    async def fetch(self, word: str):
        url = f"{self.base_url}/{word}"
        if self.api_key:
            url += f"?key={self.api_key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error fetching data: {response.status}")
                return await response.json()


def mw_dict_link(hw: str) -> str:
    return f"https://www.merriam-webster.com/dictionary/{hw.replace(' ', '%20')}"


def processed(text: str) -> str:
    # following https://dictionaryapi.com/products/json
    text = re.sub(r"\{b\}(.*?)\{/b\}", lambda m: "**" + m.group(1) + "**", text)
    text = re.sub(r"\{bc\}", ": ", text)
    text = re.sub(r"\{inf\}(.*?)\{/inf\}", lambda m: m.group(1), text)
    text = re.sub(r"\{it\}(.*?)\{/it\}", lambda m: "*" + m.group(1) + "*", text)
    text = re.sub(r"\{ldquo\}", "“", text)
    text = re.sub(r"\{rdquo\}", "”", text)
    text = re.sub(r"\{sc\}(.*?)\{/sc\}", lambda m: m.group(1).upper(), text)
    text = re.sub(r"\{sup\}(.*?)\{/sup\}", lambda m: m.group(1), text)

    text = re.sub(r"\{gloss\}(.*?)\{/gloss\}", lambda m: "[" + m.group(1) + "]", text)
    text = re.sub(
        r"\{parahw\}(.*?)\{/parahw\}",
        lambda m: "\n**" + m.group(1).upper() + "**",
        text,
    )
    text = re.sub(
        r"\{phrase\}(.*?)\{/phrase\}", lambda m: "***" + m.group(1) + "***", text
    )
    text = re.sub(r"\{qword\}(.*?)\{/qword\}", lambda m: "*" + m.group(1) + "*", text)
    text = re.sub(r"\{wi\}(.*?)\{/wi\}", lambda m: "*" + m.group(1) + "*", text)

    text = re.sub(r"\{dx\}(.*?)\{/dx\}", lambda m: "—" + m.group(1), text)
    text = re.sub(r"\{dx_def\}(.*?)\{/dx_def\}", lambda m: "—" + m.group(1), text)
    text = re.sub(r"\{dx_ety\}(.*?)\{/dx_ety\}", lambda m: "—" + m.group(1), text)
    text = re.sub(r"\{ma\}(.*?)\{/ma\}", lambda m: "—more at " + m.group(1), text)

    text = re.sub(
        r"\{a_link\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(
        r"\{d_link\|(.*?)\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(
        r"\{i_link\|(.*?)\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(
        r"\{d_link\|(.*?)\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(
        r"\{mat\|(.*?)\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(
        r"\{sx\|(.*?)\|(.*?)\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(
        r"\{dxt\|(.*?):(.*?)\|(.*?)\|(.*?)\}",
        lambda m: f"[{m.group(1)}]({mw_dict_link(m.group(1))})",
        text,
    )
    text = re.sub(r"\{ds\|(.*?):(.*?)\|(.*?)\|(.*?)\}", "", text)

    return text
