import subprocess
from pathlib import Path
from typing import List, Union


def list_files(directory: Union[str, Path]) -> List[str]:
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    files = [str(f) for f in dir_path.iterdir() if f.is_file()]
    return sorted(files)


def read_file(file_path: Union[str, Path]) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text()


def write_file(file_path: Union[str, Path], content: str) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def run_shell_command(command: str, timeout: int = 20) -> str:
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout or result.stderr
