from src.bot.domain.ai_bot import AIBot
from src.bot.domain.dto import BotReply


class AIBotTestingsMock(AIBot):
    _model: str = "testings-mock"

    def chat(self, prompt: str, context: list[dict]) -> BotReply:
        # Fake work AI work
        _ = context  # ignore
        reply = prompt[::-1]
        new_context = context + [{"role": "assistant", "content": reply}]
        return {"reply": reply, "context": new_context}
