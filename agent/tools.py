"""Инструменты для работы с C#-проектом."""
import subprocess
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Запускает команду, возвращает (код, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr


def create_console_project(project_path: Path) -> str:
    """Создаёт новый консольный проект через dotnet new."""
    project_path.parent.mkdir(parents=True, exist_ok=True)
    code, out, err = run_cmd(
        ["dotnet", "new", "console", "-o", str(project_path)],
        cwd=project_path.parent,
    )
    if code != 0:
        return f"ОШИБКА создания проекта:\n{err}"
    return f"Проект создан: {project_path}\n{out}"


def build(project_path: Path) -> str:
    """Запускает dotnet build."""
    code, out, err = run_cmd(["dotnet", "build"], cwd=project_path)
    return f"exit={code}\n{out}\n{err}"


def run(project_path: Path) -> str:
    """Запускает dotnet run."""
    code, out, err = run_cmd(["dotnet", "run"], cwd=project_path)
    return f"exit={code}\n{out}\n{err}"