from ollama import ChatResponse, chat

from src.bot.domain.ai_bot import AIBot
from src.bot.domain.dto import BotReply


class AIBotOllama(AIBot):
    _model: str = "ollama-abstract"

    def chat(self, prompt: str, context: list[dict]) -> BotReply:
        context.append({"role": "user", "content": prompt})
        response: ChatResponse = chat(model=self._model, messages=context)
        reply = response["message"]["content"]

        new_context = context + [{"role": "assistant", "content": reply}]
        return {"reply": reply, "context": new_context}


class AIBotOllamaOpenAI(AIBotOllama):
    _model: str = "openchat"


class AIBotOllamaNeuralChat(AIBotOllama):
    _model: str = "neural-chat"
