from ollama import ChatResponse, chat

from src.bot.domain.chat_bot import ChatBot
from src.bot.domain.dto import ChatBotReply


class ChatBotOllama(ChatBot):
    _model: str = "ollama-abstract"

    def chat(self, prompt: str, context: list[dict]) -> ChatBotReply:
        context.append({"role": "user", "content": prompt})
        response: ChatResponse = chat(model=self._model, messages=context)
        reply = response["message"]["content"]

        new_context = context + [{"role": "assistant", "content": reply}]
        return {"reply": reply, "context": new_context}


class ChatBotOllamaOpenAI(ChatBotOllama):
    _model: str = "openchat"


class ChatBotOllamaNeuralChat(ChatBotOllama):
    _model: str = "neural-chat"
