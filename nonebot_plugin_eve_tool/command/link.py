from typing import Optional

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Event, MessageSegment, MessageEvent
from nonebot.internal.params import Depends

from ..database.redis.search import RA
from ..utils.speed_limit import get_url

link = on_command(
    "link",
    aliases={"链接"}
)


def reply_message_id(event: MessageEvent) -> Optional[int]:
    message_id = None
    for seg in event.original_message:
        if seg.type == "reply":
            message_id = int(seg.data["id"])
            break
    return message_id


@link.handle()
async def link_handle(
        event: Event,
        reply_msg_id: Optional[int] = Depends(reply_message_id)
):
    url = await get_url(
        RA,
        event.group_id if event.group_id else event.user_id,
        reply_msg_id
    )
    if url:
        await link.finish(
            MessageSegment.reply(reply_msg_id) + MessageSegment.text(url)
        )
    else:
        await link.finish(MessageSegment.reply(reply_msg_id) + MessageSegment.text("未找到符合的link"))
