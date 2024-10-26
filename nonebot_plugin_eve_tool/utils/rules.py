from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent


async def group_increase_notice(event: GroupIncreaseNoticeEvent):
    return isinstance(event, GroupIncreaseNoticeEvent)


async def group_decrease_notice(event: GroupDecreaseNoticeEvent):
    return isinstance(event, GroupDecreaseNoticeEvent)

