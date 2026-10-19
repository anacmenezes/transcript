
from pathlib import Path


def garantir_diretorio(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def remover_arquivo(path: Path) -> None:
    if path.is_file():
        path.unlink(missing_ok=True)
