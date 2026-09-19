"""Контекст сессии: какой проект сейчас открыт."""
from pathlib import Path


class Session:
    def __init__(self):
        self.project_root: Path | None = None

    def open(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Проект не найден: {path}")
        self.project_root = path.resolve()
        print(f"📂 Открыт проект: {self.project_root}")

    def close(self) -> None:
        self.project_root = None
        print("📁 Проект закрыт")

    @property
    def is_open(self) -> bool:
        return self.project_root is not None