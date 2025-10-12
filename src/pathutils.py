from pathlib import Path


def path_to_str(path: Path) -> str:
    if path is None:
        return None
    return path.absolute().as_posix()
