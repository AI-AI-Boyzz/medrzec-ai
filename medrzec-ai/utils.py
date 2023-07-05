import re

from httpx import AsyncClient

CODEPOINT_RE = re.compile(r"\/unicode\/(?P<codepoints>[\da-f-]+)\.png", re.ASCII)


class EmojiReplacer:
    def __init__(self) -> None:
        self.emojis: dict[str, str] = {}

    async def load_emojis(self, client: AsyncClient) -> None:
        response = await client.get("https://api.github.com/emojis")
        json: dict[str, str] = response.json()

        for name, url in json.items():
            if match := next(CODEPOINT_RE.finditer(url), None):
                codepoints = match["codepoints"].split("-")
                emoji = "".join(chr(int(codepoint, 16)) for codepoint in codepoints)
                self.emojis[f":{name}:"] = emoji

        print(f"Loaded {len(self.emojis)}/{len(json)} emoji replacements")

    def replace_emojis(self, text: str) -> str:
        for name, emoji in self.emojis.items():
            text = text.replace(name, emoji)

        return text
