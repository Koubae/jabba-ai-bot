from src.bot.domain.chat_bot import ChatBot
from src.bot.domain.dto import ChatBotReply


class ChatBotTestingsMock(ChatBot):
    _model: str = "testings-mock"

    def chat(self, prompt: str, context: list[dict]) -> ChatBotReply:
        # Fake work AI work
        _ = context  # ignore
        reply = prompt[::-1]
        new_context = context + [{"role": "assistant", "content": reply}]
        return {"reply": reply, "context": new_context}
