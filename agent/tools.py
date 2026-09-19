"""Инструменты для работы с C#-проектом."""
import subprocess
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 60) -> tuple[int, str, str]:
    """Запускает команду, возвращает (код, stdout, stderr)."""

    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        )
    
        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired as e:
        return -1, e.stdout or "", f"Таймаут {timeout}с: команда зависла"    

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

from pathlib import Path


def _safe_resolve(root: Path, rel: str) -> Path:
    """Гарантирует, что путь внутри project_root."""
    resolved = (root / rel).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Путь {rel} вне проекта")
    return resolved


def read_file(root: Path, rel_path: str) -> str:
    path = _safe_resolve(root, rel_path)
    if not path.exists():
        return f"ОШИБКА: файл {rel_path} не найден"
    return path.read_text(encoding="utf-8")


def write_file(root: Path, rel_path: str, content: str) -> str:
    path = _safe_resolve(root, rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Записано: {rel_path} ({len(content)} символов)"


def list_project_files(root: Path, pattern: str = "**/*.cs") -> str:
    """Список .cs файлов проекта (без bin/obj)."""
    files = [
        str(p.relative_to(root))
        for p in root.glob(pattern)
        if "bin" not in p.parts and "obj" not in p.parts
    ]
    return "\n".join(sorted(files)) if files else "(нет .cs файлов)"