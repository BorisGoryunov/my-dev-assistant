"""Обёртка над Ollama для локальной модели."""
import ollama

MODEL = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """Ты — опытный C#/.NET разработчик. Пишешь чистый, идиоматичный код.
Следуешь SOLID, используешь async/await где уместно, пишешь XML-документацию.
Отвечаешь на русском, код — на C#. Если не уверен — говори честно."""


def chat(messages: list[dict]) -> str:
    """Отправляет историю сообщений в модель, возвращает ответ."""
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        options={
            "temperature": 0.2,     # ниже — стабильнее код
            "num_ctx": 8192,        # контекст 8k, влезает в память
        },
    )
    return response.message.content


def new_conversation() -> list[dict]:
    """Создаёт новую историю с системным промптом."""
    return [{"role": "system", "content": SYSTEM_PROMPT}]