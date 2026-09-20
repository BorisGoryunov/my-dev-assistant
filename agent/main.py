"""Точка входа: агент, который сам правит код."""
import json
import re
from pathlib import Path
from agent.llm import chat, new_conversation
from agent.project_creator import create_project
from agent.context import Session
from agent.tools import read_file, write_file, list_project_files


AGENT_PROMPT_TEMPLATE = """Ты — C#/.NET разработчик, работающий с проектом.

Корень проекта: {root}

Файлы проекта:
{files}

Ты возвращаешь ТОЛЬКО JSON, без markdown-обёртки, без пояснений вокруг.

Формат:
{{
  "action": "write" | "read" | "answer",
  "path": "относительный путь (для write/read)",
  "content": "полное содержимое файла (для write)",
  "message": "краткое объяснение (для answer)"
}}

Правила:
- Если нужно изменить файл — "action": "write" с ПОЛНЫМ новым содержимым.
- Если нужно посмотреть файл, которого нет в списке — "action": "read".
- Если это просто вопрос — "action": "answer".
- НИКОГДА не оборачивай JSON в ```json или ```.
- Пути — относительные, без C:\\.
"""


def extract_json(text: str) -> dict | None:
    """Достаёт JSON из ответа модели, даже если он что-то добавил вокруг."""
    text = text.strip()

    # убрать markdown-обёртку
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # попробовать напрямую
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # найти первый { ... } блок
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def main():
    print("C# Dev Assistant (autonomous).")
    print("Команды: /open <path>, /close, /files, /new-project <path> | <задача>, /clear, /exit")

    session = Session()
    history = new_conversation()

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПока!")
            break

        if not user_input:
            continue

        # --- служебные команды ---
        if user_input == "/exit":
            break

        if user_input == "/clear":
            history = new_conversation()
            print("История очищена.")
            continue

        if user_input == "/close":
            session.close()
            continue

        if user_input.startswith("/open "):
            print("OPEN")
            path = Path(user_input[len("/open "):].strip())
            try:
                session.open(path)
                print("Файлы проекта:")
                print(list_project_files(session.project_root))
            except Exception as e:
                print(f"Ошибка: {e}")
            continue

        if user_input == "/files":
            if not session.is_open:
                print("Проект не открыт.")
                continue
            print(list_project_files(session.project_root))
            continue
        
        if user_input.startswith("/new-project "):
            rest = user_input[len("/new-project "):]
            if "|" not in rest:
                print("Формат: /new-project <path> | <задача>")
                continue
            path_str, task = rest.split("|", 1)
            project_path = Path(path_str.strip())
            create_project(project_path, task.strip())
            session.open(project_path)
            continue

        # --- агентный запрос ---
        if not session.is_open:
            print("Проект не открыт. Используй /open или /new-project")
            continue

        files = list_project_files(session.project_root)

        # Если в запросе упоминается файл — подгружаем его содержимое
        file_contents = ""
        for fname in files.splitlines():
            short = fname.split("/")[-1]
            if short.lower() in user_input.lower() or short.lower().replace(".cs", "") in user_input.lower():
                file_contents += f"\n--- {fname} ---\n{read_file(session.project_root, fname)}\n--- /{fname} ---\n"

        system_msg = AGENT_PROMPT_TEMPLATE.format(
            root=session.project_root,
            files=files + file_contents,
        )

        messages = [
            {"role": "system", "content": system_msg},
            *history[-6:],   # последние 3 обмена для контекста диалога
            {"role": "user", "content": user_input},
        ]

        print("\n[думаю...]")
        raw = chat(messages)
        parsed = extract_json(raw)

        if not parsed:
            print("⚠ Модель вернула не-JSON. Сырой ответ (первые 300 символов):")
            print(raw[:300])
            continue

        action = parsed.get("action")
        msg = parsed.get("message", "")

        if action == "answer":
            print(f"\n{msg}")
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": msg})

        elif action == "read":
            rel = parsed.get("path")
            content = read_file(session.project_root, rel)
            print(f"\n--- {rel} ---")
            print(content)
            print(f"--- /{rel} ---")

        elif action == "write":
            rel = parsed.get("path")
            content = parsed.get("content", "")
            try:
                result = write_file(session.project_root, rel, content)
                print(f"\n✏ {result}")
                if msg:
                    print(f"  {msg}")
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": msg or f"Записал {rel}"})
            except Exception as e:
                print(f"Ошибка записи: {e}")

        else:
            print(f"⚠ Неизвестное действие: {action}")


if __name__ == "__main__":
    main()