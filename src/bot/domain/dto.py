import typing as t


class ChatBotReply(t.TypedDict):
    reply: str
    context: list[dict]
