"""Создание C# проекта с помощью модели."""
import re
from pathlib import Path
from agent.llm import chat, new_conversation
from agent.tools import create_console_project, build, run


# CREATE_PROMPT = """Ты — C# разработчик. Тебе дали задачу создать консольное приложение.
# Верни ТОЛЬКО содержимое файла Program.cs, без объяснений, без markdown-обёртки ```csharp.
# Если нужны другие файлы — не создавай их, всё в одном Program.cs.
# Код должен быть компилируемым на .NET 10.
# """

CREATE_PROMPT = """Ты — C# разработчик. Верни ТОЛЬКО код файла Program.cs.

ЖЁСТКИЕ ПРАВИЛА:
- Первая строка ответа должна начинаться с "using" или "//".
- НЕ используй markdown-обёртки ```csharp или ```.
- НЕ добавляй пояснений до или после кода.
- НЕ пиши "Вот код:" или "Конечно!".

Пример ПРАВИЛЬНОГО ответа:
using System;

class Program
{
    static void Main()
    {
        Console.WriteLine("Hello");
    }
}

Пример НЕПРАВИЛЬНОГО ответа (так делать нельзя):
```csharp
using System;
...
Теперь напиши код для этой задачи:"""


def create_project(project_path: Path, task: str) -> None:
    print(f"[1/4] Создаю проект в {project_path}...")
    result = create_console_project(project_path)
    print(result)

    print(f"[2/4] Прошу модель написать код...")
    messages = [
        {"role": "system", "content": CREATE_PROMPT},
        {"role": "user", "content": task},
    ]
    code = chat(messages)
    code = strip_markdown_fence(code)
    program_cs = project_path / "Program.cs"
    program_cs.write_text(code, encoding="utf-8")
    print(f"Program.cs записан ({len(code)} символов)")

    print(f"[3/4] Собираю проект...")
    build_result = build(project_path)
    print(build_result)

    if "exit=0" in build_result:
        print(f"[4/4] Запускаю...")
        run_result = run(project_path)
        print(run_result)
    else:
        print("Сборка упала — запуск пропущен.")

def strip_markdown_fence(text: str) -> str:
    """Убирает ```csharp ... ``` или ``` ... ``` из ответа модели."""
    text = text.strip()

    # Случай 1: обёртка с языком: ```csharp ... ```
    match = re.search(r"```(?:csharp|cs)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Случай 2: только открывающие/закрывающие бэктики
    lines = text.splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()        