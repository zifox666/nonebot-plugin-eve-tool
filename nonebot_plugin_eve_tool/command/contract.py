
from nonebot import on_regex, on_command
from nonebot.adapters.onebot.v11 import Event, MessageSegment, Message
from nonebot.params import RegexStr, CommandArg

from ..utils.common import type_word
from ..api import Appraisal
from ..utils.png import html2pic_element


janice_matcher = on_regex(r"https://janice\.e-351\.com/a/([a-zA-Z0-9]{6})")
janice_appraisal = on_command("janice", aliases={"合同估价"}, priority=5)


@janice_matcher.handle()
async def _(
    event: Event,
    url: str = RegexStr()
):
    pic = await html2pic_element(
        url=url,
        element=".appraisal"
    )
    if pic:
        await janice_matcher.finish(
            MessageSegment.reply(event.message_id) + MessageSegment.image(pic)
        )


@janice_appraisal.handle()
async def _(args: Message = CommandArg()):
    appraisal = Appraisal(
        contract=await type_word(str(args)),
        persist=True
    )
    await appraisal.load_data()
    msg = f'''估价地址：{appraisal.janiceUrl}
合同体积：{appraisal.totalVolume} m3
合同卖单：{appraisal.totalSellPrice:,.2f} isk
合同买单：{appraisal.totalBuyPrice:,.2f} isk
中间价：{appraisal.totalSplitPrice:,.2f} isk'''
    message_id = await janice_appraisal.send(
            MessageSegment.text(msg)
        )
    try:
        pic = await html2pic_element(
            url=appraisal.janiceUrl,
            element=".appraisal"
        )
        await janice_appraisal.send(
            MessageSegment.reply(message_id.get('message_id', 0)) + MessageSegment.image(pic)
        )
    except Exception as e:
        await janice_appraisal.send(f"渲染图片出错\n{e}")


