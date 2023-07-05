import re

from httpx import AsyncClient
from enum import Enum, auto

CODEPOINT_RE = re.compile(r"\/unicode\/(?P<codepoints>[\da-f-]+)\.png", re.ASCII)

PLAYBOOK_URL = "https://remotehow.notion.site/Remote-Work-Playbook-Template-b537fb9b503f4a0a9296774d464777d6"
PLAYBOOK_UPSELL = (
    "Get access to the world’s best playbook on #remotework, and improve your score."
)


class TextFormat(Enum):
    MARKDOWN = auto()
    SLACK = auto()


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


def remote_work_score_message(score: int, text_format: TextFormat) -> str:
    match text_format:
        case TextFormat.MARKDOWN:
            bold = "**"
            paragraph = "\n\n"
            playbook = f"[{PLAYBOOK_UPSELL}]({PLAYBOOK_URL})"
        case TextFormat.SLACK:
            bold = "*"
            paragraph = "\n"
            playbook = f"<{PLAYBOOK_URL}|{PLAYBOOK_UPSELL}>"

    playbook += f"{paragraph}Let’s dive in 🚀"

    message = f"{bold}Your Remote Work Score is {score}%!{bold} "

    if score > 90:
        message += """🧠
You are a REMOTE PRO — super well done! ⭐⭐⭐ Keep rocking!"""

    elif score > 50:
        message += f"""👏👏👏
You are familiar with remote work but need more guidance to feel fully comfortable in it. Let us help you! 🏗️
{playbook}"""

    else:
        message += f"""😅
You need more assistance with remote work to feel fully comfortable in it. Let us help you! 🏗️
{playbook}"""
    return message.replace("\n", paragraph)
