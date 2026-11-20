from pathlib import Path

from config import SCAN_EXCLUDE_BINARY_EXT, SCAN_EXCLUDE_DIRS, SCAN_EXCLUDE_FILES


def is_excluded_dir(path: Path) -> bool:
    return path.name in SCAN_EXCLUDE_DIRS


def is_excluded_file(path: Path) -> bool:
    if path.name in SCAN_EXCLUDE_FILES:
        return True
    return path.suffix.lower() in SCAN_EXCLUDE_BINARY_EXT


def is_binary_file(path: Path) -> bool:
    return path.suffix.lower() in SCAN_EXCLUDE_BINARY_EXT
