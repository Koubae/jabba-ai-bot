import typing as t


class IWebSocket(t.Protocol):

    async def accept(
        self,
        subprotocol: str | None = None,
        headers: t.Iterable[tuple[bytes, bytes]] | None = None,
    ) -> None: ...

    async def receive_text(self) -> str: ...

    async def send_text(self, data: str) -> None: ...
