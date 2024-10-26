from nonebot import require
from PIL import Image
from io import BytesIO

from ..model import plugin_path

from nonebot import require

require("nonebot_plugin_htmlrender")

from nonebot_plugin_htmlrender import (
    text_to_pic,
    md_to_pic,
    template_to_pic,
    get_new_page,
)

templates_path = plugin_path / 'src' / 'templates' / 'kb_info'
help_templates_path = plugin_path / 'src' / 'help_html'


async def md2pic(content):
    return await md_to_pic(md=content)


async def html2pic(html_content: str, width: int = 700, height: int = 400) -> str:
    async with get_new_page(viewport={"width": width, "height": height}, device_scale_factor=2) as page:
        await page.set_content(html_content)
        pic = await page.screenshot(full_page=True, path="./html2pic.png")
    return pic


async def html2pic_element(html_content: str = None, url: str = None, element: str = None) -> bytes:
    async with get_new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1) as page:
        if url:
            await page.goto(url)
        else:
            await page.set_content(html_content)

        element_handle = await page.wait_for_selector(element)
        if element_handle is None:
            raise ValueError(f"Element '{element}' not found on the page.")

        bounding_box = await element_handle.bounding_box()
        element_width = bounding_box['width']
        element_height = bounding_box['height']
        viewport_height = 1080

        screenshots = []
        for offset in range(0, int(element_height), viewport_height):
            # Scroll to the part of the element we want to capture
            await page.evaluate(f"window.scrollTo(0, {offset})")
            await page.wait_for_timeout(500)  # Ensure the scroll action has been completed
            screenshot = await page.screenshot(
                clip={
                    "x": bounding_box['x'],
                    "y": bounding_box['y'] - offset if bounding_box['y'] > offset else 0,
                    "width": element_width,
                    "height": min(viewport_height, element_height - offset)
                }
            )
            screenshots.append(screenshot)

        # 拼接截图
        stitched_image = Image.new('RGB', (int(element_width), int(element_height)))
        current_height = 0
        for screenshot in screenshots:
            img = Image.open(BytesIO(screenshot))
            stitched_image.paste(img, (0, current_height))
            current_height += img.height

        # 保存图片
        stitched_image.save("./html2pic.png")
        with BytesIO() as output:
            stitched_image.save(output, format="PNG")
            return output.getvalue()


async def render(char_json) -> bytes:

    return await template_to_pic(
        template_path=str(templates_path),
        template_name="profile.html",
        templates=char_json,
        pages={
            "viewport": {"width": 550, "height": 10},
            "base_url": f"file://{templates_path}",
        },
    )


async def render_help(_json) -> bytes:

    return await template_to_pic(
        template_path=str(help_templates_path),
        template_name="help.html",
        templates=_json,
        pages={
            "viewport": {"width": 790, "height": 10},
            "base_url": f"file://{templates_path}",
        },
    )
