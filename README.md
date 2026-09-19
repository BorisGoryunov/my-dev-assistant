# my-dev-assistant

Расширения VS Code:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- C# Dev Kit (ms-dotnettools.csdevkit)

python -m venv .venv
. .venv/Scripts/activate
which python
pip install ollama langchain chromadb sentence-transformers

dotnet --version
python --version
ollama --version

Для деактивации:
deactivate

pip install --upgrade pip
pip install ollama

pip freeze > requirements.txt

скачать
ollama pull qwen2.5-coder:7b
ollama show qwen2.5-coder:7b
ollama list
ollama run qwen2.5-coder:7b "напиши C# функцию для сложения двух чисел"
ollama run qwen2.5-coder:7b --verbose "напиши C# функцию для сложения двух чисел"
Выйти из интерактивного режима: /bye.

Проверь связку Python → Ollama:
python -c "import ollama; print([m.model for m in ollama.list()['models']])"

> удалить модель:
ollama rm qwen2.5-coder:7b
ollama rm qwen2.5-coder:14b
ollama rm dotnet-coder

mkdir -p agent workspace index
touch agent/__init__.py agent/llm.py agent/main.py


python -m agent.main
> Напиши record User с Id, Name, Email и методом валидации

python -m agent.main
> /new-project C:/projects/HelloAgent | программа, которая спрашивает имя у пользователя и здоровается

> /open C:/projects/HelloAgent

ollama pull qwen2.5-coder:14b
ollama run qwen2.5-coder:14b --verbose "напиши класс на C#"

