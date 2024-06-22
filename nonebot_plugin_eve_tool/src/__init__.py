from ..model import plugin_path, data_path, KillMailDetails
from ..utils.zkb import CharacterInfo

import aiofiles


templates_path = plugin_path / 'src' / 'templates'


with open(templates_path / "kb_info.html", "r", encoding="utf-8") as file:
    template_kb_info = file.read()

with open(templates_path / "killmail.html", "r", encoding="utf-8") as file:
    template_killmail = file.read()

with open(templates_path / "killmail.css", "r", encoding="utf-8") as file:
    template_killmail_css = file.read()


async def use_kb_info_html(char_info: CharacterInfo) -> str:
    return template_kb_info.format(**vars(char_info))


async def save_html_to_file(html_content: str, file_path: str):
    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(html_content)


async def use_killmail_html(kill_mail_details: KillMailDetails) -> str:
    kill_mail_details.css = template_killmail_css
    path_out = data_path / "KillMailHtml" / f"{kill_mail_details.kill_mail_id}.html"

    await save_html_to_file(template_killmail.format(**vars(kill_mail_details)), path_out)
    return template_killmail.format(**vars(kill_mail_details))


