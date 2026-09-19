"""Точка входа: чат + команды."""
import argparse
from pathlib import Path
from agent.llm import chat, new_conversation
from agent.project_creator import create_project


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, help="Путь к C# проекту")
    args = parser.parse_args()

    print("C# Dev Assistant. /clear, /exit, /new-project <path> | <задача>")
    history = new_conversation()

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПока!")
            break

        if not user_input:
            continue
        
        if user_input == "/exit":
            break

        if user_input == "/clear":
            history = new_conversation()
            print("История очищена.")
            continue

        if user_input.startswith("/new-project "):
            rest = user_input[len("/new-project "):]
            if "|" not in rest:
                print("Формат: /new-project C:/projects/X | задача")
                continue
            path_str, task = rest.split("|", 1)
            create_project(Path(path_str.strip()), task.strip())
            continue

        history.append({"role": "user", "content": user_input})
        print("\n[думаю...]")
        answer = chat(history)
        history.append({"role": "assistant", "content": answer})
        print(f"\n{answer}")


if __name__ == "__main__":
    main()