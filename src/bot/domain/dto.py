import typing as t


class BotReply(t.TypedDict):
    reply: str
    context: list[dict]
